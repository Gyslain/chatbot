#%%
import pathlib
import sys

import aiounittest
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import AiohttpTelemetryProcessor
from botbuilder.testing import DialogTestClient

current = pathlib.Path(__file__).parent.parent
sys.path.append(str(current))

from config import DefaultConfig
from dialogs import BookingDialog, MainDialog
from flight_booking_recognizer import FlightBookingRecognizer


class Test_LuisHelper(aiounittest.AsyncTestCase):
    async def test_request1(self):
        CONFIG = DefaultConfig()
        HISTORY = []
        RECOGNIZER = FlightBookingRecognizer(CONFIG)
        BOOKING_DIALOG = BookingDialog(HISTORY)
        DIALOG = MainDialog(RECOGNIZER, BOOKING_DIALOG, HISTORY)
        testClient = DialogTestClient("test", DIALOG)

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
            "I have you booked to Brasilia from Paris on 2022-09-30 "
            "return on 2022-10-04 with a budget of 1000 $",
        )

        reply = testClient.get_next_reply()
        self.assertEqual(reply.text, "What else can I do for you?")

    async def test_request2(self):
        CONFIG = DefaultConfig()
        HISTORY = []
        RECOGNIZER = FlightBookingRecognizer(CONFIG)
        BOOKING_DIALOG = BookingDialog(HISTORY)
        DIALOG = MainDialog(RECOGNIZER, BOOKING_DIALOG, HISTORY)
        testClient = DialogTestClient("test", DIALOG)

        reply = await testClient.send_activity("hi")
        self.assertEqual(reply.text, "What can I help you with today?")

        reply = await testClient.send_activity("I want to travel for a budget of 500")
        self.assertEqual(reply.text, "To what city would you like to travel?")

        reply = await testClient.send_activity("to London")
        self.assertEqual(reply.text, "From what city will you be travelling?")

        reply = await testClient.send_activity("from Paris")
        self.assertEqual(reply.text, "On what date would you like to travel?")

        reply = await testClient.send_activity("on 01/01/2022")
        self.assertEqual(reply.text, "On what date would you like to return?")

        reply = await testClient.send_activity("on 10/01/2022")
        self.assertEqual(
            reply.text,
            "Please confirm, I have you traveling to: to London from: from Paris "
            "on: 2022-01-01 return: 2022-10-01 with a budget of 500. (1) Yes or (2) No",
        )

        reply = await testClient.send_activity("Yes")
        self.assertEqual(
            reply.text,
            "I have you booked to to London from from "
            "Paris on 2022-01-01 return on 2022-10-01 with a budget of 500",
        )

        reply = testClient.get_next_reply()
        self.assertEqual(reply.text, "What else can I do for you?")
