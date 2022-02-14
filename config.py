#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""
import os

# from dotenv import dotenv_values

# config = dotenv_values(".env")


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 8000

    APP_ID = os.environ.get("APP_ID", "")
    APP_PASSWORD = os.environ.get("APP_PASSWORD", "")

    LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "")
    LUIS_API_KEY = os.environ.get("LUIS_AUTHORING_KEY", "")
    LUIS_END_POINT = os.environ.get("LUIS_AUTHORING_END_POINT", "")

    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "APPINSIGHTS_INSTRUMENTATION_KEY", ""
    )

    def print(self):
        print(f"PORT : {DefaultConfig.PORT}")
        print(f"APP_ID : {DefaultConfig.APP_ID}")
        print(f"APP_PASSWORD : {DefaultConfig.APP_PASSWORD}")
        print(f"LUIS_APP_ID : {DefaultConfig.LUIS_APP_ID}")
        print(f"LUIS_API_KEY : {DefaultConfig.LUIS_API_KEY}")
        print(f"LUIS_END_POINT : {DefaultConfig.LUIS_END_POINT}")
        print(
            f"APPINSIGHTS_INSTRUMENTATION_KEY : {DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY}"
        )


#     PORT = 3978
#     APP_ID = config["APP_ID"]
#     APP_PASSWORD = config["APP_PASSWORD"]
#     LUIS_APP_ID = config["LUIS_APP_ID"]
#     LUIS_API_KEY = config["LUIS_AUTHORING_KEY"]
#     LUIS_END_POINT = config["LUIS_AUTHORING_END_POINT"]
#     APPINSIGHTS_INSTRUMENTATION_KEY = config["APPINSIGHTS_INSTRUMENTATION_KEY"]
