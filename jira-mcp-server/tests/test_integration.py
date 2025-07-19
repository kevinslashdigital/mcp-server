"""
Integration tests for jira-mcp-server.
These tests verify the interaction between main.py and JiraApiAdapter.
"""
import pytest
from unittest.mock import Mock, patch
import requests
from main import (
    create_jira_ticket,
    update_jira_ticket,
    list_jira_tickets,
    list_jira_statuses,
    update_jira_status,
    add_comment_to_jira_ticket
)


@pytest.mark.integration
class TestJiraMcpServerIntegration:
    """Integration tests for the complete jira-mcp-server workflow."""

    @patch('requests.post')
    def test_end_to_end_ticket_creation(self, mock_post, mock_env_vars):
        """Test end-to-end ticket creation flow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "TEST-123"}
        mock_post.return_value = mock_response

        result = create_jira_ticket("Integration Test Ticket", "This is a test description")
        
        assert "TEST-123" in result
        assert "successfully created" in result
        mock_post.assert_called_once()

    @patch('requests.put')
    def test_end_to_end_ticket_update(self, mock_put, mock_env_vars):
        """Test end-to-end ticket update flow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response

        result = update_jira_ticket("TEST-123", "Updated Title", "Updated Description")
        
        assert "successfully updated" in result
        mock_put.assert_called_once()

    @patch('requests.get')
    def test_end_to_end_ticket_listing(self, mock_get, mock_env_vars):
        """Test end-to-end ticket listing flow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test Issue",
                        "description": {
                            "content": [
                                {
                                    "content": [
                                        {"text": "Test description"}
                                    ]
                                }
                            ]
                        },
                        "status": {"name": "To Do"}
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = list_jira_tickets(10)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "TEST-123"
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_end_to_end_status_listing(self, mock_get, mock_env_vars):
        """Test end-to-end status listing flow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transitions": [
                {"id": "11", "name": "To Do"},
                {"id": "21", "name": "In Progress"},
                {"id": "31", "name": "Done"}
            ]
        }
        mock_get.return_value = mock_response

        result = list_jira_statuses("TEST-123")
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["name"] == "To Do"
        mock_get.assert_called_once()

    @patch('requests.post')
    @patch('requests.get')
    def test_end_to_end_status_update(self, mock_get, mock_post, mock_env_vars):
        """Test end-to-end status update flow."""
        # Mock get transitions response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "transitions": [
                {"id": "21", "name": "In Progress"}
            ]
        }
        mock_get.return_value = mock_get_response

        # Mock post transition response
        mock_post_response = Mock()
        mock_post_response.status_code = 204
        mock_post.return_value = mock_post_response

        result = update_jira_status("TEST-123", "In Progress")
        
        assert "successfully updated" in result
        mock_get.assert_called_once()
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_end_to_end_add_comment(self, mock_post, mock_env_vars):
        """Test end-to-end comment addition flow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = add_comment_to_jira_ticket("TEST-123", "This is a test comment")
        
        assert "successfully added" in result
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_error_handling_network_failure(self, mock_post, mock_env_vars):
        """Test error handling when network requests fail."""
        mock_post.side_effect = requests.RequestException("Network error")

        result = create_jira_ticket("Test", "Test")
        
        assert "Error creating jira ticket" in result

    @patch('requests.post')
    def test_error_handling_api_error(self, mock_post, mock_env_vars):
        """Test error handling when API returns error status."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid project key"
        mock_post.return_value = mock_response

        result = create_jira_ticket("Test", "Test")
        
        assert "Error creating jira ticket" in result


@pytest.mark.integration
@pytest.mark.slow
class TestJiraMcpServerWorkflows:
    """Test complete workflows combining multiple operations."""

    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def test_complete_ticket_workflow(self, mock_get, mock_put, mock_post, mock_env_vars):
        """Test a complete workflow: create -> update -> list -> add comment."""
        
        # Mock create ticket response
        create_response = Mock()
        create_response.status_code = 201
        create_response.json.return_value = {"key": "TEST-123"}
        
        # Mock update ticket response
        update_response = Mock()
        update_response.status_code = 204
        
        # Mock list tickets response
        list_response = Mock()
        list_response.status_code = 200
        list_response.json.return_value = {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Updated Test Issue",
                        "description": {
                            "content": [{"content": [{"text": "Updated description"}]}]
                        },
                        "status": {"name": "To Do"}
                    }
                }
            ]
        }
        
        # Mock add comment response
        comment_response = Mock()
        comment_response.status_code = 201
        
        # Configure mock responses based on URL patterns
        def mock_request_side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            if 'issue' in url and kwargs.get('json', {}).get('fields'):
                return create_response
            elif 'comment' in url:
                return comment_response
            else:
                return update_response
        
        mock_post.side_effect = mock_request_side_effect
        mock_put.return_value = update_response
        mock_get.return_value = list_response
        
        # Execute workflow
        # 1. Create ticket
        create_result = create_jira_ticket("Test Issue", "Test description")
        assert "TEST-123" in create_result
        assert "successfully created" in create_result
        
        # 2. Update ticket
        update_result = update_jira_ticket("TEST-123", "Updated Test Issue", "Updated description")
        assert "successfully updated" in update_result
        
        # 3. List tickets
        list_result = list_jira_tickets(10)
        assert isinstance(list_result, list)
        assert len(list_result) == 1
        assert list_result[0]["key"] == "TEST-123"
        
        # 4. Add comment
        comment_result = add_comment_to_jira_ticket("TEST-123", "Workflow test comment")
        assert "successfully added" in comment_result
        
        # Verify all calls were made
        assert mock_post.call_count >= 2  # create and comment
        assert mock_put.call_count == 1   # update
        assert mock_get.call_count == 1   # list
