import random
import unittest

from pythingies.profiling.event import Event
from pythingies.profiling.node import AnalysisNode


class BaseTestCase(unittest.TestCase):

    def __init__(self, method_name):
        super().__init__(method_name)
        self.random = random.Random(method_name)
        self.initial_time = self.random.randint(0x01_00, 0xFF_FF_FF_FF)
        self.current_thread_name = None
        self.current_thread_logs = None
        self.logs_by_thread_name = {}

    def thread(self, name="main", loop_calls=None):
        self.current_thread_name = name
        self.current_thread_logs = []
        self.logs_by_thread_name[name] = self.current_thread_logs
        current_time = self.initial_time + self.random.randint(0, 0xFF)
        if loop_calls:
            for loop_call in loop_calls:
                current_time = loop_call(current_time)

    def call(self, name: str, time=1, count=1, sub_calls=None):
        def do_call(entry_time: int) -> int:
            assert self.current_thread_logs is not None
            current_time = entry_time
            for _ in range(count):
                remaining_time = time
                self.current_thread_logs.append(Event(Event.ENTER, name, current_time, self.current_thread_name))
                if sub_calls:
                    for sub_call in sub_calls:
                        dt = self.random.randint(0, remaining_time) if remaining_time > 0 else 0
                        remaining_time -= dt
                        current_time += dt
                        current_time = sub_call(current_time)
                current_time += remaining_time
                self.current_thread_logs.append(Event(Event.LEAVE, name, current_time, self.current_thread_name))
            return current_time

        return do_call

    def mixed_events_log(self):
        logs = sorted([
            event
            for thread_logs in self.logs_by_thread_name.values()
            for event in thread_logs
        ], key=lambda e: e.time)
        print(self._testMethodName + " logs:")
        print(sep="\n\t", *([""] + logs))
        print("\n")
        self.logs_by_thread_name.clear()
        return logs

    def child(self, node: AnalysisNode, *path: str) -> AnalysisNode:
        if len(path) == 0:
            return node
        elif len(path) == 1:
            return node.children[path[0]]
        else:
            self.child(*path[1:])

    @staticmethod
    def path(node: AnalysisNode) -> str:
        path = ""
        while node:
            path = node.name + "/" + path
            node = node.parent
        return "/" + path

    def assert_rec(self, node: AnalysisNode, expectation) -> None:
        name, assertion, children = expectation
        try:
            assertion(node)
        except AssertionError as e:
            raise AssertionError(e, BaseTestCase.path(node))

        if children:
            for child_name, sub_assertion, sub_children in children:
                self.assert_rec(node.children[child_name], (child_name, sub_assertion, sub_children))
