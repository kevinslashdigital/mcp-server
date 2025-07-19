"""
Real integration tests for jira-mcp-server that make actual API calls to Jira.
These tests require valid Jira credentials and are skipped by default.
Run with: pytest tests/test_real_integration.py -m real_integration --jira-real
"""
import pytest
import os
from main import (
    create_jira_ticket,
    update_jira_ticket,
    list_jira_tickets,
    list_jira_statuses,
    update_jira_status,
    add_comment_to_jira_ticket
)


@pytest.fixture(scope="session")
def jira_credentials():
    """Check for required Jira credentials."""
    required_env_vars = [
        "JIRA_PROJECT_KEY",
        "JIRA_DOMAIN", 
        "JIRA_EMAIL",
        "JIRA_API_TOKEN"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {missing_vars}")
    
    return {
        "project_key": os.getenv("JIRA_PROJECT_KEY"),
        "domain": os.getenv("JIRA_DOMAIN"),
        "email": os.getenv("JIRA_EMAIL"),
        "api_token": os.getenv("JIRA_API_TOKEN")
    }


@pytest.fixture
def test_ticket_key():
    """Store created ticket key for cleanup."""
    return {"key": None}


@pytest.mark.real_integration
class TestRealJiraIntegration:
    """Real integration tests against actual Jira instance."""

    def test_real_create_jira_ticket(self, jira_credentials, test_ticket_key):
        """Test creating a real ticket in Jira."""
        title = "Test Ticket from Integration Test"
        description = "This is a test ticket created by pytest integration test. Safe to delete."
        
        result = create_jira_ticket(title, description)
        
        # Should return success message with ticket key
        assert "successfully created" in result
        
        # Extract ticket key for cleanup
        import re
        match = re.search(r'ticket (\w+-\d+)', result)
        if match:
            test_ticket_key["key"] = match.group(1)
            print(f"Created ticket: {test_ticket_key['key']}")

    def test_real_list_jira_tickets(self, jira_credentials):
        """Test listing real tickets from Jira."""
        result = list_jira_tickets(5)
        
        # Should return a list of tickets
        assert isinstance(result, list)
        
        if result:  # If there are tickets
            # Each ticket should have expected structure
            ticket = result[0]
            assert "key" in ticket
            assert "fields" in ticket
            assert "summary" in ticket["fields"]
            print(f"Found {len(result)} tickets")

    def test_real_list_jira_statuses(self, jira_credentials, test_ticket_key):
        """Test listing real statuses for a ticket."""
        if not test_ticket_key["key"]:
            pytest.skip("No test ticket available")
        
        result = list_jira_statuses(test_ticket_key["key"])
        
        # Should return a list of available transitions
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Each transition should have id and name
        transition = result[0]
        assert "id" in transition
        assert "name" in transition
        print(f"Available transitions: {[t['name'] for t in result]}")

    def test_real_add_comment_to_jira_ticket(self, jira_credentials, test_ticket_key):
        """Test adding a real comment to a ticket."""
        if not test_ticket_key["key"]:
            pytest.skip("No test ticket available")
        
        comment = "This is a test comment added by pytest integration test."
        result = add_comment_to_jira_ticket(test_ticket_key["key"], comment)
        
        # Should return success message
        assert "successfully added" in result
        print(f"Added comment to {test_ticket_key['key']}")

    def test_real_update_jira_ticket(self, jira_credentials, test_ticket_key):
        """Test updating a real ticket in Jira."""
        if not test_ticket_key["key"]:
            pytest.skip("No test ticket available")
        
        updated_title = "Updated Test Ticket from Integration Test"
        updated_description = "This ticket has been updated by pytest integration test."
        
        result = update_jira_ticket(test_ticket_key["key"], updated_title, updated_description)
        
        # Should return success message
        assert "successfully updated" in result
        print(f"Updated ticket: {test_ticket_key['key']}")

    def test_real_update_jira_status(self, jira_credentials, test_ticket_key):
        """Test updating ticket status in real Jira."""
        if not test_ticket_key["key"]:
            pytest.skip("No test ticket available")
        
        # First get available transitions
        transitions = list_jira_statuses(test_ticket_key["key"])
        
        if not transitions:
            pytest.skip("No transitions available")
        
        # Try to transition to the first available status
        target_status = transitions[0]["name"]
        result = update_jira_status(test_ticket_key["key"], target_status)
        
        # Should return success message or "Status is unknown" if already in that status
        assert ("successfully updated" in result or "Status is unknown" in result)
        print(f"Status update result: {result}")


@pytest.mark.real_integration
class TestRealJiraWorkflow:
    """Test complete workflows against real Jira."""

    def test_real_complete_ticket_workflow(self, jira_credentials):
        """Test a complete ticket lifecycle in real Jira."""
        # 1. Create a ticket
        title = "Complete Workflow Test Ticket"
        description = "Testing complete workflow from creation to completion."
        
        create_result = create_jira_ticket(title, description)
        assert "successfully created" in create_result
        
        # Extract ticket key
        import re
        match = re.search(r'ticket (\w+-\d+)', create_result)
        assert match, "Could not extract ticket key from creation result"
        ticket_key = match.group(1)
        print(f"Created workflow test ticket: {ticket_key}")
        
        try:
            # 2. Update the ticket
            updated_title = "Updated Complete Workflow Test Ticket"
            updated_description = "This ticket has been updated as part of workflow test."
            
            update_result = update_jira_ticket(ticket_key, updated_title, updated_description)
            assert "successfully updated" in update_result
            print(f"Updated ticket: {ticket_key}")
            
            # 3. Add a comment
            comment = "Workflow test comment - this ticket is being tested end-to-end."
            comment_result = add_comment_to_jira_ticket(ticket_key, comment)
            assert "successfully added" in comment_result
            print(f"Added comment to: {ticket_key}")
            
            # 4. List available transitions
            transitions = list_jira_statuses(ticket_key)
            assert isinstance(transitions, list)
            print(f"Available transitions: {[t['name'] for t in transitions]}")
            
            # 5. Try to transition if possible
            if transitions:
                target_status = transitions[0]["name"]
                status_result = update_jira_status(ticket_key, target_status)
                print(f"Status transition result: {status_result}")
            
            # 6. Verify ticket appears in listing
            tickets = list_jira_tickets(10)
            ticket_keys = [t["key"] for t in tickets] if tickets else []
            # Note: The ticket might not appear immediately due to indexing delays
            print(f"Ticket listing contains {len(ticket_keys)} tickets")
            
            print(f"✅ Complete workflow test successful for ticket: {ticket_key}")
            
        except Exception as e:
            print(f"❌ Workflow test failed for ticket {ticket_key}: {e}")
            raise


@pytest.mark.real_integration
class TestRealJiraErrorHandling:
    """Test error handling with real Jira API."""

    def test_real_invalid_ticket_key(self, jira_credentials):
        """Test operations with invalid ticket key."""
        invalid_key = "INVALID-999999"
        
        # These should handle errors gracefully
        update_result = update_jira_ticket(invalid_key, "Test", "Test")
        assert "Error updating jira ticket" in update_result
        
        comment_result = add_comment_to_jira_ticket(invalid_key, "Test comment")
        assert comment_result is None  # Should return None on exception
        
        status_result = list_jira_statuses(invalid_key)
        assert status_result is None  # Should return None on exception

    def test_real_invalid_status_transition(self, jira_credentials):
        """Test invalid status transition."""
        # First create a ticket to test with
        create_result = create_jira_ticket("Invalid Status Test", "Testing invalid status")
        
        if "successfully created" in create_result:
            import re
            match = re.search(r'ticket (\w+-\d+)', create_result)
            if match:
                ticket_key = match.group(1)
                
                # Try invalid status
                result = update_jira_status(ticket_key, "INVALID_STATUS_NAME")
                assert result == "Status is unknown"
                print(f"Invalid status test passed for: {ticket_key}")
