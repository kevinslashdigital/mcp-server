import uvicorn
from mcp.server.fastmcp import FastMCP
from adapter.jira_api_adapter import JiraApiAdapter
from typing import List, Optional, Dict

mcp = FastMCP(
    name="Jira Adapter MCP Server",
    instructions="A jira adapter server to list, create, update, and change status from slash jira"
)

adapter = JiraApiAdapter()

@mcp.tool()
def create_jira_ticket(title: str, description: str) -> str:
    """
    Call jira api adapter to create ticket

    Args:
        title (str): The summary/title of the Jira issue.
        description (str): The body content of the Jira issue in plain text.

    Returns:
        str: The key of the created Jira issue (e.g., "ABC-123") or error.
    """
    try:
        return adapter.create_ticket(title=title, description_text=description)
    except Exception as e:
        return f"Error creating jira ticket: {str(e)}"

@mcp.tool()
def update_jira_ticket(issue_key: str, title: str, description: str) -> str:
    """
    Call jira api adapter to update ticket

    Args:
        issue_key(str): the issue identifier
        title (str): The title to update.
        description (str): The description to update.
    
    Return:
        str: Success message or error message if exception raised
    """
    
    try:
        return adapter.update_ticket(issue_key=issue_key, summary=title, description_text=description)
    except Exception as e:
        return f"Error updating jira ticket: {str(e)}"

@mcp.tool()
def list_jira_tickets(max_result: int) -> List[Optional[Dict]]:
    """
    Call jira api adapter to list tickets

    Args:
        max_result(int): the max number of tickets to be fetched

    Return:
        list: A list of issue objects returned by the Jira API. None if the request fails.
    """
    
    try:
        return adapter.list_tickets(max_results=max_result)
    except Exception:
        return None
    
@mcp.tool()
def list_jira_statuses(ticket_no: str) -> List[Optional[Dict]]:
    """
    Call jira api adapter to list available transitions

    Args:
        ticket_no(str): Ticket Number
    
    Return:
        list: A list of statuses returned by the Jira API. None if the request fails.
    """
    try:
        return adapter.get_transitions(ticket_no)
    except Exception:
        return None

@mcp.tool()
def update_jira_status(ticket_no: str, status: str) -> str:
    """
    Call jira api adapter to do transition of issue

    Args:
        ticket_no(str): The ticket number
        status(str): Status to update

    Return:
        str: Success or Error of transitioning status or None if exception raised.
    """
    try:
        transitions = adapter.get_transitions(ticket_no)
        filtered_transitions = [t for t in transitions if t["name"] == status]
        if filtered_transitions:
            return adapter.transition_ticket(ticket_no, filtered_transitions[0]["id"])
        else:
            return "Status is unknown"
    except Exception:
        return None

@mcp.tool()
def add_comment_to_jira_ticket(ticket_no: str, comment: str) -> str:
    """
    Call jira api adapter to add comment to specified jira ticket

    Args:
        ticket_no(str): the ticket number
        comment (str): The comment body.
    Return:
        str: Success or Error of adding comment to jira ticket or None if exception raised.
    """
    try:
        return adapter.add_comment(issue_key=ticket_no, comment=comment)
    except Exception:
        return None

if __name__ == "__main__":
    # For SSE transport (HTTP server)
    print("🚀 Starting MCP server with SSE transport...")
    print("📡 Server will be available at: http://localhost:9999")
    print("📡 Your MCP endpoint: http://localhost:9999/sse")
    app = mcp.sse_app
    uvicorn.run(app, host="0.0.0.0", port=9999)