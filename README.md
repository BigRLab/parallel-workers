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
 * The promises results can be selected based on the moment they get released with the `PromiseSet` class. Example:
```python
promise_set = PromiseSet([promise, promise2, promise3, promise4])

# This loop takes the promises by arrival order
for promise in promise_set.select():
 print("Result: ", promise.get_result())
```
 * The promises results can be retrieved as event-callbacks with a single thread (main thread) by using the `PromiseSet` class. Example:
```python
def completed_callback(promise):
    # Shared operations DOES NOT require of a multiprocessing LOCK. This function is executed in the main thread.
    print(promise.get_result())

promise_set = PromiseSet([promise, promise2, promise3, promise4])

# Single-threaded completed_callback
promise_set.wait_for_all(completed_callback=completed_callback)
```
 * The promises results can be retrieved as event-callbacks with multi-threads. Example:
```python
def completed_callback(promise):
    # Shared operations requires of a multiprocessing LOCK, as this function is invoked by a parallel process
    print(promise.get_result())

# Multithreaded completed_callback
promise = processor_service.queue_request("hola", completed_callback)
promise2 = processor_service.queue_request("hola2", completed_callback)
promise3 = processor_service.queue_request("hola3", completed_callback)
promise4 = processor_service.queue_request("hola4", completed_callback)

promise_set = PromiseSet([promise, promise2, promise3, promise4])
promise_set.wait_for_all()
```
* Requests can be aborted by using its promises. Example:
```python
promise = processor_service.queue_request("hola")
promise2 = processor_service.queue_request("hola2")
promise3 = processor_service.queue_request("hola3")
promise4 = processor_service.queue_request("hola4")

# A promise can be aborted before it is getting processed.
promise3.abort()
```

* Supports a virtually unlimited amount of requests/promises. Example:
```python
requests = ["hola{}".format(i) for i in range(1000000)] 
promises = [processor_service.queue_request(request) for request in requests]
promise_set = PromiseSet(promises)

# Single-threaded completed_callback
promise_set.wait_for_all(completed_callback=completed_callback)
```
