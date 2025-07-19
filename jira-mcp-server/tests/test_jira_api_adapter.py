"""
Unit tests for JiraApiAdapter class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from adapter.jira_api_adapter import JiraApiAdapter


class TestJiraApiAdapter:
    """Test cases for JiraApiAdapter class."""

    @pytest.fixture
    def adapter(self, mock_env_vars):
        """Create JiraApiAdapter instance with mocked environment."""
        return JiraApiAdapter()

    def test_init(self, mock_env_vars):
        """Test JiraApiAdapter initialization."""
        adapter = JiraApiAdapter()
        assert adapter.project_key == "TEST"
        assert adapter.base_url == "https://test.atlassian.net/rest/api/3"
        assert adapter.auth.username == "test@example.com"
        assert adapter.auth.password == "test_token"
        assert adapter.headers["Accept"] == "application/json"
        assert adapter.headers["Content-Type"] == "application/json"

    @patch('requests.post')
    def test_create_ticket_success(self, mock_post, adapter, sample_jira_response):
        """Test successful ticket creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = sample_jira_response["create_response"]
        mock_post.return_value = mock_response

        result = adapter.create_ticket("Test Summary", "Test Description")
        
        assert result == "ticket TEST-123 is successfully created"
        mock_post.assert_called_once()
        
        # Verify the payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['fields']['summary'] == "Test Summary"
        assert payload['fields']['project']['key'] == "TEST"
        assert payload['fields']['issuetype']['name'] == "Task"

    @patch('requests.post')
    def test_create_ticket_failure(self, mock_post, adapter):
        """Test ticket creation failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.create_ticket("Test Summary", "Test Description")
        
        assert "Error creating ticket with status code 400" in str(exc_info.value)

    @patch('requests.put')
    def test_update_ticket_success(self, mock_put, adapter):
        """Test successful ticket update."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response

        result = adapter.update_ticket("TEST-123", "Updated Summary", "Updated Description")
        
        assert result == "ticket is successfully updated"
        mock_put.assert_called_once()

    @patch('requests.put')
    def test_update_ticket_failure(self, mock_put, adapter):
        """Test ticket update failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_put.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.update_ticket("TEST-123", "Updated Summary", "Updated Description")
        
        assert "Error updating ticket 404" in str(exc_info.value)

    @patch('requests.get')
    def test_list_tickets_success(self, mock_get, adapter, sample_jira_response):
        """Test successful ticket listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_jira_response["list_response"]
        mock_get.return_value = mock_response

        result = adapter.list_tickets(10)
        
        assert len(result) == 1
        assert result[0]["key"] == "TEST-123"
        assert result[0]["fields"]["summary"] == "Test Issue"
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_list_tickets_failure(self, mock_get, adapter):
        """Test ticket listing failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.list_tickets(10)
        
        assert "Error listing tickets 401" in str(exc_info.value)

    @patch('requests.get')
    def test_get_transitions_success(self, mock_get, adapter, sample_jira_response):
        """Test successful transitions listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_jira_response["transitions_response"]
        mock_get.return_value = mock_response

        result = adapter.get_transitions("TEST-123")
        
        assert len(result) == 3
        assert result[0]["name"] == "To Do"
        assert result[1]["name"] == "In Progress"
        assert result[2]["name"] == "Done"
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_transitions_failure(self, mock_get, adapter):
        """Test transitions listing failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.get_transitions("TEST-123")
        
        assert "Error getting transitions 404" in str(exc_info.value)

    @patch('requests.post')
    def test_transition_ticket_success(self, mock_post, adapter):
        """Test successful ticket transition."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        result = adapter.transition_ticket("TEST-123", "21")
        
        assert result == "Ticket status is successfully updated"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_transition_ticket_failure(self, mock_post, adapter):
        """Test ticket transition failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.transition_ticket("TEST-123", "21")
        
        assert "Error transitioning ticket 400" in str(exc_info.value)

    @patch('requests.post')
    def test_add_comment_success(self, mock_post, adapter):
        """Test successful comment addition."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = adapter.add_comment("TEST-123", "Test comment")
        
        assert result == "Comment is successfully added"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_add_comment_failure(self, mock_post, adapter):
        """Test comment addition failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            adapter.add_comment("TEST-123", "Test comment")
        
        assert "Error adding comment 400" in str(exc_info.value)

    def test_requests_exception_handling(self, adapter):
        """Test handling of requests exceptions."""
        with patch('requests.post', side_effect=requests.RequestException("Connection error")):
            with pytest.raises(requests.RequestException) as exc_info:
                adapter.create_ticket("Test", "Test")
            assert "Connection error" in str(exc_info.value)
