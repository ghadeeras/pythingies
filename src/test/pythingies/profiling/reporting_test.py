from io import StringIO
from xml.etree import ElementTree
from xml.sax.saxutils import XMLGenerator

from pythingies.profiling import analyze, XmlReporter
from testing_utils import BaseTestCase


class ReportingTest(BaseTestCase):

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

    def test_xml_report(self):
        # Analyse
        self.run_thread1()
        analysis = analyze(self.mixed_events_log())

        # Generate report
        sio = StringIO()
        reporter = XmlReporter(XMLGenerator(out=sio, short_empty_elements=True))
        reporter.accept(analysis)
        xml = sio.getvalue()
        print(xml)

        # Parse report
        tree = ElementTree.fromstring(xml)

        # Assertions
        [[aggregated_thread], [thread_node]] = tree
        self.assertEqual(aggregated_thread.attrib['name'], 'root')
        self.assertEqual(thread_node.attrib['name'], 'thread1')

        [node_a, node_b] = aggregated_thread
        self.assertEqual(node_a.attrib['name'], 'a')
        self.assertEqual(node_b.attrib['name'], 'b')

        [node_a1, node_b1] = thread_node
        self.assertEqual(node_a1.attrib['name'], 'a')
        self.assertEqual(node_b1.attrib['name'], 'b')
