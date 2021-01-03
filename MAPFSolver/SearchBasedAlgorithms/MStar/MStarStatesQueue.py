class MStarStatesQueue:
    def __init__(self):
        self._queue = []

    def get_node(self, item):
        for state in self._queue:
            if state.equal_position_and_time_step(item):
                return state
        return None

    def contains_state(self, item):
        for state in self._queue:
            if state.equal(item):
                return True
        return False

    def contains_position_and_time_step(self, item):
        for state in self._queue:
            if state.equal_position_and_time_step(item):
                return True
        return False

    def contains_position(self, position):
        for s in self._queue:
            if s.get_position() == position:
                return True
        return False

    def get_state_by_position(self, position):
        for s in self._queue:
            if s.get_position() == position:
                return s
        return None

    def update(self, state):
        for s in self._queue:
            if s.get_position() == state.get_position():
                self._queue.remove(s)
                self.add(state)
                return True
        return False

    def sort_by_f_value(self):
        self._queue.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)

    def add(self, item):
        self._queue.append(item)

    def add_list_of_states(self, state_list):
        self._queue.extend(state_list)

    def pop(self):
        return self._queue.pop(0)

    def is_empty(self):
        return len(self._queue) == 0

    def __str__(self):
        string = ''
        for s in self._queue[:5]:
            string = string + s.__str__()
        return string
