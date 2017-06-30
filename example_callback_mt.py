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
    # Shared operations requires of a multiprocessing LOCK, as this function is invoked by a parallel process
    print(promise.get_result())

# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=2)
processor_service.start()

# 2. Queue 4 elements
print("Queued hola, hola2, hola3 y hola4")

# Multithreaded completed_callback
promise = processor_service.queue_request("hola", completed_callback)
promise2 = processor_service.queue_request("hola2", completed_callback)
promise3 = processor_service.queue_request("hola3", completed_callback)
promise4 = processor_service.queue_request("hola4", completed_callback)

promise_set = PromiseSet([promise, promise2, promise3, promise4])

promise_set.wait_for_all()

processor_service.stop()
