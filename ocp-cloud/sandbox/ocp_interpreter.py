#!/usr/bin/env python3
"""
OC+ (Octane) DSL Interpreter v2.0
Full-featured pipeline automation language.
Usage: python3 ocp_interpreter.py script.ocp
"""

import sys, os, re, subprocess, shlex, threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any

# ═══════════════════════════════════════════════
# LEXER
# ═══════════════════════════════════════════════

TOK_WORD = "WORD"
TOK_STRING = "STRING"
TOK_LBRACE = "LBRACE"
TOK_RBRACE = "RBRACE"
TOK_LBRACKET = "LBRACKET"
TOK_RBRACKET = "RBRACKET"
TOK_DOTDOT = "DOTDOT"
TOK_EOF = "EOF"
TOK_EQ = "EQ"
TOK_COMMA = "COMMA"


def tokenize(text: str) -> list[tuple[str, str]]:
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]

        if c == "#":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue

        if c in " \t\r\n":
            i += 1
            continue

        if c == "{":
            tokens.append((TOK_LBRACE, "{"))
            i += 1
            continue
        if c == "}":
            tokens.append((TOK_RBRACE, "}"))
            i += 1
            continue
        if c == "[":
            tokens.append((TOK_LBRACKET, "["))
            i += 1
            continue
        if c == "]":
            tokens.append((TOK_RBRACKET, "]"))
            i += 1
            continue
        if c == ",":
            tokens.append((TOK_COMMA, ","))
            i += 1
            continue
        if c == "=" and i + 1 < len(text) and text[i + 1] == "=":
            tokens.append(("OP", "=="))
            i += 2
            continue
        if c == "!" and i + 1 < len(text) and text[i + 1] == "=":
            tokens.append(("OP", "!="))
            i += 2
            continue
        if c == "<" and i + 1 < len(text) and text[i + 1] == "=":
            tokens.append(("OP", "<="))
            i += 2
            continue
        if c == ">" and i + 1 < len(text) and text[i + 1] == "=":
            tokens.append(("OP", ">="))
            i += 2
            continue
        if c in "<>":
            tokens.append(("OP", c))
            i += 1
            continue
        if c == "." and i + 1 < len(text) and text[i + 1] == ".":
            tokens.append((TOK_DOTDOT, ".."))
            i += 2
            continue
        if c == "=":
            tokens.append((TOK_EQ, "="))
            i += 1
            continue

        if c == '"':
            i += 1
            s = ""
            while i < len(text) and text[i] != '"':
                if text[i] == "\\" and i + 1 < len(text):
                    i += 1
                    s += text[i]
                else:
                    s += text[i]
                i += 1
            if i < len(text):
                i += 1
            tokens.append((TOK_STRING, s))
            continue

        if c.isalpha() or c == "_":
            w = ""
            while i < len(text) and (text[i].isalnum() or text[i] in "._-"):
                w += text[i]
                i += 1
            tokens.append((TOK_WORD, w))
            continue

        if c.isdigit():
            n = ""
            while i < len(text) and text[i].isdigit():
                n += text[i]
                i += 1
            tokens.append(("NUM", n))
            continue

        if c in "+-*/%()":
            tokens.append(("OP", c))
            i += 1
            continue

        i += 1

    tokens.append((TOK_EOF, ""))
    return tokens


# ═══════════════════════════════════════════════
# AST NODES
# ═══════════════════════════════════════════════

class ExprNode:
    pass


class IntLit(ExprNode):
    def __init__(self, v): self.v = v


class VarRef(ExprNode):
    def __init__(self, name): self.name = name


