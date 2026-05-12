"""OC+ (Octane) DSL — Pipeline Automation Language

Usage:
    from ocplus import execute_script
    result = execute_script("echo Hello; run ls")
"""

from .interpreter import tokenize, Parser, Executor, execute_script, run_file

__version__ = "2.0.0"
