#!/usr/bin/env python3
"""
Test runner script for jira-mcp-server.
Provides different test execution options.
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|integration|all|coverage]")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  all         - Run all tests")
        print("  coverage    - Run all tests with coverage report")
        sys.exit(1)

    test_type = sys.argv[1].lower()
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    if test_type == "unit":
        cmd = ["python", "-m", "pytest", "tests/test_main.py", "tests/test_jira_api_adapter.py", "-v"]
        run_command(cmd, "Running unit tests")
        
    elif test_type == "integration":
        cmd = ["python", "-m", "pytest", "tests/test_integration.py", "-v", "-m", "integration"]
        run_command(cmd, "Running integration tests")
        
    elif test_type == "all":
        cmd = ["python", "-m", "pytest", "tests/", "-v"]
        run_command(cmd, "Running all tests")
        
    elif test_type == "coverage":
        # Install coverage if not available
        try:
            import coverage
        except ImportError:
            print("Installing coverage...")
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)
        
        cmd = ["python", "-m", "coverage", "run", "-m", "pytest", "tests/"]
        if run_command(cmd, "Running tests with coverage"):
            run_command(["python", "-m", "coverage", "report"], "Generating coverage report")
            run_command(["python", "-m", "coverage", "html"], "Generating HTML coverage report")
            print("📊 HTML coverage report generated in htmlcov/index.html")
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()
