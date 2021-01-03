from MAPFSolver.Utilities.AbstractSolver import AbstractSolver
from MAPFSolver.Utilities.AStar import AStar
from threading import Thread, Event
import time


class CooperativeAStarSolver(AbstractSolver):

    def __init__(self, solver_settings):
        super().__init__(solver_settings)
        self._reservation_table = None
        self._completed_pos = None
        self._solution = []
        self._stop_event = None

    def solve(self, problem_instance, return_infos=False):
        self._stop_event = Event()
        start = time.time()

        thread = Thread(target=self.solve_problem, args=(problem_instance,))
        thread.start()
        thread.join(timeout=self._solver_settings.get_time_out())
        self._stop_event.set()

        output_infos = self.generate_output_infos(0, 0, time.time() - start)

        return self._solution if not return_infos else (self._solution, output_infos)

    def solve_problem(self, problem_instance):
        self._reservation_table = dict()
        self._completed_pos = []

        paths = []
        for i, agent in enumerate(problem_instance.get_agents()):

            print(i," ",agent)
            if self._stop_event.is_set():
                break

            solver = AStar(self._solver_settings)
            path = solver.find_path_with_reservation_table(problem_instance.get_map(), agent.get_start(),
                                                           agent.get_goal(), self._reservation_table,
                                                           self._completed_pos)
            if not path:
                paths.append([])
                path = [agent.get_start()]
            else:
                paths.append(path)

            for j, pos in enumerate(path):
                if not self._reservation_table.get(pos):
                    self._reservation_table[pos] = []
                self._reservation_table[pos].append(j)
                self._reservation_table[pos].sort()
                self._completed_pos.append(path[-1])

            print("Path:", path)
            print("Reservation table:", self._reservation_table)
            print("Completed pos:", self._completed_pos)

        self._solution = paths

    def __str__(self):
        return "Cooperative A* Solver using " + "Manhattan" + " heuristics"
