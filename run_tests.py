#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API
"""

import subprocess
import sys


def run_tests(with_coverage=True, verbose=True):
    """Run the test suite with optional coverage reporting."""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if with_coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)
    
    result = subprocess.run(cmd, cwd=".")
    return result.returncode


if __name__ == "__main__":
    # Parse command line arguments
    with_coverage = "--no-cov" not in sys.argv
    verbose = "--quiet" not in sys.argv
    
    exit_code = run_tests(with_coverage=with_coverage, verbose=verbose)
    sys.exit(exit_code)