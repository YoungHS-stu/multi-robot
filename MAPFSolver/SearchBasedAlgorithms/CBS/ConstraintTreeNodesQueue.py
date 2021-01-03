from MAPFSolver.SearchBasedAlgorithms.CBS.ConstraintTreeNode import ConstraintTreeNode
class ConstraintTreeNodesQueue:
    def __init__(self):
        self._queue = []

    def contains_node(self, item):
        assert isinstance(item, ConstraintTreeNode)
        for node in self._queue:
            if node.vertex_constraints() == item.vertex_constraints():
                return True
        return False

    def add(self, item):
        assert isinstance(item, ConstraintTreeNode)
        self._queue.append(item)

    def add_list_of_nodes(self, node_list):
        self._queue.extend(node_list)

    def pop(self):
        return self._queue.pop(0)

    def is_empty(self):
        return len(self._queue) == 0

    def sort_by_cost(self):
        self._queue.sort(key=lambda x: x.total_cost(), reverse=False)
