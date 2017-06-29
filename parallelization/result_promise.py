#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import select

__author__ = "Ivan de Paz Centeno"


class WaitableEvent:
    """
    Class source: http://code.activestate.com/recipes/498191-waitable-cross-process-threadingevent-class/
    Provides an abstract object that can be used to resume select loops with
    indefinite waits from another thread or process. This mimics the standard
    threading.Event interface.
    """

    def __init__(self):
        self._read_fd, self._write_fd = os.pipe()

    def wait(self, timeout=None):
        rfds, wfds, efds = select.select([self._read_fd], [], [], timeout)
        return self._read_fd in rfds

    def isSet(self):
        return self.wait(0)

    def clear(self):
        if self.isSet():
            os.read(self._read_fd, 1)

    def set(self):
        if not self.isSet():
            os.write(self._write_fd, b'1')

    def fileno(self):
        """
        Return the FD number of the read side of the pipe, allows this object to
        be used with select.select().
        """
        return self._read_fd

    def __del__(self):
        os.close(self._read_fd)
        os.close(self._write_fd)


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
        #self.event = multithread_manager.Event()
        self.event = WaitableEvent()
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

    def _get_event(self):
        return self.event