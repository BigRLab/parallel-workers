#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

from parallelization.pool_interface import PoolInterface
from parallelization.result_promise import ResultPromise, WaitableEvent
from parallelization.service_interface import ServiceInterface, SERVICE_STOPPED

__author__ = 'Iván de Paz Centeno'


class ProcessorService(ServiceInterface, PoolInterface):

    def __init__(self, processor_class, parallel_workers=10, processor_class_init_args=None):
        ServiceInterface.__init__(self)
        PoolInterface.__init__(self, processor_class=processor_class, pool_limit=parallel_workers,
                               processor_class_init_args=processor_class_init_args)
        self.total_workers = parallel_workers
        self.promises = {}
        self.promises_lock = self.manager.Lock()
        self.promises_event = WaitableEvent()

    def queue_request(self, request, completed_callback=None):
        promise = self._book_request(request, completed_callback=completed_callback)
        self._consume_booked(promise)

        return promise

    def queue_requests(self, requests, completed_callback=None, consume_immediately=True):
        """
        Queues the requests in the pool for getting processed.
        :param requests: list of requests to be queued.
        :param completed_callback: completed_callback for calling whenever the request is finished. This is a paralleled invoked method,
         requiring of a multiprocessing lock to syncrhonize values.
        :param consume_immediately: Each request from the requests list is queued into the pool for processing. This
         flag specifies whether the request should be processed as fast as it gets queued, or if its processing should
         be delayed until all the requests from the list are successfully queued.
        :return: A processing promise per request, wrapped in a list.
        """
        if consume_immediately:
            promises = [self.queue_request(request, completed_callback=completed_callback) for request in requests]
        else:
            promises = [self._book_request(request, completed_callback=completed_callback) for request in requests]
            for promise in promises: self._consume_booked(promise)

        return promises

    def _book_request(self, request, completed_callback=None):
        """
        Generates the promise without queuing the request.
        Invoke _consume_booked() with the promise to make it real.
        :param request:
        :param completed_callback:
        :return:
        """
        with self.lock:
            if request in self.promises:
                promise = self.promises[request]
            else:
                promise = ResultPromise(self.manager, request, self, completed_callback, promise_lock=self.promises_lock,
                                        promise_event=self.promises_event)

        promise.set_booked()

        return promise

    def _consume_booked(self, promise):
        """
        Performs the queue of the promise inside the parallel pool. Must have been booked before..
        :return:
        """
        if not promise.is_booked():
            return False

        request = promise.get_request()

        with self.lock:
            if request in self.promises:
                promise.discard_one_abort()
            else:
                self.promises[request] = promise

        promise.unset_booked()

        PoolInterface.queue_request(self, request)

        return True

    def get_queue_remaining(self):

        with self.lock_process_variable:
            queue_size = self.processing_queue.qsize()

        return queue_size

    def get_workers_processing_count(self):

        workers_free = self.get_processes_free()
        return self.total_workers - workers_free

    def __internal_thread__(self):
        ServiceInterface.__internal_thread__(self)

        while not self.__get_stop_flag__():

            if self.get_queue_remaining() == 0 or self.get_processes_free() == 0:
                sleep(0.1)

            self.process_queue()

        self.__set_status__(SERVICE_STOPPED)

    def process_finished(self, wrapped_result):
        """
        Method invoked when the process of the processor finished processing the request.
        :param wrapped_result: parameters of the result
        :return:
        """

        try:
            request = wrapped_result[0]
            result = wrapped_result[1]

            with self.lock:
                if request in self.promises:
                    promise = self.promises[request]
                    del self.promises[request]
                    promise.set_result(result)
                else:
                    raise Exception("Retrieved result for a request not listed as queued.")

        except Exception as ex:
            print(ex)

        self.process_queue()
