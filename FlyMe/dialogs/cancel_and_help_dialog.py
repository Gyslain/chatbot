# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle cancel and help intents."""

from botbuilder.core import BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.schema import ActivityTypes


class CancelAndHelpDialog(ComponentDialog):
    """Implementation of handling cancel and help."""

    def __init__(
        self,
        history,
        dialog_id: str,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(CancelAndHelpDialog, self).__init__(dialog_id)
        self.history = history
        self.telemetry_client = telemetry_client

    async def on_begin_dialog(
        self, inner_dc: DialogContext, options: object
    ) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_begin_dialog(inner_dc, options)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        """Detect interruptions."""
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()

            if text in ("help", "?"):
                msg = "Show Help..."
                self.history.append({"bot": msg})
                await inner_dc.context.send_activity(msg)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in ("cancel", "quit"):
                msg = "Cancelling"
                self.history.append({"bot": msg})
                await inner_dc.context.send_activity(msg)
                return await inner_dc.cancel_all_dialogs()

        return None
