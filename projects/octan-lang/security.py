#!/usr/bin/env python3
"""
OCTAN Security Module
Input validation, sandboxing, and safe execution
"""

import re
import os
from typing import Any, List, Optional
from dataclasses import dataclass

class SecurityError(Exception):
    """Security violation detected"""
    pass

@dataclass
class SecurityPolicy:
    """Security configuration"""
    max_string_length: int = 10000
    max_array_size: int = 10000
    max_execution_time: float = 30.0  # seconds
    max_recursion_depth: int = 100
    allow_file_access: bool = False
    allow_network: bool = True
    allowed_paths: Optional[List[str]] = None
    forbidden_patterns: List[str] = None
    
    def __post_init__(self):
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                r'[;&|]\s*(?:rm|del|format|mkfs)',  # Dangerous commands
                r'\$\{.*\}',  # Shell interpolation
                r'`.*`',  # Command substitution
                r'\$\(.*\)',  # Command substitution
                r'\.\./',  # Path traversal
                r'\.\.\\',  # Windows path traversal
                r'<script',  # XSS attempts
                r'javascript:',  # JS injection
                r'data:text/html',  # Data URI
            ]

class InputValidator:
    """Validate all inputs for security"""
    
    # Whitelist for safe characters in identifiers
    SAFE_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*\??$')
    
    # Whitelist for safe strings (no control chars)
    SAFE_STRING = re.compile(r'^[\x20-\x7E\s]*$')
    
    # Dangerous path patterns
    DANGEROUS_PATH = re.compile(r'\.{2,}[/\\]|[/\\]\.{2,}')
    
    @staticmethod
    def validate_identifier(name: str) -> bool:
        """Check if identifier is safe"""
        if not InputValidator.SAFE_IDENTIFIER.match(name):
            raise SecurityError(f"Invalid identifier: {name}")
        return True
    
    @staticmethod
    def validate_string(value: str, max_length: int = 10000) -> str:
        """Sanitize and validate string input"""
        if len(value) > max_length:
            raise SecurityError(f"String too long: {len(value)} > {max_length}")
        
        # Check for null bytes
        if '\x00' in value:
            raise SecurityError("Null bytes not allowed")
        
        # Check for control characters (except common whitespace)
        for char in value:
            if ord(char) < 32 and char not in '\t\n\r':
                raise SecurityError(f"Control character detected: {repr(char)}")
        
        return value
    
    @staticmethod
    def validate_path(path: str, allowed_paths: Optional[List[str]] = None) -> str:
        """Validate file path for traversal attacks"""
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Check for path traversal
        if InputValidator.DANGEROUS_PATH.search(path):
            raise SecurityError(f"Path traversal detected: {path}")
        
        # Check if absolute (forbidden unless explicitly allowed)
        if os.path.isabs(normalized):
            raise SecurityError(f"Absolute paths not allowed: {path}")
        
        # Check allowed paths
        if allowed_paths:
            resolved = os.path.abspath(normalized)
            allowed = False
            for allowed_path in allowed_paths:
                if resolved.startswith(os.path.abspath(allowed_path)):
                    allowed = True
                    break
            if not allowed:
                raise SecurityError(f"Path not in allowed directories: {path}")
        
        return normalized
    
    @staticmethod
    def check_forbidden_patterns(value: str, patterns: List[str]) -> str:
        """Check for forbidden patterns in input"""
        for pattern in patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Forbidden pattern detected: {pattern}")
        return value
    
    @staticmethod
    def validate_array(elements: List[Any], max_size: int = 10000) -> List[Any]:
        """Validate array size"""
        if len(elements) > max_size:
            raise SecurityError(f"Array too large: {len(elements)} > {max_size}")
        return elements


