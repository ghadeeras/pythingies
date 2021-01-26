from pythingies.profiling.analysis import Analysis
from pythingies.profiling.node import AnalysisNode
from xml.sax.handler import ContentHandler


class XmlReporter:

    def __init__(self, content_handler: ContentHandler):
        self.contentHandler = content_handler

    def accept(self, analysis: Analysis):
        self.contentHandler.startDocument()
        self.contentHandler.startElement("Analysis", {})
        self.contentHandler.startElement("ThreadsAggregation", {})
        self.accept_node(analysis.threadsAggregation)
        self.contentHandler.endElement("ThreadsAggregation")
        self.contentHandler.startElement("Threads", {})
        threads = sorted(analysis.threads.items(), key=lambda item: item[0])
        for name, thread in threads:
            self.accept_node(thread)
        self.contentHandler.endElement("Threads")
        self.contentHandler.endElement("Analysis")
        self.contentHandler.endDocument()

    def accept_node(self, node: AnalysisNode):
        self.contentHandler.startElement("Node", {
            "name": node.name,
            "averageTime": str(node.average_time()),
            "averageNetTime": str(node.average_net_time()),
            "minTime": str(node.minTime),
            "maxTime": str(node.maxTime),
            "multiplicity": str(node.multiplicity()),
            "frequency": str(node.frequency())
        })
        for child in node.hot_spots():
            self.accept_node(child)
        self.contentHandler.endElement("Node")
