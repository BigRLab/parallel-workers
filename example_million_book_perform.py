#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import signal
from threading import Lock
from time import sleep

from parallelization.promise_set import PromiseSet
from processors.processor_interface import Processor
from services.processor_service import ProcessorService


__author__ = 'Iván de Paz Centeno'

count = 10000
processed = 0

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
        time_to_sleep = random.randint(1,2)
        sleep(time_to_sleep)

        # Return result
        return "{} processed ({} seconds).".format(request, time_to_sleep)


#count = 40
do_abort = False

def signal_handler(signal, frame):
    global do_abort
    do_abort = True

def completed_callback(promise):
    # Shared operations requires of a multiprocessing LOCK, as this function is invoked by a parallel process
    global processed, count
    processed += 1
    print("\r{}/{}".format(processed, count), end="", flush=True)


signal.signal(signal.SIGINT, signal_handler)

# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=100)
processor_service.start()

# 2. Queue 1000000 elements
print("Generating {} elements".format(count))
requests = ["hola{}".format(x) for x in range(count)]

# Multithreaded completed_callback
print("Queuing {} elements".format(count))
promises = processor_service.queue_requests(requests, consume_immediately=False)

print("Processing started")

promise_set = PromiseSet(promises)

promise_set.wait_for_all(completed_callback=completed_callback)

processor_service.stop()
