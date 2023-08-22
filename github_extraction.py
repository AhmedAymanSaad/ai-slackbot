from github import Github
from github import Auth
from dotenv import load_dotenv
import os
import requests
import csv

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
      discussions(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
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
print(response.json())
data = response.json()["data"]
discussions = data["repository"]["discussions"]["nodes"]
total_count = data["repository"]["discussions"]["totalCount"]
has_next_page = data["repository"]["discussions"]["pageInfo"]["hasNextPage"]
end_cursor = data["repository"]["discussions"]["pageInfo"]["endCursor"]


#The dataset could look like this:
# Discussion ID    CommentID    Author      Category    Body     Created At     Last Edited At   
# where the commentID can be null if its the first starting discussion
# 


# iterate through all pages of discussions
while has_next_page:
    # update query with new endCursor to get next page of data
    query = query.replace(f'after: {end_cursor}', f'after: "{end_cursor}"')
    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    response.raise_for_status()
    
    # parse the response
    data = response.json()["data"]
    discussions += data["repository"]["discussions"]["nodes"]
    has_next_page = data["repository"]["discussions"]["pageInfo"]["hasNextPage"]
    end_cursor = data["repository"]["discussions"]["pageInfo"]["endCursor"]

# iterate through all discussions and their comments
i=0
with open('discussions_dataset.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Discussion_ID", "Discussion_Title", "Comment_ID", "Author", "Category", "Markup_Body", "Body" ,"Created At", "Last Edited At"])

    for discussion in discussions:
        print(i)
        discussion_id = discussion["id"]
        dis_author = discussion["author"]["login"]
        dis_title= discussion["title"]
        category = discussion["category"]["name"]
        dis_body = discussion["body"]
        dis_bodyText = discussion["bodyText"]
        dis_created_at = discussion["createdAt"]
        dis_last_edited_at = discussion["lastEditedAt"]

        # write the initial post as a comment with Comment ID set to NULL
        writer.writerow([discussion_id, dis_title ,None, dis_author, category, dis_body, dis_bodyText, dis_created_at, dis_last_edited_at])

        # iterate through all comments for the discussion
        has_next_page = discussion["comments"]["pageInfo"]["hasNextPage"]
        end_cursor = discussion["comments"]["pageInfo"]["endCursor"]
        for comment in discussion["comments"]["edges"]:
            comment_node = comment["node"]
            comment_id = comment_node["id"]
            comm_author = comment_node["author"]["login"]
            comm_body = comment_node["body"]
            comm_bodyText = comment_node["bodyText"]
            comm_created_at = comment_node["createdAt"]
            comm_last_edited_at = comment_node["lastEditedAt"]

            # write the comment to the CSV file
            writer.writerow([discussion_id, dis_title, comment_id, comm_author, category, comm_body,comm_bodyText, comm_created_at, comm_last_edited_at])
        i=i+1

 


