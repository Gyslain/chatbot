# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    # TODO il faut rajouter les steps budget, nb_adult, nb_children
    # TODO doit on gerer les airports?
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        start_date: str = None,
        end_date: str = None,
        unsupported_airports=None,
    ):
        if unsupported_airports is None:
            unsupported_airports = []
        self.destination = destination
        self.origin = origin
        self.start_date = start_date
        self.end_date = end_date
        self.unsupported_airports = unsupported_airports
