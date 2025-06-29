#!/usr/bin/env python3
"""
Comprehensive code validation script for Civitai Shortcut project.

This script performs static analysis to catch import errors, undefined variables,
and other issues that could cause runtime errors during refactoring.
"""

import ast
import sys
import importlib.util
from pathlib import Path
from typing import List
import subprocess


class CodeValidator:
    """Validates Python code for common refactoring issues."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        self.python_files = []

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))

        # Filter out venv, __pycache__, cache directories
        filtered_files = []
        skip_patterns = ["venv/", "env/", "__pycache__", ".git/", "htmlcov/", "node_modules/"]
        for file in python_files:
            path_str = str(file)
            if any(x in path_str for x in skip_patterns) or not file.is_file():
                continue
            filtered_files.append(file)

        self.python_files = filtered_files
        return filtered_files

    def validate_syntax(self, file_path: Path) -> bool:
        """Check if file has valid Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.errors.append(f"SYNTAX ERROR in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"ERROR reading {file_path}: {e}")
            return False

    def check_imports(self, file_path: Path) -> bool:
        """Check if all imports can be resolved."""
        try:
            # Add project root to path for imports
            sys.path.insert(0, str(self.project_root))

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self._can_import(alias.name):
                            self.errors.append(
                                f"IMPORT ERROR in {file_path}: Cannot import '{alias.name}'"
                            )
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    if module_name and not self._can_import(module_name):
                        self.errors.append(
                            f"IMPORT ERROR in {file_path}: Cannot import from '{module_name}'"
                        )

            return True
        except Exception as e:
            self.errors.append(f"IMPORT CHECK ERROR in {file_path}: {e}")
            return False
        finally:
            # Remove added path
            if str(self.project_root) in sys.path:
                sys.path.remove(str(self.project_root))

    def _can_import(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        # Skip known external dependencies that may not be installed
        external_deps = {
            'gradio',
            'PIL',
            'modules',
            'torch',
            'transformers',
            'numpy',
            'requests',
            'httpx',
            'cv2',
        }

        if module_name.split('.')[0] in external_deps:
            return True

        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
        except Exception:
            return True  # Assume it's okay if other errors

    def find_undefined_variables(self, file_path: Path) -> bool:
        """Find potentially undefined variables using AST analysis."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Track defined names per scope
            defined_names = set()

            for node in ast.walk(tree):
                # Track assignments
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_names.add(target.id)
                elif isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        defined_names.add(name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        defined_names.add(name)

            # Check for undefined usage
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    name = node.id
                    if (
                        name not in defined_names
                        and name not in dir(__builtins__)
                        and name not in ['self', 'cls']
                    ):

                        # Get line number for better error reporting
                        line_no = getattr(node, 'lineno', 'unknown')
                        self.warnings.append(
                            f"UNDEFINED VAR in {file_path}:{line_no}: '{name}' may be undefined"
                        )

            return True
        except Exception as e:
            self.errors.append(f"UNDEFINED VAR CHECK ERROR in {file_path}: {e}")
            return False

    def run_flake8(self) -> bool:
        """Run flake8 linting on project files only."""
        try:
            # Create a list of project files to check
            files_to_check = []
            for file_path in self.python_files:
                files_to_check.append(str(file_path))

            if not files_to_check:
                self.warnings.append("No Python files found to check with flake8")
                return True

            # Run flake8 only on project files
            result = subprocess.run(
                ['flake8'] + files_to_check, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode != 0:
                self.warnings.append(f"FLAKE8 ISSUES:\n{result.stdout}")

            return True
        except FileNotFoundError:
            self.warnings.append("FLAKE8 not found - install with: pip install flake8")
            return False
        except Exception as e:
            self.warnings.append(f"FLAKE8 ERROR: {e}")
            return False

    def validate_project(self) -> bool:
        """Run comprehensive validation."""
        print("🔍 Starting comprehensive code validation...")

        # Find all Python files
        files = self.find_python_files()
        print(f"📁 Found {len(files)} Python files")

        # Validate each file
        for file_path in files:
            print(f"📄 Validating {file_path.relative_to(self.project_root)}")

            # Check syntax
            if not self.validate_syntax(file_path):
                continue

            # Check imports
            self.check_imports(file_path)

            # Check for undefined variables
            self.find_undefined_variables(file_path)

        # Run flake8
        print("🧹 Running flake8 analysis...")
        self.run_flake8()

        # Report results
        self.report_results()

        return len(self.errors) == 0

    def report_results(self):
        """Report validation results."""
        print("\n" + "=" * 80)
        print("📊 VALIDATION RESULTS")
        print("=" * 80)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        elif not self.errors:
            print(f"\n✅ No critical errors found (only {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Found {len(self.errors)} errors and {len(self.warnings)} warnings")


def main():
    """Main validation entry point."""
    project_root = Path(__file__).parent.parent
    validator = CodeValidator(str(project_root))

    success = validator.validate_project()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
