from abc import ABC, abstractmethod
from DB.Database import Database
import requests
from datetime import datetime, timezone
import pandas as pd
import concurrent.futures
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

class DataLogger(ABC):

    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def saveToDatabase(self, database: Database):
        pass

class GithubIssuesLogger(DataLogger):

    def __init__(self):
        access_token = os.getenv("GITHUB_ACCESS_TOKEN")
        username = os.getenv("GITHUB_USERNAME")
        repository = os.getenv("GITHUB_REPOSITORY")

        base_url = os.getenv("GITHUB_BASE_URL")
        headers = {
        "Authorization": f"token {access_token}"
        }
        lastUpdated = os.getenv("GITHUB_LAST_UPDATED")
        url = f"{base_url}/repos/{username}/{repository}/issues?state=all&since={lastUpdated}" if lastUpdated else f"{base_url}/repos/{username}/{repository}/issues?state=all"

    def getIssues(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get issues. Error: {e}")
            return None
        
        if response.status_code == 200:
            issues = response.json()
            lastUpdated = datetime.now(timezone.utc)
            return issues
        else:
            print(f"Failed to get issues. Status code: {response.status_code}")
            return None   
        
    def getIssueComments(self, issue : list[dict]):
        issueUrl = issue["comments_url"]
        try:
            response = requests.get(issueUrl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get issue comments. Error: {e}")
            return None
        
        if response.status_code == 200:
            comments = response.json()
            return comments
        else:
            print(f"Failed to get issue comments. Status code: {response.status_code}")
            return None
        
    def cleanComments(self, comments : list[dict]):
        df = pd.DataFrame(comments)
        df["user"] = df["user"].apply(lambda x: x["login"])
        cleanedComments = df[["body", "user", "created_at"]].to_dict("records")
        return cleanedComments
    
    def getIssueComments(self, issue : dict):
        issueUrl = issue["comments_url"]
        try:
            response = requests.get(issueUrl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get issue comments. Error: {e}")
            return None
        
        if response.status_code == 200:
            comments = response.json()
            return comments
        else:
            print(f"Failed to get issue comments. Status code: {response.status_code}")
            return None
    
    def cleanIssues(self, issues : list[dict]):
        df = pd.DataFrame(issues)
        df["user"] = df["user"].apply(lambda x: x["login"])
        cleanedIssues = df[["title", "body", "user", "created_at", "number", "state", "labels", "comments", "comment_data"]].to_dict("records")
        return cleanedIssues

    def process_issue(self, issue : dict):
        comments = self.getIssueComments(issue)
        if comments:
            issue["comment_data"] = self.cleanComments(comments)
        else:
            issue["comment_data"] = []

    def getIssuesCommentsParallel(self, issues : list[dict]):
        with concurrent.futures.ThreadPoolExecutor(maxWorkers=32) as executor:
            futures = [executor.submit(self.process_issue, issue) for issue in issues]

            for future in concurrent.futures.as_completed(futures):
                pass  # We are just waiting for all tasks to complete

        issues = self.cleanIssues(self, issues)
        return issues
    
    def getData(self):
        issues = self.getIssues()
        if issues:
            issues = self.getIssuesCommentsParallel(issues)
            return issues
        else:
            return None
    
    def saveToDatabase(self, database: Database):
        issues = self.getData()
        if issues:
            database.insert_documents("issues", issues)
            print("Issues saved to database.")
        else:
            print("Failed to save issues to database.")