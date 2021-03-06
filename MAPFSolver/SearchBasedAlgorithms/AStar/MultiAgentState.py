from MAPFSolver.Utilities.State import State
from MAPFSolver.Utilities.SingleAgentState import SingleAgentState
import itertools


class MultiAgentState(State):

    def __init__(self, single_agents_states, solver_settings, parent=None):
        super().__init__(parent=parent)
        self._single_agents_states = single_agents_states
        self._solver_settings = solver_settings
        self.set_time_step(max([state.time_step() for state in single_agents_states]))
        self.compute_cost()
        self.compute_heuristics()

    def expand(self):
        candidate_list = []
        for single_state in self._single_agents_states:
            single_state_neighbor_list = single_state.expand()
            candidate_list.append(single_state_neighbor_list)

        #calculate Cartesian Product of candidates
        #contains all possible conbinations of moves
        candidate_state_list = list(itertools.product(*candidate_list))

        valid_states = []
        for i, multi_state in enumerate(candidate_state_list):
            if self.is_valid(multi_state):
                valid_states.append(multi_state)

        free_conflict_states = []
        for i, multi_state in enumerate(valid_states):
            m = MultiAgentState(multi_state, self._solver_settings, parent=self)
            if not self.is_conflict(m):
                free_conflict_states.append(m)


        return free_conflict_states

    def is_conflict(self, multi_state):
        current_positions = self.get_positions_list()
        next_positions = multi_state.get_positions_list()

        next_active_positions = multi_state.get_active_positions()
        if len(next_active_positions) != len(set(next_active_positions)):
            return True

        for i, next_pos in enumerate(next_positions):
            for j, cur_pos in enumerate(current_positions):
                if i != j:
                    if next_pos == cur_pos:
                        if next_positions[j] == current_positions[i]:
                            return True
        return False

    def colliding_robots(self, multi_state):
        colliding_robots = set()

        for i, next_state_i in enumerate(multi_state.get_single_agent_states()):
            for j, next_state_j in enumerate(multi_state.get_single_agent_states()):
                if i != j and next_state_i.get_position() == next_state_j.get_position() and \
                        not next_state_i.is_gone() and not next_state_j.is_gone():
                    colliding_robots.add(i)
                    colliding_robots.add(j)


        current_positions = self.get_positions_list()
        next_positions = multi_state.get_positions_list()

        for i, next_pos in enumerate(next_positions):
            for j, cur_pos in enumerate(current_positions):
                if i != j:
                    if next_pos == cur_pos:
                        if next_positions[j] == current_positions[i]:
                            colliding_robots.add(i)
                            colliding_robots.add(j)

        return colliding_robots

    def get_active_positions(self):
        pos_list = []
        for state in self._single_agents_states:
            if not state.is_gone():
                pos_list.append(state.get_position())
        return pos_list

    def goal_test(self):
        for single_state in self._single_agents_states:
            if not single_state.goal_test():
                return False
        return True

    def is_completed(self):
        for single_state in self._single_agents_states:
            if not single_state.is_completed():
                return False
        return True

    def compute_heuristics(self):
        self._h = 0
        if self._solver_settings.get_objective_function() == "SOC":
            for single_state in self._single_agents_states:
                self._h += single_state.h_value()
        if self._solver_settings.get_objective_function() == "Makespan":
            self._h = max([single_state.h_value() for single_state in self._single_agents_states])

    def compute_cost(self):
        self._g = 0
        if self.is_root():
            return
        if self._solver_settings.get_objective_function() == "SOC":
            for single_state in self._single_agents_states:
                self._g += single_state.g_value()
        if self._solver_settings.get_objective_function() == "Makespan":
            self._g = max([single_state.g_value() for single_state in self._single_agents_states])

    def get_paths_to_root(self):
        paths = []
        for single_state in self._single_agents_states:
            paths.append(single_state.get_path_to_root())
        return paths

    def get_single_agent_states(self):
        return self._single_agents_states

    def get_positions_list(self):
        return [state.get_position() for state in self._single_agents_states]

    def equal_position(self, other):
        assert isinstance(other, MultiAgentState)
        for i, single_state in enumerate(self._single_agents_states):
            if not single_state.equal_position(other.get_single_agent_states()[i]):
                return False
        return True

    def equal(self, other):
        assert isinstance(other, MultiAgentState)
        for i, single_state in enumerate(self._single_agents_states):
            if not single_state.equal(other.get_single_agent_states()[i]):
                return False
        return True

    def __str__(self):
        string = '[F:' + str(self.f_value()) + ' G: ' + str(self.g_value()) + ' TS:' + str(self.time_step()) + ' '
        string += str(self.get_positions_list()) + ']'
        return string

    @staticmethod
    def is_valid(multi_state):
        if len(multi_state) == 1:
            return True
        for s in multi_state:
            assert isinstance(s, SingleAgentState)
        return True
