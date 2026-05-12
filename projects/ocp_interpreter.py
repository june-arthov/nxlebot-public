#!/usr/bin/env python3
"""
OC+ (Octane Command Pipeline) Interpreter v2.0
Full implementation: recursive-descent parser, AST, and executor.

Supports:
  set VAR = "value"         # string literal
  set VAR = 42               # number
  set VAR = $A + $B * 2      # math expression (+, -, *, /, %, parentheses)
  run "shell $VAR"
  echo "message $VAR"
  cd /path
  parallel { ... } { ... }
  try { ... } catch { ... }
  if $VAR == "val" { ... } [else { ... }]
  for item in ["a","b","c"] { ... }
  for i in [1..10] { ... }
  while $VAR < 10 { ... }
"""

import sys
import os
import subprocess
import shlex
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# ── errors ──────────────────────────────────────────────────────────────

class OCPError(Exception):
    def __init__(self, msg: str, line: int = 0):
        super().__init__(msg)
        self.line = line


# ── AST nodes ───────────────────────────────────────────────────────────

class Node:
    line: int = 0


@dataclass
class Block(Node):
    stmts: list[Node] = field(default_factory=list)
    line: int = 0


@dataclass
class Set(Node):
    var: str
    value: str               # string literal (legacy mode)
    expr: Optional["ExprNode"] = None  # expression mode


# ── expression AST ──────────────────────────────────────────────────────

class ExprNode:
    """Base class for expression nodes."""
    pass


@dataclass
class IntLit(ExprNode):
    val: int


@dataclass
class VarRef(ExprNode):
    name: str


@dataclass
class BinOp(ExprNode):
    left: ExprNode
    op: str   # '+', '-', '*', '/', '%'
    right: ExprNode


# ── statements ──────────────────────────────────────────────────────────


@dataclass
class Run(Node):
    cmd: str


@dataclass
class Echo(Node):
    msg: str


@dataclass
class Cd(Node):
    path: str


@dataclass
class Parallel(Node):
    blocks: list[Block] = field(default_factory=list)


@dataclass
class TryCatch(Node):
    try_block: Block = field(default_factory=Block)
    catch_block: Block = field(default_factory=Block)


@dataclass
class IfElse(Node):
    cond: "Condition"
    then_block: Block = field(default_factory=Block)
    else_block: Optional[Block] = None


@dataclass
class ForRange(Node):
    var: str
    start: ExprNode   # evaluated at runtime
    end: ExprNode     # evaluated at runtime
    body: Block = field(default_factory=Block)


@dataclass
class ForList(Node):
    var: str
    items: list[str]
    body: Block = field(default_factory=Block)


@dataclass
class While(Node):
    cond: "Condition"
    body: Block = field(default_factory=Block)


# ── conditions ──────────────────────────────────────────────────────────

