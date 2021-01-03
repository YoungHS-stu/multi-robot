from .State import State


class SingleAgentState(State):

    def __init__(self, problem_map, goal, position, solver_settings, parent=None):
        super().__init__(parent)
        self._map = problem_map
        self._position = position
        self._goal = goal
        self._solver_settings = solver_settings
        self.compute_cost()
        self.compute_heuristics()

    def expand(self):
        expanded_nodes_list = [self.wait_state()]
        possible_moves = self._map.neighbours(self._position)
        for i in possible_moves:
            expanded_nodes_list.append(SingleAgentState(self._map, self._goal, i, self._solver_settings, parent=self))
        return expanded_nodes_list

    def wait_state(self):
        return SingleAgentState(self._map, self._goal, self._position, self._solver_settings, parent=self)

    def expand_optimal_policy(self):
        if self.goal_test():
            return self.wait_state()

        next_node = self.get_next_optimal_state()

        return next_node

    def get_next_optimal_state(self):
        from MAPFSolver.Utilities.AStar import AStar
        from MAPFSolver.Utilities.SolverSettings import SolverSettings
        solver = AStar(SolverSettings())
        path = solver.find_path(self._map, self._position, self._goal)
        next_pos = path[1]
        return SingleAgentState(self._map, self._goal, next_pos, self._solver_settings, parent=self)

    def compute_heuristics(self):
        self._h = self._solver_settings.get_heuristic_object().compute_heuristic(self._position, self._goal)

    def compute_cost(self):
        if self.is_root():
            self._g = 0
        else:
            list_of_states = [self]
            state = self
            while not state.is_root():
                state = state.parent()
                list_of_states.append(state)

            self._g = 0
            for i, s in enumerate(list_of_states):
                if not s.goal_test():
                    if i == 0:
                        self._g = len(list_of_states) - 1
                    else:
                        self._g = len(list_of_states) - i
                    break

    def goal_test(self):
        return self._position == self._goal

    def is_completed(self):
        #if self._solver_settings.stay_at_goal():
        return self.goal_test()


    def is_gone(self):
        #if self._solver_settings.stay_at_goal():
        return False

    def get_position(self):
        return self._position

    def get_positions_list(self):
        return [self.get_position()]

    def get_path_to_root(self):
        path = []
        node = self


        while node.parent() is not None:  # Delete the extra states we don't need.
            if node.parent().goal_test():
                node = node.parent()
            else:
                break

        while node.parent() is not None:
            path.append(node._position)
            node = node.parent()
        path.append(node._position)
        path.reverse()
        return path

    def equal_position(self, other):
        assert isinstance(other, SingleAgentState)
        return self._position == other._position

    def equal(self, other):
        assert isinstance(other, SingleAgentState)
        return self._position == other._position and self.time_step() == other.time_step()

    def __str__(self):
        return '[STATE -> F:' + str(self.f_value()) + ' G:' + str(self.g_value()) + ' H:' + str(self.h_value()) + ' '\
               + str(self._position) + ' TS:' + str(self.time_step()) + ']'
