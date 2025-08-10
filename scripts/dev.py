#!/usr/bin/env python3
"""
BDR AI - Development Scripts
============================

Python-based development tools to replace Makefile for Windows compatibility.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description or cmd} - Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or cmd} - Failed")
        print(f"Error: {e.stderr}")
        return False


def install():
    """Install the package."""
    return run_command("pip install -e .", "Installing package")


def install_dev():
    """Install the package with development dependencies."""
    success = run_command("pip install -e .[dev]", "Installing package with dev dependencies")
    if success:
        run_command("pre-commit install", "Installing pre-commit hooks")
    return success


def test():
    """Run tests."""
    return run_command("pytest", "Running tests")


def test_cov():
    """Run tests with coverage."""
    return run_command("pytest --cov=bdr_ai --cov-report=html --cov-report=term-missing", "Running tests with coverage")


def test_fast():
    """Run fast tests only."""
    return run_command('pytest -m "not slow"', "Running fast tests")


def lint():
    """Run linting checks."""
    success1 = run_command("flake8 bdr_ai/ tests/", "Running flake8")
    success2 = run_command("mypy bdr_ai/", "Running mypy")
    return success1 and success2


def format_code():
    """Format code."""
    success1 = run_command("black .", "Formatting with black")
    success2 = run_command("isort .", "Sorting imports")
    return success1 and success2


def check():
    """Run all checks (format, lint, test)."""
    print("🔍 Running all checks...")
    success1 = run_command("black --check .", "Checking code format")
    success2 = run_command("isort --check-only .", "Checking import order")
    success3 = run_command("flake8 bdr_ai/ tests/", "Running flake8")
    success4 = run_command("mypy bdr_ai/", "Running mypy")
    success5 = run_command("pytest", "Running tests")
    return all([success1, success2, success3, success4, success5])


def clean():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")
    dirs_to_remove = ["build", "dist", "*.egg-info", ".pytest_cache", "htmlcov"]
    files_to_remove = [".coverage"]
    
    for dir_name in dirs_to_remove:
        if "*" in dir_name:
            # Handle wildcards
            for path in Path(".").glob(dir_name):
                if path.is_dir():
                    run_command(f"rmdir /s /q {path}", f"Removing {path}")
        else:
            run_command(f"rmdir /s /q {dir_name}", f"Removing {dir_name}")
    
    for file_name in files_to_remove:
        run_command(f"del {file_name}", f"Removing {file_name}")
    
    # Remove __pycache__ directories
    for pycache in Path(".").rglob("__pycache__"):
        run_command(f"rmdir /s /q {pycache}", f"Removing {pycache}")
    
    # Remove .pyc files
    for pyc_file in Path(".").rglob("*.pyc"):
        run_command(f"del {pyc_file}", f"Removing {pyc_file}")


def build():
    """Build the package."""
    return run_command("python setup.py sdist bdist_wheel", "Building package")


def deploy():
    """Deploy to AWS Lambda."""
    return run_command("serverless deploy", "Deploying to AWS Lambda")


def cache_status():
    """Check Apollo cache status."""
    return run_command("python cache_manager.py status", "Checking cache status")


def cache_clear():
    """Clear Apollo cache."""
    return run_command("python cache_manager.py clear", "Clearing cache")


def run_pipeline():
    """Run the complete BDR pipeline."""
    return run_command("python main.py --max-leads 5", "Running BDR pipeline")


def run_preview():
    """Run pipeline in preview mode."""
    return run_command("python main.py --max-leads 5 --preview-only", "Running pipeline preview")


def send_emails():
    """Send queued emails."""
    return run_command("python send_queue.py", "Sending emails")


def help_commands():
    """Show available commands."""
    print("BDR AI - Development Commands")
    print("=============================")
    print()
    print("Available commands:")
    print("  install        - Install the package")
    print("  install-dev    - Install with development dependencies")
    print("  test           - Run tests")
    print("  test-cov       - Run tests with coverage")
    print("  test-fast      - Run fast tests only")
    print("  lint           - Run linting checks")
    print("  format         - Format code")
    print("  check          - Run all checks (format, lint, test)")
    print("  clean          - Clean up build artifacts")
    print("  build          - Build the package")
    print("  deploy         - Deploy to AWS Lambda")
    print("  cache-status   - Check Apollo cache status")
    print("  cache-clear    - Clear Apollo cache")
    print("  run-pipeline   - Run the complete BDR pipeline")
    print("  run-preview    - Run pipeline in preview mode")
    print("  send-emails    - Send queued emails")
    print("  help           - Show this help message")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="BDR AI Development Scripts")
    parser.add_argument("command", help="Command to run")
    
    args = parser.parse_args()
    
    commands = {
        "install": install,
        "install-dev": install_dev,
        "test": test,
        "test-cov": test_cov,
        "test-fast": test_fast,
        "lint": lint,
        "format": format_code,
        "check": check,
        "clean": clean,
        "build": build,
        "deploy": deploy,
        "cache-status": cache_status,
        "cache-clear": cache_clear,
        "run-pipeline": run_pipeline,
        "run-preview": run_preview,
        "send-emails": send_emails,
        "help": help_commands,
    }
    
    if args.command not in commands:
        print(f"❌ Unknown command: {args.command}")
        help_commands()
        sys.exit(1)
    
    success = commands[args.command]()
    if success is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
