#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

from parallelization.pool_interface import PoolInterface
from parallelization.result_promise import ResultPromise
from parallelization.service_interface import ServiceInterface, SERVICE_STOPPED

__author__ = 'Iván de Paz Centeno'


class ProcessorService(ServiceInterface, PoolInterface):

    def __init__(self, processor_class, parallel_workers=10):
        ServiceInterface.__init__(self)
        PoolInterface.__init__(self, processor_class=processor_class, pool_limit=parallel_workers)
        self.total_workers = parallel_workers
        self.promises = {}

    def queue_request(self, request):
        with self.lock:
            if request in self.promises:
                promise = self.promises[request]

            else:
                promise = ResultPromise(self.manager)
                self.promises[request] = promise
                PoolInterface.queue_request(self, request)

        return promise

    def get_queue_remaining(self):

        with self.lock_process_variable:
            queue_size = self.processing_queue.qsize()

        return queue_size

    def get_workers_processing(self):

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