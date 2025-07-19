"""
Unit tests for main.py MCP tool functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Import the functions from main.py
from main import (
    create_jira_ticket,
    update_jira_ticket,
    list_jira_tickets,
    list_jira_statuses,
    update_jira_status,
    add_comment_to_jira_ticket
)


class TestMainFunctions:
    """Test cases for main.py MCP tool functions."""

    @patch('main.adapter')
    def test_create_jira_ticket_success(self, mock_adapter):
        """Test successful ticket creation."""
        mock_adapter.create_ticket.return_value = "ticket TEST-123 is successfully created"
        
        result = create_jira_ticket("Test Title", "Test Description")
        
        assert result == "ticket TEST-123 is successfully created"
        mock_adapter.create_ticket.assert_called_once_with(
            summary="Test Title", 
            description_text="Test Description"
        )

    @patch('main.adapter')
    def test_create_jira_ticket_exception(self, mock_adapter):
        """Test ticket creation with exception."""
        mock_adapter.create_ticket.side_effect = Exception("API Error")
        
        result = create_jira_ticket("Test Title", "Test Description")
        
        assert "Error creating jira ticket: API Error" in result

    @patch('main.adapter')
    def test_update_jira_ticket_success(self, mock_adapter):
        """Test successful ticket update."""
        mock_adapter.update_ticket.return_value = "ticket TEST-123 is successfully updated"
        
        result = update_jira_ticket("TEST-123", "Updated Title", "Updated Description")
        
        assert result == "ticket TEST-123 is successfully updated"
        mock_adapter.update_ticket.assert_called_once_with(
            issue_key="TEST-123",
            summary="Updated Title",
            description_text="Updated Description"
        )

    @patch('main.adapter')
    def test_update_jira_ticket_exception(self, mock_adapter):
        """Test ticket update with exception."""
        mock_adapter.update_ticket.side_effect = Exception("Update failed")
        
        result = update_jira_ticket("TEST-123", "Updated Title", "Updated Description")
        
        assert "Error updating jira ticket: Update failed" in result

    @patch('main.adapter')
    def test_list_jira_tickets_success(self, mock_adapter):
        """Test successful ticket listing."""
        mock_tickets = [
            {"key": "TEST-123", "summary": "Test Issue 1"},
            {"key": "TEST-124", "summary": "Test Issue 2"}
        ]
        mock_adapter.list_tickets.return_value = mock_tickets
        
        result = list_jira_tickets(10)
        
        assert result == mock_tickets
        assert len(result) == 2
        mock_adapter.list_tickets.assert_called_once_with(max_results=10)

    @patch('main.adapter')
    def test_list_jira_tickets_exception(self, mock_adapter):
        """Test ticket listing with exception."""
        mock_adapter.list_tickets.side_effect = Exception("List failed")
        
        result = list_jira_tickets(10)
        
        assert result is None

    @patch('main.adapter')
    def test_list_jira_statuses_success(self, mock_adapter):
        """Test successful status listing."""
        mock_statuses = [
            {"id": "11", "name": "To Do"},
            {"id": "21", "name": "In Progress"},
            {"id": "31", "name": "Done"}
        ]
        mock_adapter.get_transitions.return_value = mock_statuses
        
        result = list_jira_statuses("TEST-123")
        
        assert result == mock_statuses
        assert len(result) == 3
        mock_adapter.get_transitions.assert_called_once_with("TEST-123")

    @patch('main.adapter')
    def test_list_jira_statuses_exception(self, mock_adapter):
        """Test status listing with exception."""
        mock_adapter.get_transitions.side_effect = Exception("Status list failed")
        
        result = list_jira_statuses("TEST-123")
        
        assert result is None

    @patch('main.adapter')
    def test_update_jira_status_success(self, mock_adapter):
        """Test successful status update."""
        mock_transitions = [{"id": "21", "name": "In Progress"}]
        mock_adapter.get_transitions.return_value = mock_transitions
        mock_adapter.transition_ticket.return_value = "Ticket status is successfully updated"
        
        result = update_jira_status("TEST-123", "In Progress")
        
        assert result == "Ticket status is successfully updated"
        mock_adapter.get_transitions.assert_called_once_with("TEST-123")
        mock_adapter.transition_ticket.assert_called_once_with("TEST-123", "21")

    @patch('main.adapter')
    def test_update_jira_status_invalid_status(self, mock_adapter):
        """Test status update with invalid status."""
        mock_transitions = [{"id": "21", "name": "In Progress"}]
        mock_adapter.get_transitions.return_value = mock_transitions
        
        result = update_jira_status("TEST-123", "Invalid Status")
        
        assert result == "Status is unknown"
        mock_adapter.get_transitions.assert_called_once_with("TEST-123")

    @patch('main.adapter')
    def test_update_jira_status_exception(self, mock_adapter):
        """Test status update with exception."""
        mock_adapter.get_transitions.side_effect = Exception("Status update failed")
        
        result = update_jira_status("TEST-123", "In Progress")
        
        assert result is None

    @patch('main.adapter')
    def test_add_comment_to_jira_ticket_success(self, mock_adapter):
        """Test successful comment addition."""
        mock_adapter.add_comment.return_value = "Comment is successfully added"
        
        result = add_comment_to_jira_ticket("TEST-123", "This is a test comment")
        
        assert result == "Comment is successfully added"
        mock_adapter.add_comment.assert_called_once_with(
            issue_key="TEST-123",
            comment="This is a test comment"
        )

    @patch('main.adapter')
    def test_add_comment_to_jira_ticket_exception(self, mock_adapter):
        """Test comment addition with exception."""
        mock_adapter.add_comment.side_effect = Exception("Comment failed")
        
        result = add_comment_to_jira_ticket("TEST-123", "This is a test comment")
        
        assert result is None


class TestMainFunctionInputValidation:
    """Test cases for input validation and edge cases."""

    @patch('main.adapter')
    def test_create_jira_ticket_empty_inputs(self, mock_adapter):
        """Test ticket creation with empty inputs."""
        mock_adapter.create_ticket.return_value = "ticket TEST-123 is successfully created"
        
        result = create_jira_ticket("", "")
        
        mock_adapter.create_ticket.assert_called_once_with(summary="", description_text="")

    @patch('main.adapter')
    def test_update_jira_ticket_empty_issue_key(self, mock_adapter):
        """Test ticket update with empty issue key."""
        mock_adapter.update_ticket.return_value = "ticket  is successfully updated"
        
        result = update_jira_ticket("", "Title", "Description")
        
        mock_adapter.update_ticket.assert_called_once_with(
            issue_key="",
            summary="Title",
            description_text="Description"
        )

    @patch('main.adapter')
    def test_list_jira_tickets_zero_max_result(self, mock_adapter):
        """Test ticket listing with zero max result."""
        mock_adapter.list_tickets.return_value = []
        
        result = list_jira_tickets(0)
        
        assert result == []
        mock_adapter.list_tickets.assert_called_once_with(max_results=0)

    @patch('main.adapter')
    def test_list_jira_tickets_negative_max_result(self, mock_adapter):
        """Test ticket listing with negative max result."""
        mock_adapter.list_tickets.return_value = []
        
        result = list_jira_tickets(-1)
        
        mock_adapter.list_tickets.assert_called_once_with(max_results=-1)
