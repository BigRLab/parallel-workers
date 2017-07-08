#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selectors

__author__ = "Ivan de Paz Centeno"

class PromiseSet(object):
    """
    Wraps a set of promises
    """

    def __init__(self, promises_list):
        self.promises_list = promises_list
        self.promises_selected = []
        self.events = []

        self.selectors = selectors.DefaultSelector()
        self.promises_count = len(promises_list)

        # We get events that are different

        for promise in promises_list:
            event = promise._get_event()

            if event not in self.events:
                self.events.append(event)

        index = -1
        for event in self.events:
            index += 1
            self.selectors.register(event, selectors.EVENT_READ, index)


    def select(self, timeout=None):
        """
        Selects the first promise accomplished.
        :return: first promise accomplished
        """
        #previous_lengths = [0, 0]
        while len(self.promises_selected) < self.promises_count:
            # DONE: TIMEOUT, EXIT IF LEN OF BOTH ARE THE SAME DURING 2 "WHILE" ITERATIONS.
            #if previous_lengths == [len(self.promises_selected), len(self.promises_list)]:
            #    break

            #previous_lengths = [len(self.promises_selected), len(self.promises_list)]

            for event_taken in self.selectors.select(timeout):
                event_index = event_taken[0].data
                event = self.events[event_index]

                selected_promises = []

                for promise in self.promises_list:
                    if promise.peak_result():
                        selected_promises.append(promise)

                for selected_promise in selected_promises:
                    self.promises_selected.append(selected_promise)
                    self.promises_list.remove(selected_promise)
                    yield selected_promise

                if len(selected_promises) == 0:
                        self.selectors.unregister(event)
                        self.selectors.register(event, selectors.EVENT_READ, event_index)


    def wait_for_all(self, timeout=None, completed_callback=None, ignore_aborted=False):

        for promise in self.select(timeout=timeout):
            if completed_callback is not None:
                if ignore_aborted and promise.is_aborted():
                    continue
                completed_callback(promise)
