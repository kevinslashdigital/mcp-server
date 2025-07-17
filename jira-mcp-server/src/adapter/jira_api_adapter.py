import os
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Optional, Dict

class JiraApiAdapter:
    def __init__(self):
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
        self.base_url = f"https://{os.getenv('JIRA_DOMAIN')}/rest/api/3"
        self.auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        

    def create_ticket(self, summary: str, description_text: str) -> str:
        """Creates a new Jira issue in the configured project.

        Args:
            summary (str): The title or summary of the issue.
            description_text (str): A plain-text description of the issue.

        Returns:
        str: The key of the created Jira issue (e.g., "ABC-123").
        """
        url = f"{self.base_url}/issue"
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description_text}]
                    }]
                },
                "issuetype": {"name": "Task"}
            }
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code == 201:
            issue_key = response.json()["key"]
            return f"ticket {issue_key} is successfully created"
        else:
            print(response.text)
            raise Exception(f"Error creating ticket with status code {response.status_code}")


    def update_ticket(self, issue_key: str, summary: str, description_text: str):
        """
        Updates the fields of an existing Jira issue.

        Args:
            issue_key (str): The key of the issue to update (e.g., "PROJ-123").
            summary (str): The title update.
            description_text (str): The description to update.
        """
        url = f"{self.base_url}/issue/{issue_key}"
        payload = {
            "fields": {
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "text", "text": description_text} ]
                }
            }
        }

        response = requests.put(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code == 204:
            return "ticket is successfully updated"
        else:
            print(response.text)
            raise(f"Error updating ticket {response.status_code}")


    def list_tickets(self, max_results=10) -> List[Optional[Dict]]:
        """
        Retrieves a list of Jira issues matching a JQL query.

        Args:
            jql (str, optional): A JQL (Jira Query Language) string to filter issues. Defaults to current project.
            max_results (int, optional): Maximum number of issues to retrieve. Defaults to 10.

        Returns:
            list: A list of issue objects returned by the Jira API.
                None if the request fails.
        """
        url = f"{self.base_url}/search"
        params = {
            "jql": f"project={self.project_key}",
            "maxResults": max_results
        }

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        if response.status_code == 200:
            issues = response.json()["issues"]
            for issue in issues:
                print(f"{issue['key']}: {issue['fields']['summary']}")
            return issues
        else:
            print(response.text)
            raise(f"Error listing tickets {response.status_code}")


    def transition_ticket(self, issue_key: str, transition_id: str):
        """
        Transitions a Jira issue to a new status using a transition ID.

        Args:
            issue_key (str): The key of the issue to transition.
            transition_id (str): The ID of the transition to apply.
        """
        url = f"{self.base_url}/issue/{issue_key}/transitions"
        payload = {"transition": {"id": transition_id}}

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code == 204:
            return "Ticket status is successfully updated"
        else:
            print(response.text)
            raise(f"Error transitioning ticket {response.status_code}")


    def get_transitions(self, issue_key: str) -> List[Optional[Dict]]:
        """
        Retrieves the list of available transitions for a given Jira issue.

        Args:
            issue_key (str): The key of the issue for which to get transitions.

        Returns:
            list: A list of available transitions (each as a dict with id and name).
                None if the request fails.
        """
        url = f"{self.base_url}/issue/{issue_key}/transitions"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        if response.status_code == 200:
            transitions = response.json()["transitions"]
            for t in transitions:
                print(f"{t['id']}: {t['name']}")
            return transitions
        else:
            print(response.text)
            raise Exception(f"Error getting transitions {response.status_code}")


    def add_comment(self, issue_key: str, comment: str) -> str:
        """
        Adds a comment to a specified Jira issue.

        Args:
            issue_key (str): The key of the issue to comment on.
            comment (str): The comment text to add.
        
        Return:
            success or error information regarding comment creation
        """
        url = f"{self.base_url}/issue/{issue_key}/comment"
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }]
            }
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code == 201:
            return "Comment is successfully added"
        else:
            print(response.text)
            raise Exception(f"Error adding comment {response.status_code}")