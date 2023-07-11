from github import Github
from github import Auth
from dotenv import load_dotenv
import os
import requests

# load the environment variables from the .env file
load_dotenv()

# get the access token from the environment variables
access_token = os.environ["GITHUB_ACCESS_TOKEN"]

# using an access token
auth = Auth.Token(str(access_token))
headers = {"Authorization": f"Bearer {access_token}"}

# Public Web Github
g = Github(auth=auth)

#GraphQL query to extract the discussions with their comments, replies, date, category and author from summer-2023 repo in silverkeytech
query= '''
 {
    repository(owner: "silverkeytech", name: "summer-2023") {
      discussions(first: 43, orderBy: {field: UPDATED_AT, direction: DESC}) {
        totalCount
        nodes {
          id
          author {
            login
          }
          category {
            name
            id
          }
          bodyText
          comments(first: 100) {
            edges {
              node {
                id
                author {
                  login
                }
                bodyText
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

#getting current user
current_user= g.get_user()
print(current_user.name)

#getting SilverKey repo:
repo = g.get_repo("silverkeytech/summer-2023")
print(repo)


# send the GraphQL request
response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
response.raise_for_status()

# parse the response
data = response.json()["data"]
discussions = data["repository"]["discussions"]["nodes"]


# print the first 5 discussions
for discussion in discussions[:5]:
    print(f"Discussion ID: {discussion['id']}")
    print(f"Author: {discussion['author']['login']}")
    print(f"Category: {discussion['category']['name']}")
    print(f"Body: {discussion['bodyText']}")
    print(f"Created At: {discussion['createdAt']}")
    print(f"Last Edited At: {discussion['lastEditedAt']}")
    print("Comments:")

    # print the comments for the discussion
    for comment in discussion["comments"]["edges"]:
        comment_node = comment["node"]
        print(f"\tComment ID: {comment_node['id']}")
        print(f"\tAuthor: {comment_node['author']['login']}")
        print(f"\tBody: {comment_node['bodyText']}")
        print(f"\tCreated At: {comment_node['createdAt']}")
        print(f"\tLast Edited At: {comment_node['lastEditedAt']}")
        print("\tReplies:")

        # print the replies for the comment
        for reply in comment_node["replies"]["nodes"]:
            print(f"\t\tAuthor: {reply['author']['login']}")
            print(f"\t\tBody: {reply['bodyText']}")
            print(f"\t\tCreated At: {reply['createdAt']}")
            print(f"\t\tUpdated At: {reply['updatedAt']}")
            print()

        print()
    print("=" * 50)