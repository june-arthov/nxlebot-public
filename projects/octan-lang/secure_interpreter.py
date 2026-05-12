#!/usr/bin/env python3
"""
OCTAN - Secure Interpreter
With sandboxing and input validation
"""

import sys
from security import SecureRuntime, DEFAULT_POLICY, SecurityError

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OCTAN Secure Interpreter')
    parser.add_argument('file', nargs='?', help='Octan source file')
    parser.add_argument('-c', '--code', help='Execute code directly')
    parser.add_argument('--allow-files', action='store_true', help='Enable file access')
    parser.add_argument('--timeout', type=float, default=30.0, help='Execution timeout')
    
    args = parser.parse_args()
    
    # Setup security policy
    policy = DEFAULT_POLICY
    policy.max_execution_time = args.timeout
    if args.allow_files:
        policy.allow_file_access = True
    
    runtime = SecureRuntime(policy)
    
    if args.code:
        try:
            result = runtime.execute(args.code)
            if result is not None:
                print(f"=> {result}")
        except SecurityError as e:
            print(f"[SECURITY ERROR] {e}")
            sys.exit(1)
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
        except SecurityError as e:
            print(f"[SECURITY ERROR] {e}")
            sys.exit(1)
    else:
        # REPL
        print("OCTAN v0.5 Secure - OC+ Language")
        print(f"Timeout: {policy.max_execution_time}s | File access: {policy.allow_file_access}")
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
            except SecurityError as e:
                print(f"[SECURITY] {e}")
            except Exception as e:
                print(f"[ERROR] {type(e).__name__}: {e}")


if __name__ == '__main__':
    main()
