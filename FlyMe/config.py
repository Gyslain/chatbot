#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

from dotenv import dotenv_values

config = dotenv_values(".env")


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = config["APP_ID"]
    APP_PASSWORD = config["APP_PASSWORD"]
    LUIS_APP_ID = config["LUIS_APP_ID"]
    LUIS_API_KEY = config["LUIS_AUTHORING_KEY"]
    LUIS_END_POINT = config["LUIS_AUTHORING_END_POINT"]
    APPINSIGHTS_INSTRUMENTATION_KEY = config["APPINSIGHTS_INSTRUMENTATION_KEY"]