class BinOp(ExprNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class ASTNode:
    pass


class SetCmd(ASTNode):
    def __init__(self, var, is_expr, value):
        self.var = var
        self.is_expr = is_expr
        self.value = value  # str or ExprNode


class RunCmd(ASTNode):
    def __init__(self, cmd): self.cmd = cmd


class EchoCmd(ASTNode):
    def __init__(self, msg): self.msg = msg


class CdCmd(ASTNode):
    def __init__(self, path): self.path = path


class ParallelCmd(ASTNode):
    def __init__(self, blocks): self.blocks = blocks


class TryCmd(ASTNode):
    def __init__(self, try_block, catch_block):
        self.try_block = try_block
        self.catch_block = catch_block


class IfCmd(ASTNode):
    def __init__(self, cond_var, cond_op, cond_val, then_block, else_block):
        self.cond_var = cond_var
        self.cond_op = cond_op
        self.cond_val = cond_val
        self.then_block = then_block
        self.else_block = else_block


class ForRangeCmd(ASTNode):
    def __init__(self, var, start, end, block):
        self.var = var
        self.start = start  # ExprNode
        self.end = end      # ExprNode
        self.block = block


class ForListCmd(ASTNode):
    def __init__(self, var, items, block):
        self.var = var
        self.items = items
        self.block = block


class WhileCmd(ASTNode):
    def __init__(self, var, op, val, block):
        self.var = var
        self.op = op
        self.val = val
        self.block = block


class Block(ASTNode):
    def __init__(self, stmts): self.stmts = stmts


class Program(ASTNode):
    def __init__(self, stmts): self.stmts = stmts


# ═══════════════════════════════════════════════
# PARSER
# ═══════════════════════════════════════════════

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def expect(self, typ, val=None):
        t = self.consume()
        if t[0] != typ or (val is not None and t[1] != val):
            raise SyntaxError(f"Expected {typ}({val}), got {t}")
        return t

    def parse_expr(self) -> ExprNode:
        return self._parse_binop(0)

    def _parse_binop(self, min_prec: int) -> ExprNode:
        left = self._parse_atom()
        while True:
            t = self.peek()
            if t[0] not in ("OP",):
                break
            prec = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}.get(t[1], -1)
            if prec < min_prec:
                break
            op = self.consume()[1]
            right = self._parse_binop(prec + 1)
            left = BinOp(left, op, right)
        return left

    def _parse_atom(self) -> ExprNode:
        t = self.peek()
        if t[0] == "NUM":
            self.consume()
            return IntLit(int(t[1]))
        if t[0] == TOK_WORD:
            self.consume()
            return VarRef(t[1])
        if t[0] == "OP" and t[1] == "(":
            self.consume()
            e = self.parse_expr()
            self.expect("OP", ")")
            return e
        if t[0] == "OP" and t[1] == "-":
            self.consume()
            return BinOp(IntLit(0), "-", self._parse_atom())
        if t[0] == "OP" and t[1] == "$":
            raise SyntaxError("$ must be followed by var name (use set without $)")
        raise SyntaxError(f"Unexpected token in expression: {t}")

    def parse_block(self) -> Block:
        self.expect(TOK_LBRACE)
        stmts = []
        while self.peek()[0] != TOK_RBRACE:
            stmts.append(self.parse_stmt())
        self.expect(TOK_RBRACE)
        return Block(stmts)

    def parse_stmt(self) -> ASTNode:
        t = self.peek()
        if t[0] != TOK_WORD:
            raise SyntaxError(f"Expected command, got {t}")

        cmd = t[1].lower()
        self.consume()

        if cmd == "set":
            name = self.expect(TOK_WORD)[1]
            self.expect(TOK_EQ)
            val_tok = self.peek()
            if val_tok[0] == TOK_STRING:
                self.consume()
                return SetCmd(name, False, val_tok[1])
            else:
                expr = self.parse_expr()
                return SetCmd(name, True, expr)

        elif cmd == "run":
            s = self.expect(TOK_STRING)[1]
            return RunCmd(s)

        elif cmd == "echo":
            s = self.expect(TOK_STRING)[1]
            return EchoCmd(s)

        elif cmd == "cd":
            s = self.expect(TOK_STRING)[1]
            return CdCmd(s)

        elif cmd == "parallel":
            blocks = []
            while self.peek()[0] == TOK_LBRACE:
                blocks.append(self.parse_block())
            if len(blocks) < 2:
                raise SyntaxError("parallel requires at least 2 blocks")
            return ParallelCmd(blocks)

        elif cmd == "try":
            try_block = self.parse_block()
            self.expect(TOK_WORD, "catch")
            catch_block = self.parse_block()
            return TryCmd(try_block, catch_block)

        elif cmd == "if":
            var = self.expect(TOK_WORD)[1]
            op_tok = self.peek()
            if op_tok[0] != "OP" or op_tok[1] not in ("==", "!=", "<", ">", "<=", ">="):
                raise SyntaxError(f"Expected comparison operator, got {op_tok}")
            op = self.consume()[1]
            val_tok = self.peek()
            if val_tok[0] == TOK_STRING:
                val = self.consume()[1]
            elif val_tok[0] == TOK_WORD:
                val = self.consume()[1]
            elif val_tok[0] == "NUM":
                val = self.consume()[1]
            else:
                raise SyntaxError(f"Expected value, got {val_tok}")
            then_block = self.parse_block()
            else_block = None
            if self.peek()[0] == TOK_WORD and self.peek()[1].lower() == "else":
                self.consume()
                else_block = self.parse_block()
            return IfCmd(var, op, val, then_block, else_block)

        elif cmd == "for":
            var = self.expect(TOK_WORD)[1]
            self.expect(TOK_WORD, "in")
            nxt = self.peek()
            if nxt[0] == TOK_LBRACKET:
                self.consume()
                # Range: [start..end]
                start = self._parse_range_expr()
                self.expect(TOK_DOTDOT)
                end = self._parse_range_expr()
                self.expect(TOK_RBRACKET)
                block = self.parse_block()
                return ForRangeCmd(var, start, end, block)
            else:
                raise SyntaxError(f"Expected [ for for loop range, got {nxt}")

        elif cmd == "while":
            var = self.expect(TOK_WORD)[1]
            op_tok = self.peek()
            if op_tok[0] != "OP" or op_tok[1] not in ("==", "!=", "<", ">", "<=", ">="):
                raise SyntaxError(f"Expected comparison operator, got {op_tok}")
            op = self.consume()[1]
            val_tok = self.peek()
            if val_tok[0] == TOK_STRING:
                val = self.consume()[1]
            elif val_tok[0] == TOK_WORD:
                val = self.consume()[1]
            elif val_tok[0] == "NUM":
                val = self.consume()[1]
            else:
                raise SyntaxError(f"Expected value, got {val_tok}")
            block = self.parse_block()
            return WhileCmd(var, op, val, block)

        else:
            raise SyntaxError(f"Unknown command: {cmd}")

    def _parse_range_expr(self) -> ExprNode:
        """Parse int literal or $VAR for range endpoints."""
        t = self.peek()
        if t[0] == "NUM":
            self.consume()
            return IntLit(int(t[1]))
        if t[0] == TOK_WORD:
            self.consume()
            return VarRef(t[1])
        raise SyntaxError(f"Expected integer or $VAR for range endpoint, got {t}")

    def parse(self) -> Program:
        stmts = []
        while self.peek()[0] != TOK_EOF:
            stmts.append(self.parse_stmt())
        return Program(stmts)


