from MAPFSolver.SearchBasedAlgorithms.AStar.MultiAgentState import MultiAgentState
import itertools


class MStarState(MultiAgentState):

    def __init__(self, single_agents_states, solver_settings, parent=None):
        super().__init__(single_agents_states, solver_settings, parent=parent)
        self._back_propagation_set = []
        self._collisions_set = set()
        self.compute_cost()
        self.compute_heuristics()

    def expand(self):

        candidate_list = []
        for i, single_state in enumerate(self._single_agents_states):
            if i in self._collisions_set:
                single_state_neighbor_list = single_state.expand()
                candidate_list.append(single_state_neighbor_list)
            else:
                next_optimal_state = single_state.expand_optimal_policy()
                candidate_list.append([next_optimal_state])

        candidate_state_list = list(itertools.product(*candidate_list))

        valid_states = []
        for i, multi_state in enumerate(candidate_state_list):
            if self.is_valid(multi_state):
                valid_states.append(multi_state)

        expanded_states = []
        for i, multi_state in enumerate(valid_states):
            m = MStarState(multi_state, self._solver_settings, parent=self)
            m.set_back_propagation_set([self])
            m.set_collisions_set(self.colliding_robots(m).copy())
            expanded_states.append(m)

        return expanded_states

    def equal_position(self, other):
        assert isinstance(other, MStarState)
        for i, single_state in enumerate(self._single_agents_states):
            if not single_state.equal_position(other.get_single_agent_states()[i]):
                return False
        return True

    def equal_position_and_time_step(self, other):
        assert isinstance(other, MStarState)
        for i, single_state in enumerate(self._single_agents_states):
            if not single_state.equal(other.get_single_agent_states()[i]):
                return False
        return True

    def equal(self, other):
        assert isinstance(other, MStarState)
        if not self._collisions_set == other._collisions_set:
            return False
        for i, single_state in enumerate(self._single_agents_states):
            if not single_state.equal(other.get_single_agent_states()[i]):
                return False
        return True

    def set_back_propagation_set(self, back_set):
        self._back_propagation_set = back_set

    def get_back_propagation_set(self):
        return self._back_propagation_set

    def set_collisions_set(self, collisions_set):
        self._collisions_set = collisions_set

    def get_collisions_set(self):
        return self._collisions_set

    def __str__(self):
        string = '[F:' + str(self.f_value()) + ' G: ' + str(self.g_value()) + ' TS:' + str(self.time_step()) + ' '
        string += str(self.get_positions_list()) + ' ' + str(self.get_collisions_set()) + ']'
        return string
