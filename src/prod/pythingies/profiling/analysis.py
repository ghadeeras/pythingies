from pythingies.profiling.event import Event
from pythingies.profiling.node import AnalysisNode


class Analysis:

    def __init__(self):
        self.threads = {}
        self.threadsAggregation: AnalysisNode or None = None

    def handle(self, event: Event):
        assert self.threadsAggregation is None
        if event.thread not in self.threads:
            root_node = AnalysisNode(name=event.thread)
            root_event = Event.enter(event.thread, event.time, event.thread)
            self.threads[event.thread] = root_node.enter(root_event)

        thread_node = self.threads[event.thread]
        self.threads[event.thread] = thread_node.handle(event)

    def finalize(self):
        assert self.threadsAggregation is None
        for thread_name, thread in self.threads.items():
            while thread.parent:
                thread = thread.do_leave()
            thread.do_leave()
            self.threads[thread_name] = thread
        self.threadsAggregation = AnalysisNode.merge(None, self.threads.values())

    def threads_aggregation(self) -> AnalysisNode:
        assert self.threadsAggregation is not None
        return self.threadsAggregation