class CmpOp(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="


@dataclass
class Condition:
    left: str   # "$VAR"
    op: CmpOp
    right: str  # "string" or number


def parse_condition(raw: str) -> Condition:
    """Parse '$VAR == "val"' or '$VAR < 5' into a Condition."""
    m = re.match(r'^\$(\w+)\s*(==|!=|<=|>=|<|>)\s*(.+)$', raw.strip())
    if not m:
        raise OCPError(f"Invalid condition: {raw}")
    var = m.group(1)
    op = CmpOp(m.group(2))
    right = m.group(3).strip().strip('"')
    return Condition(left=var, op=op, right=right)


def eval_condition(cond: Condition, env: dict[str, str]) -> bool:
    left_val = env.get(cond.left, "")
    # Try numeric comparison
    try:
        lf = float(left_val)
        rf = float(cond.right)
    except ValueError:
        lf, rf = None, None

    if cond.op == CmpOp.EQ:
        if lf is not None:
            return lf == rf
        return left_val == cond.right
    elif cond.op == CmpOp.NE:
        if lf is not None:
            return lf != rf
        return left_val != cond.right
    elif cond.op == CmpOp.LT:
        if lf is not None:
            return lf < rf
        raise OCPError(f"Cannot compare strings with '<': {left_val} < {cond.right}")
    elif cond.op == CmpOp.GT:
        if lf is not None:
            return lf > rf
        raise OCPError(f"Cannot compare strings with '>': {left_val} > {cond.right}")
    elif cond.op == CmpOp.LE:
        if lf is not None:
            return lf <= rf
        raise OCPError(f"Cannot compare strings with '<=': {left_val} <= {cond.right}")
    elif cond.op == CmpOp.GE:
        if lf is not None:
            return lf >= rf
        raise OCPError(f"Cannot compare strings with '>=': {left_val} >= {cond.right}")
    return False


# ── tokenizer ───────────────────────────────────────────────────────────

class TokenType(Enum):
    WORD = 1
    STRING = 2
    LBRACE = 3
    RBRACE = 4
    LBRACKET = 5
    RBRACKET = 6
    DOTDOT = 7
    COMMA = 8
    COMMENT = 9
    EOF = 10


@dataclass
class Token:
    type: TokenType
    value: str
    line: int


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    while i < len(text):
        ch = text[i]

        if ch == '\n':
            line += 1
            i += 1
            continue

        if ch.isspace():
            i += 1
            continue

        if ch == '#':
            j = text.find('\n', i)
            if j == -1:
                j = len(text)
            tokens.append(Token(TokenType.COMMENT, text[i:j], line))
            i = j
            continue

        if ch == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                if text[j] == '\\':
                    j += 1
                j += 1
            if j >= len(text):
                raise OCPError("Unterminated string", line)
            tokens.append(Token(TokenType.STRING, text[i+1:j], line))
            i = j + 1
            continue

        if ch == '{':
            tokens.append(Token(TokenType.LBRACE, '{', line))
            i += 1
            continue

        if ch == '}':
            tokens.append(Token(TokenType.RBRACE, '}', line))
            i += 1
            continue

        if ch == '[':
            tokens.append(Token(TokenType.LBRACKET, '[', line))
            i += 1
            continue

        if ch == ']':
            tokens.append(Token(TokenType.RBRACKET, ']', line))
            i += 1
            continue

        if ch == ',':
            tokens.append(Token(TokenType.COMMA, ',', line))
            i += 1
            continue

        # Check for .. (before word detection, so 1..5 splits correctly)
        if ch == '.' and i + 1 < len(text) and text[i + 1] == '.':
            tokens.append(Token(TokenType.DOTDOT, '..', line))
            i += 2
            continue

        # Word: any non-whitespace, non-special char
        j = i
        while j < len(text) and not text[j].isspace() and text[j] not in '"{}[],#.':
            j += 1

        word = text[i:j]
        # Check for comparison ops
        if word in ('==', '!=', '<', '>', '<=', '>='):
            # These get consumed as WORD (will be parsed in condition)
            pass

        tokens.append(Token(TokenType.WORD, word, line))
        i = j

    tokens.append(Token(TokenType.EOF, '', line))
    return tokens


# ── expression parser (string → ExprNode) ───────────────────────────────

def parse_expr_string(raw: str, line: int) -> ExprNode:
    """Parse '42' | '$VAR' | '$A + $B * 2' | '(1 + 2) * 3' into an ExprNode tree."""
    raw = raw.strip()
    if not raw:
        raise OCPError("Empty expression", line)
    lex = _ExprLexer(raw, line)
    parser = _ExprRecursiveDescent(lex)
    expr = parser.parse()
    if lex.peek():
        raise OCPError(f"Unexpected token '{lex.peek()}' in expression", line)
    return expr


class _ExprLexer:
    """Mini lexer for math expressions inside set value."""

    def __init__(self, text: str, line: int):
        self.text = text
        self.line = line
        self.pos = 0

    def _skip_spaces(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def peek(self) -> Optional[str]:
        self._skip_spaces()
        if self.pos >= len(self.text):
            return None
        ch = self.text[self.pos]
        if ch.isdigit():
            j = self.pos
            while j < len(self.text) and self.text[j].isdigit():
                j += 1
            return self.text[self.pos:j]
        if ch in '+-*/%=()':
            return ch
        if ch == '$':
            j = self.pos + 1
            while j < len(self.text) and (self.text[j].isalnum() or self.text[j] == '_'):
                j += 1
            return self.text[self.pos:j]
        raise OCPError(f"Unexpected char '{ch}' in expression", self.line)

    def consume(self) -> Optional[str]:
        t = self.peek()
        if t is None:
            return None
        self.pos += len(t)
        return t

    def has(self) -> bool:
        return self.peek() is not None


class _ExprRecursiveDescent:
    """Pratt-style expression parser: handles precedence correctly."""

    PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2}

    def __init__(self, lex: _ExprLexer):
        self.lex = lex
        self.line = lex.line

    def parse(self, min_prec: int = 0) -> ExprNode:
        left = self._atom()
        while True:
            op = self.lex.peek()
            if op is None or op not in self.PREC:
                break
            prec = self.PREC[op]
            if prec < min_prec:
                break
            self.lex.consume()  # consume op
            right = self.parse(prec + 1)
            left = BinOp(left=left, op=op, right=right)
        return left

    def _atom(self) -> ExprNode:
        t = self.lex.peek()
        if t is None:
            raise OCPError("Unexpected end of expression", self.line)

        if t == '(':
            self.lex.consume()  # (
            expr = self.parse()
            close = self.lex.peek()
            if close != ')':
                raise OCPError("Expected ')'", self.line)
            self.lex.consume()  # )
            return expr

        if t.startswith('$'):
            self.lex.consume()
            return VarRef(name=t[1:])

        if t.isdigit():
            self.lex.consume()
            return IntLit(val=int(t))

        raise OCPError(f"Unexpected token '{t}' in expression", self.line)


def eval_expr(expr: ExprNode, env: dict[str, str]) -> int:
    """Evaluate expression tree to integer."""
    if isinstance(expr, IntLit):
        return expr.val
    elif isinstance(expr, VarRef):
        val = env.get(expr.name, '0')
        try:
            return int(val)
        except ValueError:
            try:
                return int(float(val))
            except ValueError:
                raise OCPError(
                    f"Variable ${expr.name} = '{val}' is not a number")
    elif isinstance(expr, BinOp):
        l = eval_expr(expr.left, env)
        r = eval_expr(expr.right, env)
        if expr.op == '+':
            return l + r
        elif expr.op == '-':
            return l - r
        elif expr.op == '*':
            return l * r
        elif expr.op == '/':
            if r == 0:
                raise OCPError("Division by zero")
            return l // r
        elif expr.op == '%':
            if r == 0:
                raise OCPError("Modulo by zero")
            return l % r
    raise OCPError(f"Unknown expression type: {type(expr).__name__}")


# ▸ token → ExprNode helper (used during parsing for range endpoints etc.)

def _token_to_expr(tok: Token, line: int) -> ExprNode:
    """Convert a token to an ExprNode. Handles digits, $VAR, and raw words."""
    val = tok.value
    if val.isdigit():
        return IntLit(val=int(val))
    if val.startswith('$'):
        return VarRef(name=val[1:])
    # Bare word — treat as int if possible, otherwise error
    try:
        return IntLit(val=int(val))
    except ValueError:
        raise OCPError(f"Expected number or $VAR, got '{val}'", line)


# ── parser ──────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: Optional[TokenType] = None) -> Token:
        t = self.tokens[self.pos]
        if expected_type and t.type != expected_type:
            raise OCPError(
                f"Expected {expected_type.name}, got {t.type.name} '{t.value}'",
                t.line,
            )
        self.pos += 1
        return t

    def parse_program(self) -> Block:
        block = Block(stmts=[], line=1)
        while self.peek().type != TokenType.EOF:
            stmt = self.parse_stmt()
            if stmt is not None:
                block.stmts.append(stmt)
                block.stmts[-1].line = self.peek().line
        return block

    def parse_stmt(self) -> Optional[Node]:
        t = self.peek()
        if t.type == TokenType.COMMENT:
            self.pos += 1
            return self.parse_stmt()
        if t.type == TokenType.RBRACE or t.type == TokenType.EOF:
            return None  # end of block
        if t.type != TokenType.WORD:
            raise OCPError(f"Expected command, got {t.value}", t.line)
        cmd = t.value
        self.pos += 1

        if cmd == 'set':
            return self.parse_set()
        elif cmd == 'run':
            return self.parse_run()
        elif cmd == 'echo':
            return self.parse_echo()
        elif cmd == 'cd':
            return self.parse_cd()
        elif cmd == 'parallel':
            return self.parse_parallel()
        elif cmd == 'try':
            return self.parse_try()
        elif cmd == 'if':
            return self.parse_if()
        elif cmd == 'for':
            return self.parse_for()
        elif cmd == 'while':
            return self.parse_while()
        else:
            raise OCPError(f"Unknown command: {cmd}", t.line)

    def parse_set(self) -> Set:
        line = self.peek().line
        var = self.consume(TokenType.WORD).value
        self.consume(TokenType.WORD)  # =
        t = self.peek()
        if t.type == TokenType.STRING:
            # Legacy mode: string literal
            val = self.consume(TokenType.STRING).value
            return Set(var=var, value=val)
        else:
            # Expression mode: collect tokens until block/EOF/keyword/comment
            KEYWORDS = {
                'set', 'run', 'echo', 'cd', 'parallel', 'try', 'catch',
                'if', 'else', 'for', 'while', 'in',
            }
            raw_parts: list[str] = []
            while True:
                t = self.peek()
                if t.type in (TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF,
                              TokenType.COMMENT):
                    break
                if t.type == TokenType.WORD and t.value in KEYWORDS:
                    break
                raw_parts.append(self.consume().value)
            if not raw_parts:
                raise OCPError("Expected expression after =", line)
            expr = parse_expr_string(' '.join(raw_parts), line)
            node = Set(var=var, value='', expr=expr)
            node.line = line
            return node

    def parse_run(self) -> Run:
        cmd = self.consume(TokenType.STRING).value
        return Run(cmd=cmd)

    def parse_echo(self) -> Echo:
        msg = self.consume(TokenType.STRING).value
        return Echo(msg=msg)

    def parse_cd(self) -> Cd:
        path = self.consume(TokenType.WORD).value
        return Cd(path=path)

    def parse_block(self) -> Block:
        self.consume(TokenType.LBRACE)
        stmts: list[Node] = []
        while self.peek().type != TokenType.RBRACE:
            stmt = self.parse_stmt()
            if stmt is not None:
                stmts.append(stmt)
        self.consume(TokenType.RBRACE)
        return Block(stmts=stmts)

    def parse_parallel(self) -> Parallel:
        blocks: list[Block] = []
        while self.peek().type == TokenType.LBRACE:
            blocks.append(self.parse_block())
        if len(blocks) < 1:
            raise OCPError("parallel requires at least one block",
                           self.peek().line)
        return Parallel(blocks=blocks)

    def parse_try(self) -> TryCatch:
        try_block = self.parse_block()
        self.consume(TokenType.WORD)  # 'catch'
        catch_block = self.parse_block()
        return TryCatch(try_block=try_block, catch_block=catch_block)

    def parse_if(self) -> IfElse:
        # Read the condition: everything until '{'
        cond_parts: list[str] = []
        while self.peek().type != TokenType.LBRACE:
            t = self.peek()
            if t.type == TokenType.STRING:
                cond_parts.append(f'"{t.value}"')
            else:
                cond_parts.append(t.value)
            self.pos += 1
        cond = parse_condition(' '.join(cond_parts))
        then_block = self.parse_block()

        else_block = None
        if self.peek().type == TokenType.WORD and self.peek().value == 'else':
            self.pos += 1
            else_block = self.parse_block()

        return IfElse(cond=cond, then_block=then_block, else_block=else_block)

    def parse_for(self) -> Node:
        var = self.consume(TokenType.WORD).value
        self.consume(TokenType.WORD)  # 'in'
        self.consume(TokenType.LBRACKET)

        # Check if range: [1..10] or [1..$VAR] or [$A..$B]
        first = self.consume()
        if self.peek().type == TokenType.DOTDOT:
            start_expr = _token_to_expr(first, first.line)
            self.consume(TokenType.DOTDOT)
            end_tok = self.consume()
            end_expr = _token_to_expr(end_tok, end_tok.line)
            self.consume(TokenType.RBRACKET)
            body = self.parse_block()
            return ForRange(var=var, start=start_expr, end=end_expr, body=body)

        # List: ["a", "b", "c"]
        items: list[str] = []
        if first.type == TokenType.STRING:
            items.append(first.value)
        else:
            raise OCPError(f"Expected string, got '{first.value}'", first.line)

        while self.peek().type == TokenType.COMMA:
            self.pos += 1
            items.append(self.consume(TokenType.STRING).value)

        self.consume(TokenType.RBRACKET)
        body = self.parse_block()
        return ForList(var=var, items=items, body=body)

    def parse_while(self) -> While:
        cond_parts: list[str] = []
        while self.peek().type != TokenType.LBRACE:
            t = self.peek()
            if t.type == TokenType.STRING:
                cond_parts.append(f'"{t.value}"')
            else:
                cond_parts.append(t.value)
            self.pos += 1
        cond = parse_condition(' '.join(cond_parts))
        body = self.parse_block()
        return While(cond=cond, body=body)


# ── executor ────────────────────────────────────────────────────────────

class Executor:
    def __init__(self):
        self.env: dict[str, str] = {}
        self._exit_requested = False

    def _subst(self, s: str) -> str:
        """Replace $VAR in string with env value."""
        def repl(m):
            return self.env.get(m.group(1), '')
        return re.sub(r'\$(\w+)', repl, s)

    def _run_cmd(self, cmd: str) -> int:
        expanded = self._subst(cmd)
        result = subprocess.run(
            expanded,
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        return result.returncode

    def execute(self, node: Node):
        if isinstance(node, Block):
            for stmt in node.stmts:
                if self._exit_requested:
                    break
                self.execute(stmt)

        elif isinstance(node, Set):
            if node.expr is not None:
                result = eval_expr(node.expr, self.env)
                self.env[node.var] = str(result)
            else:
                val = self._subst(node.value)
                self.env[node.var] = val

        elif isinstance(node, Run):
            expanded = self._subst(node.cmd)
            rc = self._run_cmd(expanded)
            if rc != 0:
                raise OCPError(
                    f"Command failed (exit {rc}): {expanded}", node.line)

        elif isinstance(node, Echo):
            print(self._subst(node.msg))

        elif isinstance(node, Cd):
            path = self._subst(node.path)
            os.chdir(os.path.expanduser(path))

        elif isinstance(node, Parallel):
            errors: list[str] = []
            with ThreadPoolExecutor(max_workers=len(node.blocks)) as pool:
                futures = {
                    pool.submit(self._exec_parallel_block, block): i
                    for i, block in enumerate(node.blocks)
                }
                for fut in as_completed(futures):
                    idx = futures[fut]
                    try:
                        fut.result()
                    except OCPError as e:
                        errors.append(f"  Block {idx + 1}: {e}")

            if errors:
                raise OCPError(
                    "parallel blocks failed:\n" + "\n".join(errors),
                    node.line,
                )

        elif isinstance(node, TryCatch):
            try:
                self.execute(node.try_block)
            except Exception:
                self.execute(node.catch_block)

        elif isinstance(node, IfElse):
            if eval_condition(node.cond, self.env):
                self.execute(node.then_block)
            elif node.else_block:
                self.execute(node.else_block)

        elif isinstance(node, ForRange):
            start = eval_expr(node.start, self.env)
            end = eval_expr(node.end, self.env)
            for i in range(start, end + 1):
                self.env[node.var] = str(i)
                self.execute(node.body)

        elif isinstance(node, ForList):
            for item in node.items:
                self.env[node.var] = item
                self.execute(node.body)

        elif isinstance(node, While):
            iters = 0
            while eval_condition(node.cond, self.env):
                self.execute(node.body)
                iters += 1
                if iters > 100_000:
                    raise OCPError("Infinite loop detected (>100k iter)",
                                   node.line)

        else:
            raise OCPError(f"Unknown node: {type(node).__name__}")

    def _exec_parallel_block(self, block: Block):
        """Execute a block in a sub-executor (isolated env copy)."""
        sub = Executor()
        sub.env = self.env.copy()
        sub.execute(block)
        # Sync env back (writes from parallel blocks are merged)
        self.env.update(sub.env)


# ── main ────────────────────────────────────────────────────────────────

def interpret(file_path: str):
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, 'r') as f:
        source = f.read()

    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse_program()
        Executor().execute(ast)
    except OCPError as e:
        print(f"Error [line {e.line}]: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ocp_interpreter.py <script.ocp>', file=sys.stderr)
        sys.exit(1)
    interpret(sys.argv[1])
