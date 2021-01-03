from MAPFSolver.SearchBasedAlgorithms.MStar.MStarStatesQueue import MStarStatesQueue
from MAPFSolver.Utilities.AbstractSolver import AbstractSolver
from MAPFSolver.Utilities.SingleAgentState import SingleAgentState
from MAPFSolver.Utilities.StatesQueue import StatesQueue
from MAPFSolver.SearchBasedAlgorithms.MStar.MStarState import MStarState
from threading import Thread, Event
import time


class MStarSolver(AbstractSolver):

    def __init__(self, solver_settings):
        super().__init__(solver_settings)
        self._frontier = None
        self._closed_list = None
        self._n_of_generated_nodes = 0
        self._n_of_expanded_nodes = 0
        self._solution = []

        self._stop_event = None

    def solve(self, problem_instance, return_infos=False):
        self._stop_event = Event()
        start = time.time()

        thread = Thread(target=self.solve_problem, args=(problem_instance,))
        thread.start()
        thread.join(timeout=self._solver_settings.get_time_out())
        self._stop_event.set()

        output_infos = self.generate_output_infos( self._n_of_generated_nodes, self._n_of_expanded_nodes,
                                                  time.time() - start)

        return self._solution if not return_infos else (self._solution, output_infos)

    def solve_problem(self, problem_instance):
        self.initialize_problem(problem_instance)

        while not self._frontier.is_empty():
            self._frontier.sort_by_f_value()
            cur_state = self._frontier.pop()

            if self._stop_event.is_set():
                break

            if cur_state.is_completed():
                self._solution = cur_state.get_paths_to_root()
                return

            self._closed_list.add(cur_state)
            expanded_nodes = cur_state.expand()
            self._n_of_generated_nodes += len(expanded_nodes)
            self._n_of_expanded_nodes += 1

            for node in expanded_nodes:
                if self._closed_list.contains_position_and_time_step(node):
                    n = self._closed_list.get_node(node)
                else:
                    n = node
                self.back_propagate(cur_state, n)
                if len(n.get_collisions_set()) == 0:
                    self._frontier.add(n)

    def back_propagate(self, vk, vl):
        ck = vk.get_collisions_set().copy()
        cl = vl.get_collisions_set().copy()

        if not cl.issubset(ck):
            vk.set_collisions_set(ck.union(cl))

            if not self._frontier.contains_state(vk):
                self._frontier.add(vk)

            for vm in vk.get_back_propagation_set():
                self.back_propagate(vm, vk)

    def initialize_problem(self, problem_instance):
        self._solver_settings.initialize_heuristic(problem_instance)
        self._frontier = StatesQueue()
        self._closed_list = MStarStatesQueue()
        self._n_of_generated_nodes = 1
        self._n_of_expanded_nodes = 0

        single_agents_states = []
        for agent in problem_instance.get_agents():
            s = SingleAgentState(problem_instance.get_map(), agent.get_goal(), agent.get_start(), self._solver_settings)
            single_agents_states.append(s)

        starter_state = MStarState(single_agents_states, self._solver_settings)
        self._frontier.add(starter_state)

    def __str__(self):
        return "M* Solver using " + "Manhattan" + " heuristics minimazing " + \
               self._solver_settings.get_objective_function()
