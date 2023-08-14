from typing import Union
from fastapi import FastAPI
from Classes.SlackClass import SlackClass

Server = FastAPI()

slackApp = SlackClass()

@SlackApp.app.event("app_mention")
def HandleMentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]

    mention = f"<@{slackApp.SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    response = slackApp.MyFunction(text)
    say(response)

@Server.post("/slack/events")
async def SlackEvents():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    request = await request.body()
    return slackApp.handler.handle(request)
