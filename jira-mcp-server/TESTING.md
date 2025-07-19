# Testing Guide for jira-mcp-server

This project includes comprehensive testing with both mocked unit/integration tests and real API integration tests.

## Test Types

### 1. Unit Tests (`test_main.py`, `test_jira_api_adapter.py`)
- Test individual functions and methods in isolation
- Use mocked dependencies
- Fast execution
- No external dependencies required

### 2. Mocked Integration Tests (`test_integration.py`)
- Test complete workflows with mocked API responses
- Verify interaction between components
- Fast execution
- No external dependencies required

### 3. Real Integration Tests (`test_real_integration.py`)
- Test against actual Jira API
- Require valid Jira credentials
- Slower execution
- Create/modify real Jira tickets

## Running Tests

### Quick Start - All Mocked Tests
```bash
# Run all mocked tests (unit + integration)
make test

# Or directly with pytest
python -m pytest tests/ -v
```

### Specific Test Categories
```bash
# Unit tests only
make test-unit

# Mocked integration tests only
make test-integration

# With coverage report
make test-coverage
```

### Real Integration Tests

#### Prerequisites
1. **Jira Instance Access**: You need access to a Jira instance (cloud or server)
2. **API Token**: Generate an API token from your Jira account
3. **Test Project**: Have a Jira project where you can create test tickets

#### Setup Environment Variables
Create a `.env` file or set environment variables:

```bash
# Required for real integration tests
export JIRA_PROJECT_KEY="YOUR_PROJECT_KEY"    # e.g., "TEST" or "DEMO"
export JIRA_DOMAIN="your-domain.atlassian.net"  # Without https://
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

#### Generate Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "jira-mcp-server-testing")
4. Copy the generated token

#### Running Real Integration Tests
```bash
# Run all real integration tests
make test-real

# Run specific test classes
make test-real-basic      # Basic CRUD operations
make test-real-workflow   # Complete workflow tests

# Or directly with pytest
python -m pytest tests/test_real_integration.py -v --jira-real
```

## Test Structure

```
tests/
├── __init__.py                 # Test package
├── conftest.py                # Shared fixtures and configuration
├── test_main.py               # Unit tests for main.py functions
├── test_jira_api_adapter.py   # Unit tests for JiraApiAdapter
├── test_integration.py        # Mocked integration tests
└── test_real_integration.py   # Real API integration tests
```

## Real Integration Test Features

### Test Classes

#### `TestRealJiraIntegration`
- `test_real_create_jira_ticket`: Creates an actual ticket
- `test_real_list_jira_tickets`: Lists real tickets from your project
- `test_real_list_jira_statuses`: Gets available transitions
- `test_real_add_comment_to_jira_ticket`: Adds a comment
- `test_real_update_jira_ticket`: Updates ticket content
- `test_real_update_jira_status`: Changes ticket status

#### `TestRealJiraWorkflow`
- `test_real_complete_ticket_workflow`: Full lifecycle test (create → update → comment → status change)

#### `TestRealJiraErrorHandling`
- `test_real_invalid_ticket_key`: Tests error handling with invalid tickets
- `test_real_invalid_status_transition`: Tests invalid status transitions

### Safety Features

1. **Explicit Opt-in**: Real tests only run with `--jira-real` flag
2. **Environment Validation**: Checks for required credentials before running
3. **Clear Test Data**: Test tickets are clearly labeled as test data
4. **Graceful Cleanup**: Tests are designed to be safe and non-destructive

### Example Test Output

```bash
$ make test-real
python3 -m pytest tests/test_real_integration.py -v --jira-real
=============================================== test session starts ===============================================
tests/test_real_integration.py::TestRealJiraIntegration::test_real_create_jira_ticket PASSED
Created ticket: TEST-123
tests/test_real_integration.py::TestRealJiraIntegration::test_real_list_jira_tickets PASSED
Found 5 tickets
tests/test_real_integration.py::TestRealJiraIntegration::test_real_list_jira_statuses PASSED
Available transitions: ['To Do', 'In Progress', 'Done']
...
```

## Best Practices

### For Development
1. **Run mocked tests frequently** during development
2. **Use real tests sparingly** to verify actual API integration
3. **Clean up test data** from your Jira instance periodically

### For CI/CD
1. **Include mocked tests** in your CI pipeline
2. **Run real tests** in a dedicated test environment
3. **Use separate Jira projects** for testing vs production

### For Debugging
1. **Start with unit tests** to isolate issues
2. **Use mocked integration tests** to verify component interaction
3. **Use real tests** to debug actual API behavior

## Troubleshooting

### Common Issues

#### "Missing required environment variables"
- Ensure all required environment variables are set
- Check that `.env` file is loaded or variables are exported

#### "need --jira-real option to run"
- Real integration tests require the `--jira-real` flag
- Use `make test-real` or add `--jira-real` to pytest command

#### API Authentication Errors
- Verify your API token is correct and not expired
- Check that your email matches your Jira account
- Ensure your domain is correct (without https://)

#### Permission Errors
- Verify you have permission to create tickets in the specified project
- Check that the project key exists and is accessible

### Getting Help

1. **Check test output** for specific error messages
2. **Verify Jira credentials** manually in a browser
3. **Run individual tests** to isolate issues
4. **Check Jira API documentation** for specific error codes

## Test Coverage

Current test coverage includes:
- ✅ All 6 MCP tool functions
- ✅ All JiraApiAdapter methods
- ✅ Error handling and edge cases
- ✅ Complete workflow scenarios
- ✅ Real API integration
- ✅ Input validation

Total: **40+ mocked tests** + **10+ real integration tests**