class Sandbox:
    """Sandboxed execution environment"""
    
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.execution_start: Optional[float] = None
        self.call_depth = 0
        
    def start_execution(self):
        """Mark execution start for timeout tracking"""
        import time
        self.execution_start = time.time()
        self.call_depth = 0
    
    def check_timeout(self):
        """Check if execution has timed out"""
        import time
        if self.execution_start is None:
            return
        
        elapsed = time.time() - self.execution_start
        if elapsed > self.policy.max_execution_time:
            raise SecurityError(f"Execution timeout: {elapsed:.1f}s > {self.policy.max_execution_time}s")
    
    def enter_function(self):
        """Track function call depth"""
        self.call_depth += 1
        if self.call_depth > self.policy.max_recursion_depth:
            raise SecurityError(f"Max recursion depth exceeded: {self.call_depth}")
    
    def exit_function(self):
        """Track function exit"""
        self.call_depth -= 1
    
    def validate_input(self, value: Any) -> Any:
        """Validate any input value"""
        self.check_timeout()
        
        if isinstance(value, str):
            # Check string length
            if len(value) > self.policy.max_string_length:
                raise SecurityError(f"String too long: {len(value)}")
            
            # Check forbidden patterns
            InputValidator.check_forbidden_patterns(
                value, 
                self.policy.forbidden_patterns
            )
            
            return InputValidator.validate_string(
                value, 
                self.policy.max_string_length
            )
        
        elif isinstance(value, list):
            # Validate array size
            InputValidator.validate_array(value, self.policy.max_array_size)
            
            # Validate each element
            return [self.validate_input(item) for item in value]
        
        elif isinstance(value, (int, float)):
            # Check for NaN/Inf
            if isinstance(value, float):
                if value != value:  # NaN check
                    raise SecurityError("NaN not allowed")
                if value == float('inf') or value == float('-inf'):
                    raise SecurityError("Infinity not allowed")
            return value
        
        return value
    
    def safe_file_read(self, path: str) -> str:
        """Safely read file"""
        if not self.policy.allow_file_access:
            raise SecurityError("File access disabled")
        
        # Validate path
        safe_path = InputValidator.validate_path(path, self.policy.allowed_paths)
        
        # Check file size
        size = os.path.getsize(safe_path)
        if size > self.policy.max_string_length:
            raise SecurityError(f"File too large: {size}")
        
        # Read file
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def safe_file_write(self, path: str, content: str):
        """Safely write file"""
        if not self.policy.allow_file_access:
            raise SecurityError("File access disabled")
        
        # Validate path
        safe_path = InputValidator.validate_path(path, self.policy.allowed_paths)
        
        # Validate content
        if len(content) > self.policy.max_string_length:
            raise SecurityError(f"Content too large: {len(content)}")
        
        # Write file
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)


