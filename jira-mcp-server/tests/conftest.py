"""
Pytest configuration and fixtures for jira-mcp-server tests.
"""
import pytest
from unittest.mock import Mock, patch
import os
import sys

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'JIRA_PROJECT_KEY': 'TEST',
        'JIRA_DOMAIN': 'test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_API_TOKEN': 'test_token'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_jira_adapter():
    """Mock JiraApiAdapter for testing."""
    with patch('adapter.jira_api_adapter.JiraApiAdapter') as mock:
        adapter_instance = Mock()
        mock.return_value = adapter_instance
        yield adapter_instance

@pytest.fixture
def sample_jira_response():
    """Sample Jira API response data."""
    return {
        "create_response": {
            "key": "TEST-123",
            "id": "10001",
            "self": "https://test.atlassian.net/rest/api/3/issue/10001"
        },
        "list_response": {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test Issue",
                        "description": {"content": [{"content": [{"text": "Test description"}]}]},
                        "status": {"name": "To Do"}
                    }
                }
            ]
        },
        "transitions_response": {
            "transitions": [
                {"id": "11", "name": "To Do"},
                {"id": "21", "name": "In Progress"},
                {"id": "31", "name": "Done"}
            ]
        }
    }


# Configuration for real integration tests
def pytest_addoption(parser):
    """Add command line option to enable real Jira tests."""
    parser.addoption(
        "--jira-real",
        action="store_true",
        default=False,
        help="Run tests against real Jira instance"
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "real_integration: mark test as real integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Skip real integration tests unless --jira-real flag is provided."""
    if config.getoption("--jira-real"):
        return
    skip_real = pytest.mark.skip(reason="need --jira-real option to run")
    for item in items:
        if "real_integration" in item.keywords:
            item.add_marker(skip_real)
