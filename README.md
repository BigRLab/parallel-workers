# parallel-workers
Generic parallel workers proof of concept.

# Usage example

```bash
python3 -m example
```

# Description

Given a pool of N processes and a queue, the processes will compete each other for the elements until all of them are processed.

Given a `ExampleProcessor` class defined as:

```python
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
        # Simulate the processing time
        sleep(5)

        # Return the result.
        return "{} processed.".format(request)
```

The following example corresponds to the `example.py`, with a pool of 2 workers as a service:

```python
# 1. Start the service with 2 processors.
processor_service = ProcessorService(ExampleProcessor, parallel_workers=2)
processor_service.start()

# 2. Queue 4 elements
print("Queued hola, hola2, hola3 y hola4")
promise = processor_service.queue_request("hola")
promise2 = processor_service.queue_request("hola2")
promise3 = processor_service.queue_request("hola3")
promise4 = processor_service.queue_request("hola4")

print(promise.get_result())
print(promise2.get_result())
print(promise3.get_result())
print(promise4.get_result())

processor_service.stop()
```

The example shows the proof-of-concept simulating a process of a simple String with a `time.sleep()` of 5 seconds. 
In total, 4 different strings are provided to the pool, showing how they are processed two by two because the pool is composed by two processes. 

# Characteristics:
 * The results are retrieved by using the [promise pattern](https://en.wikipedia.org/wiki/Futures_and_promises).
 * All the queued elements that share the same python `__hash__()` will return the same promise, thus, getting processed only once regardless the number of elements with same hash queued.

# Drawbacks:
 * Retrieving a promise's result blocks the thread, blocking it from retrieving the results from other promises if they finish before. Nonetheless, a promise `select()` will be added in the future.