class SecureRuntime:
    """Secure runtime with sandboxing"""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.sandbox = Sandbox(self.policy)
        self.variables = {}
        self.functions = {}
        self.setup_secure_functions()
    
    def setup_secure_functions(self):
        """Setup built-in functions with security checks"""
        
        def safe_scan(target: str) -> List[int]:
            """Secure port scan"""
            self.sandbox.enter_function()
            try:
                # Validate target
                target = self.sandbox.validate_input(target)
                
                # Check for command injection
                InputValidator.check_forbidden_patterns(
                    target,
                    [r'[;&|]', r'`', r'\$']
                )
                
                print(f"[SCAN] Scanning {target}...")
                return [80, 443, 8080]
            finally:
                self.sandbox.exit_function()
        
        def safe_probe(ports: List[int]) -> List[str]:
            """Secure service probe"""
            self.sandbox.enter_function()
            try:
                ports = self.sandbox.validate_input(ports)
                print(f"[PROBE] Probing ports {ports}...")
                return [f"http://target:{int(p)}" for p in ports if p != 8080]
            finally:
                self.sandbox.exit_function()
        
        def safe_sqli(urls: List[str], param: str = "id") -> List[str]:
            """Secure SQL injection test"""
            self.sandbox.enter_function()
            try:
                urls = self.sandbox.validate_input(urls)
                param = self.sandbox.validate_input(param)
                
                # Validate param (no special chars)
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param):
                    raise SecurityError(f"Invalid parameter name: {param}")
                
                print(f"[SQLI] Testing SQL injection...")
                return [f"{u}?{param}=1'" for u in urls[:1]]
            finally:
                self.sandbox.exit_function()
        
        def safe_exploit(vulns: List[str]) -> List[str]:
            """Secure exploitation"""
            self.sandbox.enter_function()
            try:
                vulns = self.sandbox.validate_input(vulns)
                print(f"[EXPLOIT] Analyzing {len(vulns)} vulnerabilities...")
                return ["shell@target"]
            finally:
                self.sandbox.exit_function()
        
        def safe_shell(shells: List[str], cmd: str = "whoami") -> str:
            """Secure shell execution (SIMULATION ONLY)"""
            self.sandbox.enter_function()
            try:
                shells = self.sandbox.validate_input(shells)
                cmd = self.sandbox.validate_input(cmd)
                
                # Whitelist safe commands only
                SAFE_COMMANDS = {'whoami', 'id', 'pwd', 'ls', 'cat', 'echo'}
                if cmd not in SAFE_COMMANDS:
                    raise SecurityError(f"Command not allowed: {cmd}")
                
                print(f"[SHELL] Simulating '{cmd}' on {shells[0]}...")
                return "root"
            finally:
                self.sandbox.exit_function()
        
        def safe_report(data: Any) -> str:
            """Secure report generation"""
            self.sandbox.enter_function()
            try:
                data = self.sandbox.validate_input(data)
                print(f"[REPORT] Generating report...")
                return "report.md"
            finally:
                self.sandbox.exit_function()
        
        def safe_print(data: Any) -> Any:
            """Secure print"""
            self.sandbox.enter_function()
            try:
                # Prevent format string attacks
                if isinstance(data, str):
                    data = data.replace('%', '%%')
                print(f"[OUT] {data}")
                return data
            finally:
                self.sandbox.exit_function()
        
        def safe_read(path: str) -> str:
            """Secure file read"""
            return self.sandbox.safe_file_read(path)
        
        def safe_write(path: str, content: str) -> str:
            """Secure file write"""
            self.sandbox.safe_file_write(path, content)
            return "saved"
        
        self.functions = {
            'scan': safe_scan,
            'probe': safe_probe,
            'sqli': safe_sqli,
            'exploit': safe_exploit,
            'shell': safe_shell,
            'report': safe_report,
            'print': safe_print,
            'read': safe_read,
            'write': safe_write,
            'yes': lambda x: bool(x),
            'no': lambda x: not bool(x),
            'each': lambda x: x,
            'save': lambda x: "saved",
        }
    
    def execute(self, source: str) -> Any:
        """Execute with full security"""
        # Import here to avoid circular dependency
        import sys
        sys.path.insert(0, '/home/nxelleai/.openclaw/workspace/octan-lang')
        from interpreter import Lexer, Parser
        
        # Start sandbox
        self.sandbox.start_execution()
        
        # Validate source length
        if len(source) > self.policy.max_string_length * 10:
            raise SecurityError("Source code too large")
        
        # Tokenize
        self.sandbox.check_timeout()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        self.sandbox.check_timeout()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Execute
        results = []
        for node in ast:
            self.sandbox.check_timeout()
            result = self._evaluate(node)
            results.append(result)
        
        return results[-1] if results else None
    
    def _evaluate(self, node):
        """Evaluate node with security checks"""
        from interpreter import Assignment, Pipeline, Array, FunctionCall
        
        if isinstance(node, Assignment):
            value = self._evaluate(node.value)
            value = self.sandbox.validate_input(value)
            self.variables[node.name] = value
            return value
        
        elif isinstance(node, Array):
            elements = [self._evaluate(e) if hasattr(e, '__class__') else e for e in node.elements]
            return self.sandbox.validate_input(elements)
        
        elif isinstance(node, FunctionCall):
            if node.name not in self.functions:
                raise SecurityError(f"Unknown function: {node.name}")
            
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
                    if isinstance(step, str) and step in self.variables:
                        result = self.variables[step]
                    else:
                        result = step
                else:
                    if isinstance(step, FunctionCall):
                        args = [result] + [
                            self._evaluate(a) if hasattr(a, '__class__') else a 
                            for a in step.args
                        ]
                        result = self.functions[step.name](*args)
                    else:
                        result = step
            return result
        
        return node


# Default secure policy
DEFAULT_POLICY = SecurityPolicy(
    max_string_length=10000,
    max_array_size=10000,
    max_execution_time=30.0,
    max_recursion_depth=100,
    allow_file_access=False,  # Disabled by default
    allow_network=True,
    allowed_paths=None,
)
