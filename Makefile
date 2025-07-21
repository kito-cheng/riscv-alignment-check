# RISC-V Alignment Test Makefile
# Now using Python test runner for better maintainability

.PHONY: all test clean list help

# Default target - run all tests
all: test

# Run all tests using Python script
test:
	python3 test_runner.py

# Run specific test configurations
test-norvc:
	python3 test_runner.py --configs norvc

test-norelax:
	python3 test_runner.py --configs norelax

test-relax1:
	python3 test_runner.py --sources relax1

test-relax2:
	python3 test_runner.py --sources relax2

# Clean generated files
clean:
	python3 test_runner.py --clean

# List available tests
list:
	python3 test_runner.py --list

# Show help
help:
	@echo "Available targets:"
	@echo "  all, test       - Run all tests"
	@echo "  test-norvc      - Run only norvc configuration"
	@echo "  test-norelax    - Run only norelax configuration"
	@echo "  test-relax1     - Run only relax-align-1.s tests"
	@echo "  test-relax2     - Run only relax-align-2.s tests"
	@echo "  clean           - Clean generated files"
	@echo "  list            - List available tests"
	@echo "  help            - Show this help"
	@echo ""
	@echo "For more options, run: python3 test_runner.py --help"
