# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails
import dateutil.parser as dparser


class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "NoneIntent"


class Entities(Enum):
    TO_CITY = "dst_city"
    FROM_CITY = "or_city"
    START_DATE = "str_date"
    END_DATE = "end_date"
    MAX_DURATION = "max_duration"
    BUDGET = "budget"
    N_ADULTS = "n_adults"
    N_CHILDREN = "n_children"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:

                print(f"Intent : {intent}")
                # TODO ici on reccupere les entities

                result = BookingDetails()

                # TO_CITY
                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_city = recognizer_result.entities.get("$instance", {}).get(
                    Entities.TO_CITY.value, []
                )
                print(f"to_city : {to_city}")
                # [{'startIndex': 20, 'endIndex': 25, 'text': 'paris', 'type': 'dst_city', 'score': 0.9992835}]
                if len(to_city) > 0:
                    if recognizer_result.entities.get(
                        Entities.TO_CITY.value, [{"$instance": {}}]
                    )[0]:
                        result.destination = to_city[0]["text"].capitalize()
                        print(f"result.destination={result.destination}")
                    else:
                        result.unsupported_airports.append(
                            to_city[0]["text"].capitalize()
                        )

                # FROM_CITY
                from_city = recognizer_result.entities.get("$instance", {}).get(
                    Entities.FROM_CITY.value, []
                )
                print(f"from_city : {from_city}")
                if len(from_city) > 0:
                    if recognizer_result.entities.get(
                        Entities.FROM_CITY.value, [{"$instance": {}}]
                    )[0]:
                        result.origin = from_city[0]["text"].capitalize()
                        print(f"result.origin={result.origin}")
                    else:
                        result.unsupported_airports.append(
                            from_city[0]["text"].capitalize()
                        )

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                start_date = recognizer_result.entities.get(
                    Entities.START_DATE.value, []
                )
                print(f"start_date : {start_date}")

                # from botbuilder.dialogs.prompts import (
                # DateTimePrompt,
                # PromptValidatorContext,
                # PromptOptions,
                # DateTimeResolution,
                # )
                # if "definite" in Timex(timex).types:
                # return "definite" in Timex(timex).types
                from datatypes_date_time.timex import Timex

                # timex_property = Timex(timex)
                # # time_property = Timex(result.start_date)
                # DateTimeResolution(timex=timex)

                if start_date:
                    timex = start_date[0]
                    if timex:
                        datetime = dparser.parse(timex, fuzzy=True)
                        # Timex recognize the date format yyyy-mm-dd (ex : 2022-01-20')
                        result.start_date = datetime.strftime("%Y-%m-%d")
                else:
                    result.start_date = None

        except Exception as exception:
            print(exception)

        return intent, result
