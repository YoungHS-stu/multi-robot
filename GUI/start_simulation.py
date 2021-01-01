from .Visualize import Visualize
from MAPFSolver import *


def load_map(reader):
    """
    Return the map object given the number of the chosen map.
    :param reader: Reader object.
    :return: a Map object.
    """
    from MAPFSolver.Utilities.Map import Map

    print("Loading map...")
    map_width, map_height, occupancy_list = reader.load_map_file()
    print("Map loaded.")

    return Map(map_height, map_width, occupancy_list)


def load_agents(reader, problem_map, n_of_agents):
    """
    Return the Agent list for the specified scene number of the given map and the selected number of agents.
    """
    from MAPFSolver.Utilities.Agent import Agent

    print("Loading scenario file...")
    agents = reader.load_scenario_file(problem_map.get_obstacles_xy(), problem_map.get_width(),
                                       problem_map.get_height(), n_of_agents=n_of_agents)
    print("Scenario loaded.")
    return [Agent(i, a[0], a[1]) for i, a in enumerate(agents)]

def get_solver(algorithm_str, solver_settings):
    """
    Return the Solver object for the specified algorithm and relative settings.
    """
    if algorithm_str == "Cooperative A*":
        from MAPFSolver.SearchBasedAlgorithms.CooperativeAStar.CooperativeAStarSolver import CooperativeAStarSolver
        return CooperativeAStarSolver(solver_settings)
    if algorithm_str == "A*":
        from MAPFSolver.SearchBasedAlgorithms.AStar.AStarSolver import AStarSolver
        return AStarSolver(solver_settings)

    if algorithm_str == "Conflict Based Search":
        from MAPFSolver.SearchBasedAlgorithms.CBS.CBSSolver import CBSSolver
        return CBSSolver(solver_settings)
    if algorithm_str == "M*":
        from MAPFSolver.SearchBasedAlgorithms.MStar.MStarSolver import MStarSolver
        return MStarSolver(solver_settings)
    raise ValueError('Algorithm string not exists!')


def prepare_simulation(reader, frame, algorithm_str,  solver_settings, n_of_agents):

    problem_map = load_map(reader)
    agents = load_agents(reader, problem_map, n_of_agents)
    problem_instance = ProblemInstance(problem_map, agents)


    solver = get_solver(algorithm_str, solver_settings)
    print("Solver --> ", solver, "\nSolving...")
    paths, output_infos = solver.solve(problem_instance, verbose=True, return_infos=True)
    print("Solved.")

    plot_on_gui(problem_instance,  frame, paths, output_infos)


def plot_on_gui(problem_instance,  frame, paths=None, output_infos=None):
    """
    Plot the result on GUIdd.
    :param problem_instance: instance of the problem.
    :param solver_settings: settings of the solver.
    :param frame: tkinter frame where display the result.
    :param paths: resulting paths.
    :param output_infos: problem solving results.
    """
    print("In plot_on_gui   ")
    print("problem_instance ", problem_instance)
    print("frame            ", frame)
    print("paths            ", paths)
    print("output_infos     ", output_infos)

    window = Visualize(problem_instance, frame, paths, output_infos)
    window.initialize_window()



