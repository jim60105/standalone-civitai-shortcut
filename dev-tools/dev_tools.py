#!/usr/bin/env python3
"""
Development Tools for Civitai Shortcut Project

This script provides various development tools to catch refactoring issues at coding time.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_basic_validation():
    """Run basic validation checks."""
    print("🔧 Running basic validation checks...")
    result = subprocess.run(
        [sys.executable, "dev-tools/validate_code.py"], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ All checks passed!")
    else:
        print("❌ Issues found:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

    return result.returncode == 0


def run_type_check():
    """Run mypy type checking if available."""
    print("🔧 Running type checking...")
    try:
        result = subprocess.run(
            [
                "mypy",
                "scripts/civitai_manager_libs/",
                "--ignore-missing-imports",
                "--explicit-package-bases",
                "--namespace-packages",
                "--show-error-codes",
                "--pretty",
                "--show-column-numbers",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Type checking passed!")
        else:
            print("❌ Type issues found:")
            print(result.stdout)
            if result.stderr:
                print("Stderr:")
                print(result.stderr)

            # Count errors for summary
            error_lines = [line for line in result.stdout.split('\n') if ': error:' in line]
            note_lines = [line for line in result.stdout.split('\n') if ': note:' in line]
            print(f"\n📊 Summary: {len(error_lines)} errors, {len(note_lines)} notes")

        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️ mypy not installed. Install with: pip install mypy")
        return True


def run_tests():
    """Run the test suite."""
    print("🔧 Running tests...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ All tests passed!")
            # Extract summary information from output
            lines = result.stdout.split('\n')
            for line in lines[-10:]:  # Look at last 10 lines for summary
                if ' passed' in line and ('skipped' in line or 'warnings' in line):
                    print(f"📊 {line.strip()}")
                    break
        else:
            print("❌ Test failures:")
            print(result.stdout)
            if result.stderr:
                print("Stderr:")
                print(result.stderr)

        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️ pytest not installed. Install with: pip install pytest")
        return True


def run_tests_verbose():
    """Run the test suite with verbose output."""
    print("🔧 Running tests with verbose output...")
    print("💡 Tip: For specific tests, use: python -m pytest tests/test_specific.py -v")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
            text=True
        )

        # Since we're not capturing output, the results appear directly
        if result.returncode == 0:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Some tests failed!")

        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️ pytest not installed. Install with: pip install pytest")
        return True


def run_quick_check():
    """Run a quick syntax and import check."""
    print("🔧 Running quick syntax and import check...")

    project_root = Path.cwd()
    files = list(project_root.glob("scripts/**/*.py"))

    errors = []
    for file in files:
        if any(x in str(file) for x in ["__pycache__", "venv", ".git"]):
            continue

        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check syntax
            compile(content, str(file), 'exec')
            print(f"✅ {file.relative_to(project_root)}")

        except SyntaxError as e:
            errors.append(f"❌ {file.relative_to(project_root)}: {e}")
        except Exception as e:
            errors.append(f"⚠️ {file.relative_to(project_root)}: {e}")

    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    else:
        print(f"\n✅ All {len(files)} files have valid syntax!")
        return True


def run_comprehensive_validation():
    """Run comprehensive development validation workflow."""
    print("🚀 Running comprehensive development validation...")

    all_passed = True

    # 1. Quick syntax check
    if not run_quick_check():
        all_passed = False

    # 2. Basic validation
    if not run_basic_validation():
        all_passed = False

    # 3. Type checking (optional)
    run_type_check()  # Don't fail on type issues

    if all_passed:
        print("\n🎉 All validation checks passed!")
    else:
        print("\n💥 Validation checks failed. Please fix issues before proceeding.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Development tools for Civitai Shortcut")
    parser.add_argument(
        "command",
        nargs='?',  # Make command optional
        choices=["validate", "quick", "types", "tests", "tests-verbose", "comprehensive"],
        help="Command to run",
    )

    args = parser.parse_args()
    
    # Show help if no command provided
    if args.command is None:
        parser.print_help()
        print("\nAvailable commands:")
        print("  quick        - Fast syntax and import check")
        print("  validate     - Comprehensive code validation")
        print("  types        - Type checking with mypy")
        print("  tests        - Run test suite (summary)")
        print("  tests-verbose- Run test suite (detailed output)")
        print("  comprehensive- Complete validation workflow")
        sys.exit(0)

    if args.command == "validate":
        success = run_basic_validation()
    elif args.command == "quick":
        success = run_quick_check()
    elif args.command == "types":
        success = run_type_check()
    elif args.command == "tests":
        success = run_tests()
    elif args.command == "tests-verbose":
        success = run_tests_verbose()
    elif args.command == "comprehensive":
        run_comprehensive_validation()
        return
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
