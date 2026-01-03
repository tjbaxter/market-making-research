#!/usr/bin/env python3
"""
Verify code structure without running full tests.
Checks imports and basic structure.
"""

import sys
import ast
import os
from pathlib import Path


def check_file(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)


def main():
    """Run verification checks."""
    print("🔍 Verifying project structure...\n")
    
    project_root = Path(__file__).parent
    
    # Check required files exist
    required_files = [
        'requirements.txt',
        'setup.py',
        'pytest.ini',
        'README.md',
        'LICENSE',
        '.gitignore',
        'src/__init__.py',
        'src/simulation/__init__.py',
        'src/simulation/price_process.py',
        'src/simulation/order_flow.py',
        'src/simulation/accounting.py',
        'src/simulation/market_simulator.py',
        'tests/__init__.py',
        'tests/test_price_process.py',
        'tests/test_order_flow.py',
        'tests/test_accounting.py',
        'tests/test_market_simulator.py',
        'examples/basic_simulation.py',
    ]
    
    print("📁 Checking file structure...")
    missing_files = []
    for filepath in required_files:
        full_path = project_root / filepath
        if full_path.exists():
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} - MISSING")
            missing_files.append(filepath)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files")
        return False
    
    print("\n✅ All required files present\n")
    
    # Check Python file syntax
    print("🐍 Checking Python syntax...")
    python_files = [f for f in required_files if f.endswith('.py')]
    
    syntax_errors = []
    for filepath in python_files:
        full_path = project_root / filepath
        valid, error = check_file(full_path)
        if valid:
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} - SYNTAX ERROR")
            syntax_errors.append((filepath, error))
    
    if syntax_errors:
        print(f"\n❌ Found {len(syntax_errors)} syntax errors:")
        for filepath, error in syntax_errors:
            print(f"\n  {filepath}:")
            print(f"    {error}")
        return False
    
    print("\n✅ All Python files have valid syntax\n")
    
    # Check key content
    print("📝 Checking key content...")
    
    with open(project_root / 'setup.py', 'r') as f:
        setup_content = f.read()
        if 'market_making_research' in setup_content:
            print("  ✓ setup.py has correct package name")
        else:
            print("  ✗ setup.py missing package name")
            return False
    
    with open(project_root / 'requirements.txt', 'r') as f:
        reqs = f.read()
        required_deps = ['numpy', 'pandas', 'matplotlib', 'scipy', 'pytest']
        missing_deps = [dep for dep in required_deps if dep not in reqs.lower()]
        if not missing_deps:
            print("  ✓ requirements.txt has all key dependencies")
        else:
            print(f"  ✗ requirements.txt missing: {missing_deps}")
            return False
    
    print("\n✅ All content checks passed\n")
    
    print("=" * 60)
    print("🎉 Project structure verification PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: ./install.sh")
    print("  2. Or manually:")
    print("     python3 -m venv venv")
    print("     source venv/bin/activate")
    print("     pip install -r requirements.txt")
    print("     pip install -e .")
    print("  3. Run tests: pytest")
    print("  4. Run example: python examples/basic_simulation.py")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

