#!/usr/bin/env python3
"""
run_tests.py — Run unit tests with coverage + line counts
"""

import sys, subprocess

def run(cmd):
    print(f"\n[RUNNING] {cmd}\n")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[FAILED] {cmd} → exit {e.returncode}")
        sys.exit(e.returncode)

def main():
    # Run pytest with coverage per file
    run("pytest --cov=azq --cov-report=term-missing tests/")

    # Optional: also create HTML report
    run("pytest --cov=azq --cov-report=html tests/")

    # Count lines of code (requires cloc)
    run("cloc .")

if __name__ == "__main__":
    main()

