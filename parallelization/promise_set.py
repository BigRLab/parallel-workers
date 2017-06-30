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
        self.selectors = selectors.DefaultSelector()
        self.consumed_count = 0

        index = -1
        for promise in promises_list:

            index += 1
            event = promise._get_event()

            self.selectors.register(event, selectors.EVENT_READ, index)


    def select(self, timeout=None):
        """
        Selects the first promise accomplished.
        :return: first promise accomplished
        """
        while self.consumed_count < len(self.promises_list):
            for event in self.selectors.select(timeout):
                self.consumed_count += 1
                promise = self.promises_list[event[0].data]
                self.selectors.unregister(promise._get_event())
                yield self.promises_list[event[0].data]

    def wait_for_all(self, timeout=None, completed_callback=None):
        while self.consumed_count < len(self.promises_list):
            for event in self.selectors.select(timeout):
                self.consumed_count += 1
                promise = self.promises_list[event[0].data]
                self.selectors.unregister(promise._get_event())
                if completed_callback is not None:
                    completed_callback(promise)