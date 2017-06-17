#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Ivan de Paz Centeno"


class ResultPromise(object):
    """
    Promise object
    Wraps a result in order to allow storage of a result between different threads.
    Also, it allows to wait for the result to be ready.
    """

    def __init__(self, multithread_manager):
        """
        Initializes the result container.
        """

        self.result = None
        self.lock = multithread_manager.Lock()
        self.event = multithread_manager.Event()

    def set_result(self, result):
        """
        Setter for the resource.
        """

        with self.lock:
            self.result = result

        self.event.set()

    def get_result(self):
        """
        Getter for the result. It will wait until the result is ready.
        :return: Resource object.
        """

        self.event.wait()

        with self.lock:
            result = self.result

        return result
