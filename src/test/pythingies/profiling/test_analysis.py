from pythingies.profiling import analyze
from testing_utils import BaseTestCase


class AnalysisTest(BaseTestCase):

    def assert_equivalence(self, n1, n2):
        self.assertEqual(n1.count, n2.count)
        self.assertEqual(n1.totalTime, n2.totalTime)
        self.assertSetEqual(set(n1.children.keys()), set(n2.children.keys()))
        for child_name in n1.children:
            self.assert_equivalence(n1.children[child_name], n2.children[child_name])

    def run_thread1(self):
        self.thread("thread1", [
            self.call("a", 7, 1, [
                self.call("c", 3, 2),
                self.call("d", 2, 3),
                self.call("e", 1, 1),
            ]),
            self.call("a", 5, 1, [
                self.call("b", 1, 1),
                self.call("c", 2, 2),
                self.call("d", 3, 3)
            ]),
            self.call("b", 5, 1, [
                self.call("b", 3, 3, [
                    self.call("c", 7, 1)
                ])
            ])
        ])

    def test_empty_logs_give_empty_analysis(self):
        analysis = analyze(None)
        self.assertDictEqual(analysis.threads, {})
        self.assertIsNone(analysis.threadsAggregation)

        analysis = analyze(self.mixed_events_log())
        self.assertDictEqual(analysis.threads, {})
        self.assertIsNone(analysis.threadsAggregation)

    def test_counts(self):
        def count(expected):
            return lambda node: self.assertEqual(node.count, expected)

        self.run_thread1()
        analysis = analyze(self.mixed_events_log())

        expectation = ("root", count(1), [
            ("a", count(2), [
                ("b", count(1), []),
                ("c", count(4), []),
                ("d", count(6), []),
                ("e", count(1), [])
            ]),
            ("b", count(1), [
                ("b", count(3), [
                    ("c", count(3), [])
                ])
            ])
        ])
        self.assert_rec(analysis.threads_aggregation(), expectation)
        self.assert_rec(analysis.threads["thread1"], expectation)

    def test_total_time(self):
        def total_time(expected):
            return lambda node: self.assertEqual(node.totalTime, expected)

        self.run_thread1()
        analysis = analyze(self.mixed_events_log())

        expectation = ("root", total_time(74), [
            ("a", total_time(39), [
                ("b", total_time(1), []),
                ("c", total_time(10), []),
                ("d", total_time(15), []),
                ("e", total_time(1), [])
            ]),
            ("b", total_time(35), [
                ("b", total_time(30), [
                    ("c", total_time(21), [])
                ])
            ])
        ])
        self.assert_rec(analysis.threads_aggregation(), expectation)
        self.assert_rec(analysis.threads["thread1"], expectation)

    def test_missing_trailing_events(self):
        self.thread(loop_calls=[
            self.call("a", 0, 1, [
                self.call("a1", 5, 1),
                self.call("a2", 3, 1)
            ]),
            self.call("b", 0, 1, [
                self.call("b1", 3, 1),
                self.call("b2", 5, 1)
            ])
        ])

        events = self.mixed_events_log()
        first_events = [event for event in events if event.time < events[-1].time - 2]
        assert len(first_events) == len(events) - 2

        analysis = analyze(first_events)

        self.thread(loop_calls=[
            self.call("a", 0, 1, [
                self.call("a1", 5, 1),
                self.call("a2", 3, 1)
            ]),
            self.call("b", 0, 1, [
                self.call("b1", 3, 1),
                self.call("b2", 0, 1)
            ])
        ])

        equivalent_analysis = analyze(self.mixed_events_log())

        self.assert_equivalence(analysis.threadsAggregation, equivalent_analysis.threadsAggregation)

    def test_missing_leading_events(self):
        self.thread(loop_calls=[
            self.call("a", 0, 1, [
                self.call("a1", 5, 1),
                self.call("a2", 3, 1)
            ]),
            self.call("b", 0, 1, [
                self.call("b1", 3, 1),
                self.call("b2", 5, 1)
            ])
        ])

        events = self.mixed_events_log()
        first_events = [event for event in events if event.time > events[0].time + 2]
        assert len(first_events) == len(events) - 2

        analysis = analyze(first_events)

        self.thread(loop_calls=[
            self.call("a", 0, 1, [
                self.call("a1", 0, 1),
                self.call("a2", 3, 1)
            ]),
            self.call("b", 0, 1, [
                self.call("b1", 3, 1),
                self.call("b2", 5, 1)
            ])
        ])

        equivalent_analysis = analyze(self.mixed_events_log())

        self.assert_equivalence(analysis.threadsAggregation, equivalent_analysis.threadsAggregation)
