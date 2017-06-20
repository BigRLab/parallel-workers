# parallel-workers
Generic parallel workers proof of concept.  With pool of processes as a single service, and usage of promises for results.

# Usage example

```bash
python3 -m example
```

# Description
Given a pool of N processes and a queue, the processes will compete each other for the elements until all of them are processed.
The example shows the proof-of-concept simulating a process of a simple String with a `time.sleep()` of 5 seconds. 
In total, 4 different strings are provided to the pool, showing how they are processed two by two because the pool is composed by two processes. 

# Characteristics:
 * The results are retrieved by using the [promise pattern](https://en.wikipedia.org/wiki/Futures_and_promises).
 * All the queued elements that share the same python `__hash__()` will return the same promise, thus, getting processed only once regardless the number of elements with same hash queued.

# Drawbacks:
 * Retrieving a promise's result blocks the thread, blocking it from retrieving the results from other promises if they finish before. Nonetheless, a promise `select()` will be added in the future.
