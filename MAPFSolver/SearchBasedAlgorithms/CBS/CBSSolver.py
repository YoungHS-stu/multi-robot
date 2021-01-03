from MAPFSolver.Utilities.AbstractSolver import AbstractSolver
from MAPFSolver.SearchBasedAlgorithms.CBS.ConstraintTreeNode import ConstraintTreeNode
from MAPFSolver.SearchBasedAlgorithms.CBS.ConstraintTreeNodesQueue import ConstraintTreeNodesQueue
from threading import Thread, Event

import time

class CBSSolver(AbstractSolver):

    def __init__(self, solver_settings):
        super().__init__(solver_settings)
        self._frontier = None
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



        output_infos = self.generate_output_infos(self._n_of_generated_nodes, self._n_of_expanded_nodes,
                                                  time.time() - start)

        return self._solution if not return_infos else (self._solution, output_infos)

    def solve_problem(self, problem_instance):
        self.initialize_problem(problem_instance)

        while not self._frontier.is_empty():
            self._frontier.sort_by_cost()
            cur_state = self._frontier.pop()

            if self._stop_event.is_set():
                break

            if cur_state.is_valid():
                self._solution = cur_state.solution()
                break

            expanded_nodes = cur_state.expand()
            self._n_of_generated_nodes += len(expanded_nodes)
            self._n_of_expanded_nodes += 1
            self._frontier.add_list_of_nodes(expanded_nodes)

    def initialize_problem(self, problem_instance):
        self._frontier = ConstraintTreeNodesQueue()
        self._n_of_generated_nodes = 1
        self._n_of_expanded_nodes = 0

        starter_state = ConstraintTreeNode(problem_instance, self._solver_settings)
        self._frontier.add(starter_state)
