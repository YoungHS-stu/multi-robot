from MAPFSolver.Heuristics.ManhattanDistanceHeuristic import ManhattanDistanceHeuristic

class SolverSettings:

    def __init__(self,  objective_function="SOC",  goal_occupation_time=1, time_out=None):
        #self._heuristic_str = "Manhattan"
        self._heuristic_obj = None
        self._objective_function = objective_function
        self._stay_at_goal = True
        self._goal_occupation_time = goal_occupation_time
        if time_out is not None:
            self._time_out = time_out if time_out > 0 else None
        else:
            self._time_out = None

        assert self._goal_occupation_time > 0, "Goal occupation time must be greater than zero!"

    def initialize_heuristic(self, problem_instance):
        self._heuristic_obj = ManhattanDistanceHeuristic(problem_instance)


    def get_heuristic_object(self):
        assert self._heuristic_obj is not None, "The heuristic need to be initialized"
        return self._heuristic_obj

    def get_objective_function(self):
        return self._objective_function

    def stay_at_goal(self):
        return True

    def get_goal_occupation_time(self):
        return self._goal_occupation_time

    def set_goal_occupation_time(self, time):
        self._goal_occupation_time = time


    def set_time_out(self, time_out):
        self._time_out = time_out

    def get_time_out(self):
        return self._time_out

    def __str__(self):
        return "Heuristics: Manhattan" +  ".\tObjective function: " + str(self._objective_function) + \
               ".\tGoal occupation time: " + str(self._goal_occupation_time)
