import aiounittest
from botbuilder.testing import DialogTestClient
from config import DefaultConfig
from dialogs import BookingDialog, MainDialog
from flight_booking_recognizer import FlightBookingRecognizer


class Test_LuisHelper(aiounittest.AsyncTestCase):
    async def test_requdialogsest(self):
        history = []
        recognizer = FlightBookingRecognizer(DefaultConfig())
        booking_dialog = BookingDialog(history)
        dialog = MainDialog(recognizer, booking_dialog, history)
        testClient = DialogTestClient("test", dialog)

        reply = await testClient.send_activity("hi")
        print(f"history : {history}")
        self.assertEqual(reply.text, "What can I help you with today?")

        reply = await testClient.send_activity(
            "i'm looking to go to brasilia from Paris between september"
            " 30 and october 4 for a budget of 1000$"
        )
        print(f"history : {history}")
        self.assertEqual(
            reply.text,
            "Please confirm, I have you traveling to: Brasilia from: "
            "Paris on: 2022-09-30 return: 2022-10-04 with a budget of "
            "1000 $. (1) Yes or (2) No",
        )

        reply = await testClient.send_activity("Yes")
        print(f"history : {history}")
        self.assertEqual(
            reply.text,
            "I have you booked to Brasilia from Paris on 2022-09-30 "
            "return on 2022-10-04 with a budget of 1000 $",
        )

        reply = testClient.get_next_reply()
        print(f"history : {history}")
        self.assertEqual(reply.text, "What else can I do for you?")

    async def test_prompt(self):
        history = []
        recognizer = FlightBookingRecognizer(DefaultConfig())
        booking_dialog = BookingDialog(history)
        dialog = MainDialog(recognizer, booking_dialog, history)
        testClient = DialogTestClient("test", dialog)

        reply = await testClient.send_activity("hi")
        self.assertEqual(reply.text, "What can I help you with today?")

        reply = await testClient.send_activity("I want to travel for a budget of 500")
        self.assertEqual(reply.text, "To what city would you like to travel?")

        reply = await testClient.send_activity("London")
        self.assertEqual(reply.text, "From what city will you be travelling?")

        reply = await testClient.send_activity("Paris")
        self.assertEqual(reply.text, "On what date would you like to travel?")

        reply = await testClient.send_activity("on 01/01/2022")
        self.assertEqual(reply.text, "On what date would you like to return?")

        reply = await testClient.send_activity("on 10/01/2022")
        self.assertEqual(
            reply.text,
            "Please confirm, I have you traveling to: London from: Paris "
            "on: 2022-01-01 return: 2022-10-01 with a budget of 500. (1) Yes or (2) No",
        )

        reply = await testClient.send_activity("Yes")
        self.assertEqual(
            reply.text,
            "I have you booked to London from Paris on 2022-01-01 return on "
            "2022-10-01 with a budget of 500",
        )

        reply = testClient.get_next_reply()
        self.assertEqual(reply.text, "What else can I do for you?")

    async def test_cancel(self):
        history = []
        recognizer = FlightBookingRecognizer(DefaultConfig())
        booking_dialog = BookingDialog(history)
        dialog = MainDialog(recognizer, booking_dialog, history)
        testClient = DialogTestClient("test", dialog)

        reply = await testClient.send_activity("hello")
        self.assertEqual(reply.text, "What can I help you with today?")

        reply = await testClient.send_activity("I want to book a flight for Paris")
        self.assertEqual(reply.text, "From what city will you be travelling?")

        reply = await testClient.send_activity("London")
        self.assertEqual(
            reply.text, "What is your maximum budget for the total ticket price?"
        )

        reply = await testClient.send_activity("Cancel")
        self.assertEqual(reply.text, "Cancelling")

        reply = testClient.get_next_reply()
        self.assertEqual(reply.text, "What else can I do for you?")
