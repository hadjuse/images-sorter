#!/usr/bin/env python3
"""
Test runner script for the Image Processing API
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite"""
    
    # Change to the test directory
    test_dir = os.path.dirname(__file__)
    os.chdir(test_dir)
    
    print("🧪 Running Image Processing API Tests")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--color=yes",
        "--cov=../api",
        "--cov-report=term-missing",
        "--cov-report=html:../coverage_report",
        "test_api.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())