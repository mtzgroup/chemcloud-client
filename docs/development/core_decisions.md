# Core Development Decisions

## \_RequestsClient Class

- `_RequestsClient` public http methods (like `compute()` and `result()` should always return Python objects. This gives a layer of abstraction between callers who want to think in terms of Python data objects and the `_RequestsClient` which thinks in terms of http requests and `json` data structures.

## FutureResult Class

- `.get()` will return either an `AtomicResult` or a `FailedOperation` object. From the users perspective they essentially get back a generic "Result" object (which will be either an `AtomicResult` or `FailedOperation`) and can check for its status (once complete) by checking `result.status`. While this separates the user a bit from the "status" field returned by the API, I think this is the easiest user interface, i.e., they get back a `result` from a `future_result` and can check its status very simply without having to think separately about status fields and results fields They can still access the API returned status field at `future_result.status` if needed. E.g.,:

```python
result = future_result.get()

result.success
False # If FailedOperation returned

result.success
True # If AtomicResult returned
```
