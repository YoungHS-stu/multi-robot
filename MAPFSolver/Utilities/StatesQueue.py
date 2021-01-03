from MAPFSolver.Utilities.SingleAgentState import SingleAgentState


class StatesQueue:

    def __init__(self):
        self._queue = []

    def add(self, item):
        self._queue.append(item)

    def add_list_of_states(self, state_list):
        self._queue.extend(state_list)

    def pop(self):
        return self._queue.pop(0)

    def is_empty(self):
        return len(self._queue) == 0

    def contains_state(self, item):
        for state in self._queue:
            if state.equal(item):
                return True
        return False

    def contains_state_same_positions(self, item):
        for state in self._queue:
            if state.equal_position(item):
                return state
        return None

    def update(self, state):
        for s in self._queue:
            if s.equal_position(state):
                self._queue.remove(s)
                self.add(state)
                return True
        return False

    def contains_position(self, position):
        if self._queue:
            assert isinstance(self._queue[0], SingleAgentState), "It can be called only in the single-agent case."
            for s in self._queue:
                if s.get_position() == position:
                    return s
        return None

    def sort_by_f_value(self):
       self._queue.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)

    def __str__(self):
        string = ''
        for s in self._queue[:5]:
            string = string + s.__str__()
        return string
