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
    BUDGET = "budget"
    START_DATE = "str_date"
    END_DATE = "end_date"
    # MAX_DURATION = "max_duration"
    # N_ADULTS = "n_adults"
    # N_CHILDREN = "n_children"


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

        # TODO
        # try:
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

            print(f"Luis detects {intent} intent.")
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
                    result.unsupported_airports.append(to_city[0]["text"].capitalize())

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

            # BUDGET
            budget = recognizer_result.entities.get("$instance", {}).get(
                Entities.BUDGET.value, []
            )
            print(f"budget : {budget}")
            if len(budget) > 0:
                # TODO gerer le symbole $
                if recognizer_result.entities.get(Entities.BUDGET.value, []):
                    result.budget = budget[0]["text"]
                    print(f"result.budget={result.budget}")
                else:
                    result.budget = None

            # START_DATE
            start_date = recognizer_result.entities.get(Entities.START_DATE.value, [])
            print(f"start_date : {start_date}")
            result.start_date = date_recognition(start_date)

            # END_DATE
            end_date = recognizer_result.entities.get(Entities.END_DATE.value, [])
            print(f"end_date : {end_date}")
            result.end_date = date_recognition(end_date)

        # except Exception as exception:
        #     print(exception)

        return intent, result


def date_recognition(date):
    try:
        date = date[0]
        date = dparser.parse(date, fuzzy=True)
        # Timex recognize the date as yyyy-mm-dd format (ex : 2022-01-20')
        date = date.strftime("%Y-%m-%d")
        return date
    except:
        return None
