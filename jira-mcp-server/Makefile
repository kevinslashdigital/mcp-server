env:
	python3 -m venv .venv

activate:
	@echo "Run this in your shell instead: source .venv/bin/activate"

deactivate:
	@echo "Run this in your shell instead: deactivate"

install:
	pip3 install -r requirements.txt

install-dev:
	pip3 install -r requirements-dev.txt

start:
	python3 src/main.py

# Test targets
test:
	python3 -m pytest tests/ -v

test-unit:
	python3 -m pytest tests/test_main.py tests/test_jira_api_adapter.py -v

test-integration:
	python3 -m pytest tests/test_integration.py -v -m integration

test-coverage:
	python3 run_tests.py coverage

test-watch:
	python3 -m pytest tests/ -v --tb=short -f

# Real integration test targets (require actual Jira credentials)
test-real:
	python3 -m pytest tests/test_real_integration.py -v --jira-real

test-real-workflow:
	python3 -m pytest tests/test_real_integration.py::TestRealJiraWorkflow -v --jira-real

test-real-basic:
	python3 -m pytest tests/test_real_integration.py::TestRealJiraIntegration -v --jira-real