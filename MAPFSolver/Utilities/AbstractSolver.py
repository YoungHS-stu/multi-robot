import abc
class AbstractSolver:
    __metaclass__ = abc.ABCMeta

    def __init__(self, solver_settings):
        self._solver_settings = solver_settings

    @abc.abstractmethod
    def solve(self, problem_instance, return_infos=False):
        pass

    @staticmethod
    def generate_output_infos( generated_nodes, expanded_nodes, computation_time):
        return {
            "generated_nodes": generated_nodes,
            "expanded_nodes": expanded_nodes,
            "computation_time": computation_time
        }
