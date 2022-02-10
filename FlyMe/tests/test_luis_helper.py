import asyncio
import json
import pathlib
import sys
from http import HTTPStatus

current = pathlib.Path(__file__).parent.parent
sys.path.append(str(current))

import aiounittest
import pytest
from adapter_with_error_handler import AdapterWithErrorHandler
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient

# from email_prompt import EmailPrompt
from botbuilder.community.dialogs.prompts import EmailPrompt
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    MessageFactory,
    TurnContext,
    UserState,
)
from botbuilder.core.adapters import TestAdapter
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.dialogs.prompts import (
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.integration.applicationinsights.aiohttp import (
    AiohttpTelemetryProcessor,
    bot_telemetry_middleware,
)
from botbuilder.schema import Activity, ActivityTypes, Attachment
from bots import DialogAndWelcomeBot
from config import DefaultConfig
from dialogs import BookingDialog, MainDialog
from dialogs.booking_dialog import BookingDialog

from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import Intent, LuisHelper

from botbuilder.testing import DialogTestClient


CONFIG = DefaultConfig()
# SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
# MEMORY = MemoryStorage()
# USER_STATE = UserState(MEMORY)
# CONVERSATION_STATE = ConversationState(MEMORY)
# ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY,
    telemetry_processor=AiohttpTelemetryProcessor(),
    client_queue_size=10,
)
TELEMETRY_CLIENT.track_trace("Starting bot")
HISTORY = []
RECOGNIZER = FlightBookingRecognizer(CONFIG, TELEMETRY_CLIENT)
BOOKING_DIALOG = BookingDialog(HISTORY)
DIALOG = MainDialog(
    RECOGNIZER, BOOKING_DIALOG, HISTORY, telemetry_client=TELEMETRY_CLIENT
)

testClient = DialogTestClient("test", DIALOG)


class Test_LuisHelper(aiounittest.AsyncTestCase):
    async def test_execute_luis_query(self):

        reply = await testClient.send_activity("hi")

        self.assertEqual(reply.text, "What can I help you with today?")

        reply = await testClient.send_activity(
            "i'm looking to go to brasilia from Paris between september"
            " 30 and october 4 for a budget of 1000$"
        )

        self.assertEqual(
            reply.text,
            "Please confirm, I have you traveling to: Brasilia from: "
            "Paris on: 2022-09-30 return: 2022-10-04 with a budget of "
            "1000 $. (1) Yes or (2) No",
        )

        reply = await testClient.send_activity("Yes")

        self.assertEqual(
            reply.text,
            "I have you booked to Brasilia from Paris on 2022-09-30 return on 2022-10-04 with a budget of 1000 $",
        )
