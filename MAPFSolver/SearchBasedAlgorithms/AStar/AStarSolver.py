from MAPFSolver.Utilities.SingleAgentState import SingleAgentState
from MAPFSolver.Utilities.AbstractSolver import AbstractSolver
from MAPFSolver.Utilities.StatesQueue import StatesQueue
from .MultiAgentState import MultiAgentState
from threading import Thread, Event
import time


class AStarSolver(AbstractSolver):
    """
    Classical A* multi-agent algorithm. It is complete and optimal.
    """

    def __init__(self, solver_settings):
        """
        Initialize the A* solver.
        :param solver_settings: settings used by the A* solver.
        """
        super().__init__(solver_settings)
        self._frontier = []
        self._visited_list = None
        self._n_of_generated_nodes = 0
        self._n_of_expanded_nodes = 0
        self._solution = []

        self._stop_event = None

    def solve(self, problem_instance, return_infos=False):
        """
        Solve the given MAPF problem using the A* algorithm and it returns, if exists, a solution.
        :param problem_instance: instance of the problem to solve.
        :param return_infos: if True in addition to the paths will be returned also a structure with output infos.
        :return the solution as list of paths, and, if return_infos is True, a tuple composed by the solution and a
        struct with output information.
        """
        self._stop_event = Event()
        start = time.time()

        thread = Thread(target=self.solve_problem, args=(problem_instance,))
        thread.start()
        thread.join(timeout=self._solver_settings.get_time_out())
        self._stop_event.set()

        if not self._solution:
            output_infos = self.generate_output_infos(self._n_of_generated_nodes, self._n_of_expanded_nodes,
                                                      time.time() - start)
        else:


            output_infos = self.generate_output_infos(self._n_of_generated_nodes,
                                                      self._n_of_expanded_nodes, time.time() - start)

        return self._solution if not return_infos else (self._solution, output_infos)

    def solve_problem(self, problem_instance):
        """
        Solve the MAPF problem using the A* algorithm.
        :param problem_instance: problem instance to solve
        """
        self.initialize_problem(problem_instance)
        print("\n\n in AstarSolver, solver setting:\n",self._solver_settings)
        '''_frontier is a queue, here we start BFS'''
        while not len(self._frontier) == 0: #queue not empty

            if self._stop_event.is_set():
                break

            '''biggest f value pop out'''
            self._frontier.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)
            cur_state = self._frontier.pop(0)

            if cur_state.is_completed():
                self._solution = cur_state.get_paths_to_root()
                '''if goal is reached, get path and return'''
                return

            # Standard version: no detect duplicates in the frontier.
            if not self._visited_list.contains_state_same_positions(cur_state):
                self._visited_list.add(cur_state)
                expanded_nodes = cur_state.expand()
                self._n_of_generated_nodes += len(expanded_nodes)
                self._n_of_expanded_nodes += 1
                self._frontier.extend(expanded_nodes)
       

    def initialize_problem(self, problem_instance):
        """
        Initialize the frontier and the heuristic for the given problem.

        preparing relevant data structure
        """
        self._solver_settings.initialize_heuristic(problem_instance)
        self._frontier = []
        self._visited_list = StatesQueue()
        self._n_of_generated_nodes = 1
        self._n_of_expanded_nodes = 0

        single_agents_states = []
        for agent in problem_instance.get_agents():
            s = SingleAgentState(problem_instance.get_map(), agent.get_goal(), agent.get_start(), self._solver_settings)
            single_agents_states.append(s)

        '''first create single agent state, then get multi agent state
        Multi agent state is special in A* algorithm'''
        starter_state = MultiAgentState(single_agents_states, self._solver_settings)
        self._frontier.append(starter_state)
