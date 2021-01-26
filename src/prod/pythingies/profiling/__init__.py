from pythingies.profiling.event import Event
from pythingies.profiling.analysis import Analysis
from pythingies.profiling.reporting import XmlReporter
from xml.sax.saxutils import XMLGenerator


def analyze(events) -> Analysis:
    result = Analysis()
    if events:
        for e in events:
            result.handle(e)
    result.finalize()
    return result


def xml_report(a: Analysis, file: str):
    with open(file, "w") as f:
        generator = XMLGenerator(f)
        reporter = XmlReporter(generator)
        reporter.accept(a)
