#!/bin/bash

# Create necessary directories
mkdir -p logs
mkdir -p htmlcov

# Function to run tests with specific markers
run_tests() {
    local marker=$1
    local report=$2
    echo "Running $marker tests..."
    pytest -m "$marker" --cov=ai --cov-report=html --cov-report=term-missing
    return $?
}

# Run unit tests
run_tests "unit" "unit"
if [ $? -ne 0 ]; then
    echo "Unit tests failed!"
    exit 1
fi

# Check if we should run integration tests
if [ "$1" == "--integration" ]; then
    # Check for API key
    if [ -z "$OPENWEATHER_API_KEY" ]; then
        echo "Warning: OPENWEATHER_API_KEY not set. Integration tests will be skipped."
        echo "To run integration tests, set OPENWEATHER_API_KEY environment variable."
    else
        # Run integration tests
        run_tests "integration" "integration"
        if [ $? -ne 0 ]; then
            echo "Integration tests failed!"
            exit 1
        fi
    fi
fi

echo "Tests passed successfully!"
echo "Coverage report available in htmlcov/index.html" 