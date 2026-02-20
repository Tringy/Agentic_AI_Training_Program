#!/bin/bash
# Test runner for all exercises in AI Training program
# Runs pytest for all exercises that have tests

set -e  # Exit on error

echo "🧪 AI Training - Running Tests"
echo "=============================="
echo ""

# Track results
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to run tests for a directory
run_tests() {
    local dir=$1
    local name=$(basename "$dir")

    if [ -d "$dir/tests" ] || [ -f "$dir/test_*.py" ]; then
        echo "Testing: $name"
        echo "---"

        cd "$dir"

        if pytest -v --tb=short; then
            echo "✅ $name - PASSED"
            PASSED=$((PASSED + 1))
        else
            echo "❌ $name - FAILED"
            FAILED=$((FAILED + 1))
        fi

        TOTAL=$((TOTAL + 1))
        echo ""

        cd - > /dev/null
    fi
}

# Test all levels
for level_dir in level-*-*/; do
    if [ -d "$level_dir" ]; then
        echo "Level: $level_dir"
        echo ""

        # Test each exercise in level
        for ex_dir in "$level_dir"ex*/; do
            if [ -d "$ex_dir" ]; then
                run_tests "$ex_dir"
            fi
        done
    fi
done

# Test challenges
if [ -d "challenges" ]; then
    echo "Challenges:"
    echo ""

    for challenge_dir in challenges/*/; do
        if [ -d "$challenge_dir" ]; then
            run_tests "$challenge_dir"
        fi
    done
fi

# Summary
echo "=============================="
echo "Test Summary:"
echo "---"
echo "Total:   $TOTAL"
echo "Passed:  $PASSED ✅"
echo "Failed:  $FAILED ❌"
echo "Skipped: $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Review output above."
    exit 1
fi
