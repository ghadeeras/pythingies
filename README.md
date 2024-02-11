# PyThingies
Python thingies! :-) ... Currently, only one thingy is available: Profiling. It is not complete yet.

## Profiling Thingy
This is a very simple tool to analyse profiling logs, and generate a report out of them. How these logs are generated is
application-specific. As long as such logs could be parsed and provided to the tool in the form of an iterable of 
events, the tool could generate a report to better understand where CPU time is mostly spent:

```python
import pythingies.profiling as prof

events = some_code_parsing_profiling_logs()
analysis = prof.analyze(events)
prof.xml_report(analysis, '/path/to/report.xml') 
```

Each [Event](./src/prod/pythingies/profiling/event.py) should contain:
 * Type of event: `enter` vs `leave` a profiled block
 * Name of profiled block
 * Time in milliseconds
 * Thread name
