#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import signal
from threading import Lock
from time import sleep

import sys

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
        time_to_sleep = random.randint(1,2)
        print("{} arrived first".format(request))
        sleep(time_to_sleep)

        # Return result
        return "{} processed ({} seconds).".format(request, time_to_sleep)

count = 1000000
promises = []
do_abort = False


def signal_handler(signal, frame):
    global do_abort
    do_abort = True

signal.signal(signal.SIGINT, signal_handler)

def completed_callback(promise):
    # Shared operations requires of a multiprocessing LOCK, as this function is invoked by a parallel process
    result = promise.get_result()
    if result is not None:
        print(result)


# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=20)
processor_service.start()

# 2. Queue 1000000 elements
print("Queued {} elements".format(count))
requests = ["hola{}".format(x) for x in range(count)]

# Multithreaded completed_callback
i = 0
for request in requests:
    i += 1
    promises.append(processor_service.queue_request(request, completed_callback))
    print("{}/{}".format(i, count))

    if do_abort:
        for promise in promises[::-1]:
            promise.abort()
        break

promise_set = PromiseSet(promises)

promise_set.wait_for_all(ignore_aborted=True)

processor_service.stop()