# ═══════════════════════════════════════════════
# EXECUTOR
# ═══════════════════════════════════════════════

class Executor:
    def __init__(self):
        self.env: dict[str, str] = {}
        self.catch_active = False

    def expand(self, s: str) -> str:
        def repl(m):
            var = m.group(1)
            return self.env.get(var, f"${var}")
        return re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_.-]*)', repl, s)

    def eval_expr(self, node: ExprNode) -> int:
        if isinstance(node, IntLit):
            return node.v
        if isinstance(node, VarRef):
            val = self.env.get(node.name, "0")
            try:
                return int(val)
            except ValueError:
                raise RuntimeError(f"Variable ${node.name} = '{val}' is not an integer")
        if isinstance(node, BinOp):
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)
            if node.op == "+": return left + right
            if node.op == "-": return left - right
            if node.op == "*": return left * right
            if node.op == "/": return left // right
            if node.op == "%": return left % right
        raise RuntimeError(f"Unknown expr node: {node}")

    def check_cond(self, var: str, op: str, val: str) -> bool:
        a = self.env.get(var, "")
        b = self.env.get(val, val)  # try var lookup first, fallback to literal
        # Try numeric comparison
        try:
            ai, bi = int(a), int(b)
            if op == "==": return ai == bi
            if op == "!=": return ai != bi
            if op == "<":  return ai < bi
            if op == ">":  return ai > bi
            if op == "<=": return ai <= bi
            if op == ">=": return ai >= bi
        except ValueError:
            pass
        # String comparison
        if op == "==": return a == b
        if op == "!=": return a != b
        raise RuntimeError(f"Cannot compare '{a}' {op} '{b}'")

    def execute_block(self, block: Block):
        for stmt in block.stmts:
            self.execute(stmt)

    def execute(self, node: ASTNode):
        if self.catch_active:
            return

        try:
            if isinstance(node, SetCmd):
                if node.is_expr:
                    self.env[node.var] = str(self.eval_expr(node.value))
                else:
                    self.env[node.var] = self.expand(node.value)

            elif isinstance(node, RunCmd):
                cmd = self.expand(node.cmd)
                # shlex.split: safe arg parsing, no shell injection
                args = shlex.split(cmd)
                result = subprocess.run(args, shell=False, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout, end="")
                if result.stderr:
                    print(result.stderr, end="", file=sys.stderr)
                if result.returncode != 0:
                    raise RuntimeError(f"Command failed with exit code {result.returncode}: {cmd}")

            elif isinstance(node, EchoCmd):
                print(self.expand(node.msg))

            elif isinstance(node, CdCmd):
                path = self.expand(node.path)
                os.chdir(os.path.expanduser(path))

            elif isinstance(node, ParallelCmd):
                results = []
                errors = []

                def run_block(block):
                    e = Executor()
                    e.env = dict(self.env)
                    try:
                        e.execute_block(block)
                        return e.env, None
                    except Exception as ex:
                        return None, ex

                with ThreadPoolExecutor() as pool:
                    futures = [pool.submit(run_block, b) for b in node.blocks]
                    for f in futures:
                        res_env, err = f.result()
                        if err:
                            errors.append(err)
                        if res_env:
                            results.append(res_env)

                for r in results:
                    self.env.update(r)
                if errors:
                    raise RuntimeError(f"Parallel execution errors: {errors}")

            elif isinstance(node, TryCmd):
                try:
                    self.execute_block(node.try_block)
                except Exception as e:
                    print(f"[catch] {e}", file=sys.stderr)
                    self.execute_block(node.catch_block)

            elif isinstance(node, IfCmd):
                cond_var = node.cond_var
                if cond_var.startswith("$"):
                    cond_var = cond_var[1:]
                if self.check_cond(cond_var, node.cond_op, self.expand(node.cond_val)):
                    self.execute_block(node.then_block)
                elif node.else_block:
                    self.execute_block(node.else_block)

            elif isinstance(node, ForRangeCmd):
                start = self.eval_expr(node.start)
                end = self.eval_expr(node.end)
                for i in range(start, end + 1):
                    self.env[node.var] = str(i)
                    self.execute_block(node.block)

            elif isinstance(node, ForListCmd):
                for item in node.items:
                    self.env[node.var] = self.expand(item)
                    self.execute_block(node.block)

            elif isinstance(node, WhileCmd):
                iters = 0
                while self.check_cond(node.var, node.op, self.expand(node.val)):
                    if iters >= 100000:
                        raise RuntimeError("While loop exceeded 100,000 iterations")
                    self.execute_block(node.block)
                    iters += 1

            elif isinstance(node, Program):
                for stmt in node.stmts:
                    self.execute(stmt)

        except Exception as e:
            if not self.catch_active:
                print(f"Error: {e}", file=sys.stderr)
                raise


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ocp_interpreter.py <script.ocp>", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    with open(script_path) as f:
        source = f.read()

    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        program = parser.parse()
        executor = Executor()
        executor.execute(program)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
