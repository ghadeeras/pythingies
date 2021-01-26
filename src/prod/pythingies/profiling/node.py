from pythingies.profiling.event import Event


class AnalysisNode:

    ROOT = "root"

    def __init__(self, parent=None, name=ROOT):
        self.parent = parent
        self.children = {}
        self.name = name
        self.count = 0
        self.firstTime = None
        self.lastTime = 0
        self.lastLeaveTime = 0
        self.totalTime = 0
        self.minTime = 0x7F_FF_FF_FF_FF_FF_FF_FF
        self.maxTime = 0

    def handle(self, event: Event):
        if event.kind == Event.ENTER:
            if event.name not in self.children:
                self.children[event.name] = AnalysisNode(self, event.name)
            return self.children[event.name].enter(event)
        else:
            return self.leave(event)

    def enter(self, event: Event):
        assert event.kind == Event.ENTER
        assert event.name == self.name
        self.count += 1
        self.lastTime = event.time
        if self.firstTime is None:
            self.firstTime = event.time
        return self

    def leave(self, event: Event):
        assert event.kind == Event.LEAVE
        assert event.name == self.name
        delta = event.time - self.lastTime
        self.lastLeaveTime = event.time
        self.totalTime += delta
        self.minTime = min(delta, self.minTime)
        self.maxTime = max(delta, self.maxTime)
        return self.parent

    def do_leave(self):
        time = self.lastTime
        for child in self.children.values():
            time = max(child.lastLeaveTime, time)
        return self.leave(Event.leave(self.name, time, ""))

    def children_time(self) -> int:
        return sum([child.totalTime for child in self.children.values()])

    def average_time(self) -> float:
        return float(self.totalTime) / self.count

    def net_time(self) -> int:
        return self.totalTime - self.children_time()

    def average_net_time(self) -> float:
        return float(self.net_time()) / self.count

    def frequency(self) -> float or None:
        time = self.lastTime - self.firstTime
        return float(self.count - 1) * (1000.0 / time) if time > 0 else None

    def multiplicity(self) -> float:
        return float(self.count) / self.parent.count if self.parent is not None else float(self.count)

    def hot_spots(self, percentage=1.0):
        time = percentage * self.children_time()
        children = sorted(self.children.values(), key=lambda node: node.totalTime, reverse=True)
        result = []
        for child in children:
            result.append(child)
            time -= child.totalTime
            if time < 0:
                break
        return result

    @staticmethod
    def merge(parent, nodes):
        if not nodes:
            return None

        names = {(node.name if node.parent else AnalysisNode.ROOT) for node in nodes}
        assert len(names) == 1
        name = list(names)[0]
        result = AnalysisNode(parent, name)

        for node in nodes:
            result.count += node.count
            result.totalTime += node.totalTime
            result.firstTime = \
                node.firstTime if result.firstTime is None or node.firstTime < result.firstTime \
                else result.firstTime
            result.lastTime = node.lastTime if node.lastTime > result.lastTime else result.lastTime
            result.minTime = node.minTime if node.minTime < result.minTime else result.minTime
            result.maxTime = node.maxTime if node.maxTime > result.maxTime else result.maxTime

        child_names = {child_name for node in nodes for child_name in node.children}
        for child_name in child_names:
            children = [node.children[child_name] for node in nodes if child_name in node.children]
            if len(children) > 0:
                result.children[child_name] = AnalysisNode.merge(result, children)

        return result
