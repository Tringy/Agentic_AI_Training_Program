#!/bin/bash
# Test runner script for Production AI Agent
# Usage: ./run_tests.sh [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default options
COVERAGE=true
VERBOSE=false
PARALLEL=false
SPECIFIC_TEST=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --parallel|-p)
            PARALLEL=true
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --no-coverage    Skip coverage reporting"
            echo "  --verbose, -v    Verbose output"
            echo "  --parallel, -p   Run tests in parallel"
            echo "  --test, -t FILE  Run specific test file"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Install dependencies first:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Set environment variables for testing
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-test_api_key_12345}"
export ENVIRONMENT="test"

print_info "Starting test suite..."
echo ""

# Build pytest command
PYTEST_CMD="pytest"

# Add test path
if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_CMD="$PYTEST_CMD $SPECIFIC_TEST"
else
    PYTEST_CMD="$PYTEST_CMD tests/"
fi

# Add verbose flag
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html --cov-report=term-missing"
fi

# Run tests
print_info "Running: $PYTEST_CMD"
echo ""

if $PYTEST_CMD; then
    print_info "All tests passed!"

    if [ "$COVERAGE" = true ]; then
        echo ""
        print_info "Coverage report generated in htmlcov/index.html"
    fi

    exit 0
else
    print_error "Tests failed!"
    exit 1
fi
