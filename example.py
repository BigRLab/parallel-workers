#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from time import sleep
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


# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=2)
processor_service.start()

# 2. Queue 4 elements
print("Queued hola, hola2, hola3 y hola4")
promise = processor_service.queue_request("hola")
promise2 = processor_service.queue_request("hola2")
promise3 = processor_service.queue_request("hola3")
promise4 = processor_service.queue_request("hola4")

# A promise can be aborted before it is getting processed.
promise3.abort()
print("Aborted promise3")

print(promise.get_result())
print(promise2.get_result())
print(promise3.get_result())
print(promise4.get_result())
processor_service.stop()
