#!/usr/bin/env python3
"""
OCTAN - OC+ Language Interpreter
IN -> OUT Philosophy
"""

import re
import sys
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

class TokenType(Enum):
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    ARROW = auto()      # ->
    ASSIGN = auto()     # =
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    COMMA = auto()      # ,
    NEWLINE = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int

class Lexer:
    """Tokenize Octan source code"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        
    def error(self, msg: str):
        raise SyntaxError(f"Line {self.line}: {msg}")
    
    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
        return char
    
    def skip_whitespace(self):
        while self.peek() in ' \t\r':
            self.advance()
    
    def read_string(self) -> str:
        quote = self.advance()  # " or '
        result = []
        while self.peek() != quote:
            if self.peek() == '\0':
                self.error("Unterminated string")
            if self.peek() == '\\':
                self.advance()
                escape = self.advance()
                if escape == 'n':
                    result.append('\n')
                elif escape == 't':
                    result.append('\t')
                else:
                    result.append(escape)
            else:
                result.append(self.advance())
        self.advance()  # closing quote
        return ''.join(result)
    
    def read_number(self) -> float:
        result = []
        while self.peek().isdigit() or self.peek() == '.':
            result.append(self.advance())
        return float(''.join(result))
    
    def read_identifier(self) -> str:
        result = []
        while self.peek().isalnum() or self.peek() in '_?':
            result.append(self.advance())
        return ''.join(result)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.pos < len(self.source):
            self.skip_whitespace()
            char = self.peek()
            
            if char == '\0':
                break
            elif char == '\n':
                tokens.append(Token(TokenType.NEWLINE, None, self.line))
                self.advance()
            elif char == '#':
                # Comment - skip to end of line
                while self.peek() not in '\n\0':
                    self.advance()
            elif char in '"\'':
                tokens.append(Token(TokenType.STRING, self.read_string(), self.line))
            elif char.isdigit():
                tokens.append(Token(TokenType.NUMBER, self.read_number(), self.line))
            elif char.isalpha() or char == '_':
                tokens.append(Token(TokenType.IDENTIFIER, self.read_identifier(), self.line))
            elif char == '-' and self.peek(1) == '>':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.ARROW, '->', self.line))
            elif char == '=':
                self.advance()
                tokens.append(Token(TokenType.ASSIGN, '=', self.line))
            elif char == '[':
                self.advance()
                tokens.append(Token(TokenType.LBRACKET, '[', self.line))
            elif char == ']':
                self.advance()
                tokens.append(Token(TokenType.RBRACKET, ']', self.line))
            elif char == ',':
                self.advance()
                tokens.append(Token(TokenType.COMMA, ',', self.line))
            else:
                self.error(f"Unexpected character: {char}")
        
        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens


@dataclass
class ASTNode:
    pass

@dataclass
class Assignment(ASTNode):
    name: str
    value: Any

@dataclass
class Pipeline(ASTNode):
    steps: List[Any]

@dataclass
class Array(ASTNode):
    elements: List[Any]

@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[Any]


class Parser:
    """Parse tokens into AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        token = self.peek()
        self.pos += 1
        return token
    
    def match(self, *types: TokenType) -> bool:
        return self.peek().type in types
    
    def expect(self, type: TokenType, msg: str = None) -> Token:
        if not self.match(type):
            raise SyntaxError(f"Expected {type.name}, got {self.peek().type.name}")
        return self.advance()
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse_value(self) -> Any:
        """Parse a value (string, number, array, or identifier)"""
        if self.match(TokenType.STRING):
            return self.advance().value
        elif self.match(TokenType.NUMBER):
            return self.advance().value
        elif self.match(TokenType.LBRACKET):
            return self.parse_array()
        elif self.match(TokenType.IDENTIFIER):
            return self.advance().value
        else:
            raise SyntaxError(f"Unexpected token: {self.peek().type.name}")
    
    def parse_array(self) -> Array:
        self.expect(TokenType.LBRACKET)
        elements = []
        
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_value())
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        self.expect(TokenType.RBRACKET)
        return Array(elements)
    
    def parse_pipeline(self, first_value: Any) -> Pipeline:
        """Parse a pipeline: value -> func -> func ..."""
        steps = [first_value]
        
        while self.match(TokenType.ARROW):
            self.advance()  # consume ->
            
            if self.match(TokenType.IDENTIFIER):
                func_name = self.advance().value
                args = []
                
                # Check for additional arguments
                while not self.match(TokenType.ARROW, TokenType.NEWLINE, TokenType.EOF):
                    args.append(self.parse_value())
                
                steps.append(FunctionCall(func_name, args))
            else:
                raise SyntaxError(f"Expected function name after ->, got {self.peek().type.name}")
        
        return Pipeline(steps)
    
    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        
        if self.match(TokenType.EOF):
            return None
        
        # Assignment: name = value
        if self.match(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.ASSIGN:
            name = self.advance().value
            self.advance()  # consume =
            value = self.parse_value()
            return Assignment(name, value)
        
        # Pipeline starting with value
        if self.match(TokenType.STRING, TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LBRACKET):
            first_value = self.parse_value()
            
            if self.match(TokenType.ARROW):
                return self.parse_pipeline(first_value)
            else:
                # Just a value, treat as expression
                return Pipeline([first_value])
        
        return None
    
    def parse(self) -> List[ASTNode]:
        statements = []
        
        while True:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            elif self.match(TokenType.EOF):
                break
            else:
                self.advance()  # skip unknown
        
        return statements


class OctanRuntime:
    """Execute Octan code"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
        self.setup_builtins()
    
    def setup_builtins(self):
        """Define built-in functions"""
        
        def scan(target: str) -> List[int]:
            """Simulate port scan"""
            print(f"[SCAN] Scanning {target}...")
            return [80, 443, 8080]
        
        def probe(ports: List[int]) -> List[str]:
            """Simulate service probing"""
            print(f"[PROBE] Probing ports {ports}...")
            return [f"http://target:{p}" for p in ports if p != 8080]
        
        def sqli(urls: List[str], param: str = "id") -> List[str]:
            """Simulate SQL injection test"""
            print(f"[SQLI] Testing SQL injection on {urls}...")
            return [f"{u}?{param}=1'" for u in urls[:1]]
        
        def exploit(vulns: List[str]) -> List[str]:
            """Simulate exploitation"""
            print(f"[EXPLOIT] Exploiting {len(vulns)} vulnerabilities...")
            return ["shell@target"]
        
        def shell(shells: List[str], cmd: str = "whoami") -> str:
            """Execute command on shell"""
            print(f"[SHELL] Executing '{cmd}' on {shells[0]}...")
            return "root"
        
        def report(data: Any) -> str:
            """Generate report"""
            print(f"[REPORT] Generating report...")
            return "report.md"
        
        def print_fn(data: Any) -> None:
            """Print output"""
            print(f"[OUT] {data}")
            return data
        
        def yes(data: Any) -> bool:
            """Check if truthy"""
            return bool(data)
        
        def no(data: Any) -> bool:
            """Check if falsy"""
            return not bool(data)
        
        def each(items: List[Any]) -> List[Any]:
            """Iterate over items"""
            return items
        
        def save(data: Any) -> str:
            """Save data"""
            print(f"[SAVE] Saved: {data}")
            return "saved"
        
        self.functions = {
            'scan': scan,
            'probe': probe,
            'sqli': sqli,
            'exploit': exploit,
            'shell': shell,
            'report': report,
            'print': print_fn,
            'yes': yes,
            'no': no,
            'each': each,
            'save': save,
        }
    
    def evaluate(self, node: ASTNode) -> Any:
        """Evaluate an AST node"""
        
        if isinstance(node, Assignment):
            value = self.evaluate(node.value)
            self.variables[node.name] = value
            return value
        
        elif isinstance(node, Array):
            return [self.evaluate(e) if isinstance(e, ASTNode) else e for e in node.elements]
        
        elif isinstance(node, FunctionCall):
            if node.name not in self.functions:
                raise RuntimeError(f"Unknown function: {node.name}")
            
            # Evaluate arguments
            args = []
            for arg in node.args:
                if isinstance(arg, str) and arg in self.variables:
                    args.append(self.variables[arg])
                else:
                    args.append(arg)
            
            return self.functions[node.name](*args)
        
        elif isinstance(node, Pipeline):
            result = None
            
            for i, step in enumerate(node.steps):
                if i == 0:
                    # First step - get initial value
                    if isinstance(step, str) and step in self.variables:
                        result = self.variables[step]
                    else:
                        result = step
                else:
                    # Subsequent steps - function calls
                    if isinstance(step, FunctionCall):
                        # Pass previous result as first argument
                        args = [result] + [self.evaluate(a) if isinstance(a, ASTNode) else a for a in step.args]
                        result = self.functions[step.name](*args)
                    else:
                        result = step
            
            return result
        
        else:
            # Literal value
            return node
    
    def execute(self, source: str) -> Any:
        """Execute Octan source code"""
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Execute
        results = []
        for node in ast:
            result = self.evaluate(node)
            results.append(result)
        
        return results[-1] if results else None


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OCTAN Interpreter')
    parser.add_argument('file', nargs='?', help='Octan source file')
    parser.add_argument('-c', '--code', help='Execute code directly')
    
    args = parser.parse_args()
    
    runtime = OctanRuntime()
    
    if args.code:
        result = runtime.execute(args.code)
        if result is not None:
            print(f"=> {result}")
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                source = f.read()
            result = runtime.execute(source)
            if result is not None:
                print(f"=> {result}")
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
    else:
        # REPL
        print("OCTAN v0.5 - OC+ Language")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                line = input(">>> ")
                if line.lower() in ('exit', 'quit'):
                    break
                if not line.strip():
                    continue
                
                result = runtime.execute(line)
                if result is not None:
                    print(f"=> {result}")
            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == '__main__':
    main()
