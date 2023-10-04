import csv
from dotenv import load_dotenv
from github import Auth
from github import Github
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

    def getIssueComments(self, issue: list[dict]):
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
            print(
                f"Failed to get issue comments. Status code: {response.status_code}")
            return None

    def cleanComments(self, comments: list[dict]):
        df = pd.DataFrame(comments)
        df["user"] = df["user"].apply(lambda x: x["login"])
        cleanedComments = df[["body", "user", "created_at"]].to_dict("records")
        return cleanedComments

    def getIssueComments(self, issue: dict):
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
            print(
                f"Failed to get issue comments. Status code: {response.status_code}")
            return None

    def cleanIssues(self, issues: list[dict]):
        df = pd.DataFrame(issues)
        df["user"] = df["user"].apply(lambda x: x["login"])
        cleanedIssues = df[["title", "body", "user", "created_at", "number",
                            "state", "labels", "comments", "comment_data"]].to_dict("records")
        return cleanedIssues

    def process_issue(self, issue: dict):
        comments = self.getIssueComments(issue)
        if comments:
            issue["comment_data"] = self.cleanComments(comments)
        else:
            issue["comment_data"] = []

    def getIssuesCommentsParallel(self, issues: list[dict]):
        with concurrent.futures.ThreadPoolExecutor(maxWorkers=32) as executor:
            futures = [executor.submit(self.process_issue, issue)
                       for issue in issues]

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


class GithubDailyDiscussion():

    def __init__(self) -> None:
        self.access_token = "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"
        # using an access token
        self.auth = Auth.Token(str(self.access_token))
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        # Public Web Github
        self.g = Github(auth=self.auth)

    def getContext(self, day):
        day = int(day) + 1
        self.query = '''
        {
            repository(owner: "silverkeytech", name: "summer-2023") {
              discussions(first: day, orderBy: {field: CREATED_AT, direction: DESC}) {
                totalCount
                pageInfo {
                hasNextPage
                endCursor
              }
                nodes {
                  id
                  title
                  author {
                    login
                  }
                  category {
                    name
                    id
                  }
                  bodyText
                  body
                  comments(first: 100) {
                  pageInfo {
                hasNextPage
                endCursor
              }
                    edges {
                      node {
                        id
                        author {
                          login
                        }
                        bodyText
                        body
                        replies(first: 10) {
                          nodes {
                            author {
                              login
                            }
                            bodyText
                            updatedAt
                            createdAt
                          }
                        }
                        createdAt
                        lastEditedAt
                      }
                    }
                  }
                  lastEditedAt
                  createdAt
                }
              }
            }
          }
        '''
        self.query = self.query.replace("day", str(day))
        self.current_user= self.g.get_user()
        repo = self.g.get_repo("silverkeytech/summer-2023")
        
        response = requests.post("https://api.github.com/graphql", json={"query": self.query}, headers=self.headers)
        response.raise_for_status()
        data = response.json()["data"]
        discussions = data["repository"]["discussions"]["nodes"]
        total_count = data["repository"]["discussions"]["totalCount"]
        has_next_page = data["repository"]["discussions"]["pageInfo"]["hasNextPage"]
        end_cursor = data["repository"]["discussions"]["pageInfo"]["endCursor"]

        df = pd.DataFrame(columns=["Discussion_ID", "Discussion_Title", "Comment_ID", "Author", "Category", "Markup_Body", "Body" ,"Created At", "Last Edited At"])

        i=0
        discussions = [discussions[-1]]
        for discussion in discussions:
          discussion_id = discussion["id"]
          dis_author = discussion["author"]["login"]
          dis_title= discussion["title"]
          category = discussion["category"]["name"]
          dis_body = discussion["body"]
          dis_bodyText = discussion["bodyText"]
          dis_created_at = discussion["createdAt"]
          dis_last_edited_at = discussion["lastEditedAt"]
          has_next_page = discussion["comments"]["pageInfo"]["hasNextPage"]
          end_cursor = discussion["comments"]["pageInfo"]["endCursor"]
          
          # df = df.append({"Discussion_ID": discussion_id, "Discussion_Title": dis_title, "Comment_ID": None, "Author": dis_author, "Category": category, "Markup_Body": dis_body, "Body": dis_bodyText, "Created At": dis_created_at, "Last Edited At": dis_last_edited_at}, ignore_index=True)
          df.loc[len(df)] = [discussion_id, dis_title, None, dis_author, category, dis_body, dis_bodyText, dis_created_at, dis_last_edited_at]
          for comment in discussion["comments"]["edges"]:
              comment_node = comment["node"]
              comment_id = comment_node["id"]
              comm_author = comment_node["author"]["login"]
              comm_body = comment_node["body"]
              comm_bodyText = comment_node["bodyText"]
              comm_created_at = comment_node["createdAt"]
              comm_last_edited_at = comment_node["lastEditedAt"]
              # df = df.append({"Discussion_ID": discussion_id, "Discussion_Title": dis_title, "Comment_ID": comment_id, "Author": comm_author, "Category": category, "Markup_Body": comm_body, "Body": comm_bodyText, "Created At": comm_created_at, "Last Edited At": comm_last_edited_at}, ignore_index=True)
              df.loc[len(df)] = [discussion_id, dis_title, comment_id, comm_author, category, comm_body, comm_bodyText, comm_created_at, comm_last_edited_at] 

          i = i+1
          break
        df = df.drop(columns=["Body"])
        df = df.drop(columns=["Discussion_ID"])
        df = df.drop(columns=["Comment_ID"])
        df = df.drop(columns=["Discussion_Title"])
        df = df.drop(columns=["Category"])
        df = df.drop(columns=["Created At"])
        df = df.drop(columns=["Last Edited At"])
        return df.to_string(index=True, header=True)

