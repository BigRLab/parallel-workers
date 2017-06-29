#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Ivan de Paz Centeno"


class ResultPromise(object):
    """
    Promise object
    Wraps a result in order to allow storage of a result between different threads.
    Also, it allows to wait for the result to be ready.
    """

    def __init__(self, multithread_manager, request, service_owner):
        """
        Initializes the result container.
        """

        self.result = None
        self.lock = multithread_manager.Lock()
        self.event = multithread_manager.Event()
        self.request = request
        self.discard_aborts = 0
        self.service_owner = service_owner

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

    def abort(self):
        """
        Aborts the current request from being processed.

        Note the following special-cases:

         * If this promise's request is getting processed at the moment it is aborted, it won't make the processor from
         cancelling its job.

         * If this promise has been delivered to many clients by the service, this method won't abort it unless all the
         clients unanimously abort it, or unless you call it the required times until it is aborted.

         It is recommended to avoid calling the get_result() method after the promise is aborted.
        :return:
        """
        with self.lock:
            if self.discard_aborts == 0:
                self.service_owner.abort_request(self.request)
            else:
                self.discard_aborts -= 1

    def is_request_aborted(self):
        with self.lock:
            aborted = self.service_owner.is_request_aborted(self.request)
        return aborted

    def discard_one_abort(self):
        with self.lock:
            self.discard_aborts += 1