import abc
class AbstractSolver:
    """
    Abstract class for any solver.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, solver_settings):
        """
        Initialize the solver.
        :param solver_settings: settings used by the solver.
        """
        self._solver_settings = solver_settings

    @abc.abstractmethod
    def solve(self, problem_instance, return_infos=False):
        """
        Solve the given MAPF problem and it returns, if exists, a solution.
        :param problem_instance: instance of the problem to solve.
        :param return_infos: if True in addition to the paths will be returned also a structure with output infos.
        :return the solution as list of paths, and, if return_infos is True, a tuple composed by the solution and a
        struct with output information.
        """

    @staticmethod
    def generate_output_infos( generated_nodes, expanded_nodes, computation_time):
        """
        Return a struct with the output information.
        """
        return {
            "generated_nodes": generated_nodes,
            "expanded_nodes": expanded_nodes,
            "computation_time": computation_time
        }
