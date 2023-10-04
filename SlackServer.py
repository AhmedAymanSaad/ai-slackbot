from typing import Union
from fastapi import FastAPI, Request, Response
from Classes.SlackClass import SlackClass

Server = FastAPI()

slackApp = SlackClass()

@slackApp.app.event("app_mention")
def HandleMentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]

    ts = body["event"]["ts"]
    channel = body["event"]["channel"]

    mention = f"<@{slackApp.SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    response = slackApp.MyFunction(text)
    slackApp.client.chat_postMessage(
            channel=channel,
            thread_ts=ts,
            text=response
        )
    #say(response)

@slackApp.app.event("events")
def HandleEvents(body, say):
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    return slackApp.handler.handle(body)

@Server.post("/slack/events")
async def SlackEvents(request: Request):
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    print("Received request")
    return await slackApp.handler.handle(request)

@Server.get("/")
async def Root():
    """
    Route for the root path.
    This function returns a simple message.

    Returns:
        str: The message.
    """
    return "Hello World!"
