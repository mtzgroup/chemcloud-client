# Core Development Decisions

## \_RequestsClient Class

- `_RequestsClient` public http methods (like `compute()` and `result()` should always return Python objects. This gives a layer of abstraction between callers who want to think in terms of Python data objects and the `_RequestsClient` which thinks in terms of http requests and `json` data structures.

I'm starting to have second thoughts about this ^^ decision. It feels like the `_RequestsClient` is starting to take on too much responsibility. It accepts python data types as parameters, and returns python data types as it if were an end-user class. It isn't. It's meant to be a utility class used by end-user objects such as `TCClient` and `FutureResult` objects. I think it should return data more directly from the TeraChem Cloud API and let the other classes handle this data. This becomes more apparent as I add `pydantic` to my data models and realize I'd rather have them pass rawer data types to the `_RequestsClient` and then handle the results of an API call inside their own class. Maybe the `compute()` and `compute_procedure()` methods on the `_RequestsClient` should go away and these should live exclusively on the `TCClient` object which then utilizes `request` and `authenticated_request` to access TeraChem Cloud.

## FutureResult Class

- `.get()` will return either an `AtomicResult` or a `FailedOperation` object. From the users perspective they essentially get back a generic "Result" object (which will be either an `AtomicResult` or `FailedOperation`) and can check for its status (once complete) by checking `result.status`. While this separates the user a bit from the "status" field returned by the API, I think this is the easiest user interface, i.e., they get back a `result` from a `future_result` and can check its status very simply without having to think separately about status fields and results fields They can still access the API returned status field at `future_result.status` if needed. E.g.,:

```python
result = future_result.get()

result.success
False # If FailedOperation returned

result.success
True # If AtomicResult returned
```
