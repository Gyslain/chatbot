# FlyMe

![FlyMe logo](https://user.oc-static.com/upload/2019/10/24/15719199766568_Capture%20d%E2%80%99e%CC%81cran%202019-10-24%20a%CC%80%2014.14.41.png)

Chatbot which help to book flights.

This bot has been created using [Bot Framework](https://dev.botframework.com), it shows how to:

- Use [LUIS](https://www.luis.ai) to implement core AI capabilities
- Implement a multi-turn conversation using Dialogs
- Handle user interruptions for such things as `Help` or `Cancel`
- Prompt for and validate requests for information from the user
- Use [Application Insights](https://docs.microsoft.com/azure/azure-monitor/app/cloudservices) to monitor your bot

## Prerequisites

This sample **requires** prerequisites in order to run.

### Overview

This bot uses [LUIS](https://www.luis.ai), an AI based cognitive service, to implement language understanding
and [Application Insights](https://docs.microsoft.com/azure/azure-monitor/app/cloudservices), an extensible Application Performance Management (APM) service for web developers on multiple platforms.

### LUIS Application to enable language understanding

This chat bot uses the LUIS Application to understand the customer request.

To connect the chat bot to LUIS Application, you have to specify the following environnement variable in a .env file :

- Application ID: "LUIS_APP_ID"
- Key: "LUIS_AUTHORING_KEY"
- Endpoint url: "LUIS_AUTHORING_END_POINT"

### Add Application Insights service to enable the bot monitoring

This appication also use the Azure Insight Instrumentation. To connect the bot to Insight, you have to define the following variable :

- Insight key: "APPINSIGHTS_INSTRUMENTATION_KEY"

Application Insights resource creation steps can be found [here](https://docs.microsoft.com/azure/azure-monitor/app/create-new-resource).

## To try this chat bot

- In the terminal, type `pip install -r requirements.txt`
- Run your bot with `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the latest Bot Framework Emulator from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- File -> Open Bot
- Enter a Bot URL of `http://localhost:3978/api/messages`

