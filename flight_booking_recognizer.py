# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core import (
    Recognizer,
    RecognizerResult,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)

from config import DefaultConfig


class FlightBookingRecognizer(Recognizer):
    def __init__(
        self, configuration: DefaultConfig, telemetry_client: BotTelemetryClient = None
    ):
        self._recognizer = None

        # TODO
        # if configuration.LUIS_APP_ID:
        #     print(f"LUIS_APP_ID : {configuration.LUIS_APP_ID}")
        # if configuration.LUIS_API_KEY:
        #     print(f"LUIS_API_KEY : {configuration.LUIS_API_KEY}")
        # if configuration.LUIS_END_POINT:
        #     print(f"LUIS_END_POINT : {configuration.LUIS_END_POINT}")

        luis_is_configured = (
            configuration.LUIS_APP_ID
            and configuration.LUIS_API_KEY
            and configuration.LUIS_END_POINT
        )
        if luis_is_configured:
            print("Luis is configured.")
            # Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
            # More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
            luis_application = LuisApplication(
                configuration.LUIS_APP_ID,
                configuration.LUIS_API_KEY,
                configuration.LUIS_END_POINT,
            )

            options = LuisPredictionOptions()
            options.telemetry_client = telemetry_client or NullTelemetryClient()

            self._recognizer = LuisRecognizer(
                luis_application, prediction_options=options
            )
        else:
            print("Luis is not configured!")

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)
