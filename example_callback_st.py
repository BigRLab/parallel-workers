#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from time import sleep

from parallelization.promise_set import PromiseSet
from processors.processor_interface import Processor
from services.processor_service import ProcessorService


__author__ = 'Iván de Paz Centeno'


class ExampleProcessor(Processor):
    """
    Processor class for a simple string request.
    """

    def process(self, request):
        """
        Retrieves a request (any kind of object) and returns a result
        :param request:
        :return:
        """
        # We simulate processing time
        time_to_sleep = random.randint(0, 10)
        print("{} arrived first".format(request))
        sleep(time_to_sleep)

        # Return result
        return "{} processed ({} seconds).".format(request, time_to_sleep)



def completed_callback(promise):
    # Shared operations DOES NOT require of a multiprocessing LOCK. This function is executed in the main thread.
    print(promise.get_result())

# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=2)
processor_service.start()

# 2. Queue 4 elements
print("Queued hola, hola2, hola3 y hola4")

promise = processor_service.queue_request("hola")
promise2 = processor_service.queue_request("hola2")
promise3 = processor_service.queue_request("hola3")
promise4 = processor_service.queue_request("hola4")

promise_set = PromiseSet([promise, promise2, promise3, promise4])

# Single-threaded completed_callback
promise_set.wait_for_all(completed_callback=completed_callback)

processor_service.stop()
