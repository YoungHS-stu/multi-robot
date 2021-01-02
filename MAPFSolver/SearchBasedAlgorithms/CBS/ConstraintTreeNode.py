from MAPFSolver.Utilities.AStar import AStar

def calculate_soc(paths):
    """
    Given the list of paths it return the sum of cost value. Time spent in goal is not considered.
    :param paths: list of paths.
    :param goal_occupation_time: time that the agent will spent in the goal before disappear. Have sense only if stay in
    goal is false.
    :return: sum of costs value.
    """
    if not paths:
        return None

    soc = 0
    for path in paths:
        soc += len(path) - 1

    return soc


def calculate_makespan(paths):
    """
    Given the list of paths it return the makespan value. Time spent in goal is not considered.
    :param paths: list of paths.

    :param goal_occupation_time: time that the agent will spent in the goal before disappear. Have sense only if stay in
    goal is false.
    :return: makespan value.
    """
    if not paths:
        return None

    makespan = max([len(path)-1 for path in paths])
    return makespan

def normalize_paths_lengths(paths):
    """
    It receives a list of paths of different lengths. It normalize all this lengths by adding goal state to all the
    short paths.
    :param paths: paths to update.
    :return: return the updated paths.
    """
    import copy
    max_length = max([len(path) for path in paths])
    new_paths = copy.deepcopy(paths)

    for path in new_paths:
        while len(path) < max_length:
            path.append(path[len(path)-1])

    return new_paths

def check_conflicts_with_type(paths):
    """
    Returns a couple (type of constraint, new children constraints) or None if the state has no conflicts.
    It is used for the CBS algorithm.
    - In case a vertex conflict is found it will returns the two child conflicts:
    Example: (ai, aj, v, t) -> as [(ai, v, t), (aj, v, t)]
    - In case an edge conflict is found it will returns the two child conflicts:
    Example: [(ai, pos_i, pos_f, ts_f), (aj, pos_i, pos_f, ts_f)]
    """
    reservation_table = dict()
    paths = normalize_paths_lengths(paths)

    for ag_i, path in enumerate(paths):
        for ts, pos in enumerate(path):
            if reservation_table.get((pos, ts)) is not None:
                return 'vertex_conflict', [(reservation_table[(pos, ts)], pos, ts), (ag_i, pos, ts)]
            reservation_table[(pos, ts)] = ag_i

    for ag_i, path in enumerate(paths):
        for ts, pos in enumerate(path):
            ag_j = reservation_table.get((pos, ts - 1))  # Agent in the pos position at the previous time step.
            if ag_j is not None and ag_j != ag_i:
                if len(paths[ag_j]) > ts:  # To be sure that the ag_j will still exists in the next time step.
                    if paths[ag_j][ts] == path[ts - 1]:
                        return 'edge_conflict', [(ag_j, paths[ag_j][ts-1], paths[ag_j][ts], ts),
                                                    (ag_i, path[ts-1], path[ts], ts)]
    return None

class ConstraintTreeNode:
    """
    This class represents a single node of the constraint tree.
    """

    def __init__(self, problem_instance, solver_settings, parent=None, vertex_constraints=None, edge_constraints=None,
                 agent_to_recompute=None):
        """
        Initialize the node.
        :param problem_instance: instance of the problem.
        :param solver_settings: settings of the solver.
        :param parent: parent node.
        :param vertex_constraints: list of vertex constraints. They represents the constraints resulting from vertex
        conflicts. Their form is the following: (agent_id, position, time_step)
        :param edge_constraints: list of edge constraints. They represents the constraints resulting from edge
        conflicts. Their form is the following: (agent_id, initial_position, final_position, final_time_step)
        :param agent_to_recompute: is used to speed up the process and avoid to recompute each time the path for each
        agent. if it's not the root and this node change from his predecessor only for a constraint, this represent the
        agent involved in that constraint. In this way we avoid to recompute all the other paths, but we recompute only
        the path of the agent involved.
        """
        self._problem_instance = problem_instance
        self._solver_settings = solver_settings
        self._parent = parent

        self._vertex_constraints = set() if vertex_constraints is None else vertex_constraints
        self._edge_constraints = set() if edge_constraints is None else edge_constraints

        if agent_to_recompute is None:
            self._solution = self.low_level_search()
        else:
            self._solution = parent.solution().copy()
            path = self.single_agent_low_level_search(self._problem_instance.get_agents()[agent_to_recompute])
            self._solution[agent_to_recompute] = path
            if not path:
                self._solution = None

        self._total_cost = self.calculate_cost()

        self.conflict = None

    def low_level_search(self):
        """
        Low level search. For every agent it searches a possible valid path using A* which doesn't violate the set of
        constraints.
        """
        solution = []
        for agent in self._problem_instance.get_agents():
            path = self.single_agent_low_level_search(agent)
            if not path:
                solution = None
                break
            solution.append(path)
        return solution

    def single_agent_low_level_search(self, agent):
        """
        Low level search for a single agent. It searches a possible valid path using A* which doesn't violate the set
        of constraints.
        """
        agent_vertex_constraints = []
        for vertex_constraint in self._vertex_constraints:
            agent_id, pos, ts = vertex_constraint
            if agent_id == agent.get_id():
                agent_vertex_constraints.append((pos, ts))

        agent_edge_constraints = []
        for edge_constraint in self._edge_constraints:
            agent_id, pos_i, pos_f, ts = edge_constraint
            if agent_id == agent.get_id():
                agent_edge_constraints.append((pos_i, pos_f, ts))

        solver = AStar(self._solver_settings)

        path = solver.find_path_with_constraints(self._problem_instance.get_map(), agent.get_start(),
                                                 agent.get_goal(), agent_vertex_constraints, agent_edge_constraints)
        return path

    def expand(self):
        """
        Expand the current state. It generates the two child nodes, once with the conflict constraint added to the first
        agent and the other with the conflict constraint added to the second agent involved in the conflict.
        :return: the two possible next states.
        """
        if self._solution is None:
            # it means that in that state at least a path it's impossible
            # and so it's useless create new states children of that since they will all have
            # the same constraints that make some path impossible to be computed.
            return []

        if self.conflict is None:
            conflict_type, constraints = check_conflicts_with_type(self._solution)
        else:
            conflict_type, constraints = self.conflict

        node_a, node_b = None, None

        if conflict_type == 'vertex_conflict':
            agent, pos, ts = constraints[0]
            constraints_a = self._vertex_constraints.copy()
            constraints_a.add(constraints[0])
            node_a = ConstraintTreeNode(self._problem_instance, self._solver_settings, parent=self,
                                        vertex_constraints=constraints_a,
                                        edge_constraints=self._edge_constraints.copy(), agent_to_recompute=agent)

            agent, pos, ts = constraints[1]
            constraints_b = self._vertex_constraints.copy()
            constraints_b.add(constraints[1])
            node_b = ConstraintTreeNode(self._problem_instance, self._solver_settings, parent=self,
                                        vertex_constraints=constraints_b,
                                        edge_constraints=self._edge_constraints.copy(), agent_to_recompute=agent)

        if conflict_type == 'edge_conflict':
            agent, pos_i, pos_f, ts = constraints[0]
            constraints_a = self._edge_constraints.copy()
            constraints_a.add(constraints[0])
            node_a = ConstraintTreeNode(self._problem_instance, self._solver_settings, parent=self,
                                        vertex_constraints=self._vertex_constraints.copy(),
                                        edge_constraints=constraints_a, agent_to_recompute=agent)

            agent, pos_i, pos_f, ts = constraints[1]
            constraints_b = self._edge_constraints.copy()
            constraints_b.add(constraints[1])
            node_b = ConstraintTreeNode(self._problem_instance, self._solver_settings, parent=self,
                                        vertex_constraints=self._vertex_constraints.copy(),
                                        edge_constraints=constraints_b, agent_to_recompute=agent)

        if node_a._solution is not None and node_b._solution is not None:
            return [node_a, node_b]
        elif node_a._solution is not None:
            return [node_a]
        elif node_b._solution is not None:
            return [node_b]
        else:
            return []

    def calculate_cost(self):
        if self._solver_settings.get_objective_function() == "SOC":
            return calculate_soc(self._solution)
        if self._solver_settings.get_objective_function() == "Makespan":
            return calculate_makespan(self._solution)

    def total_cost(self):
        """
        Return the cost of the node.
        """
        return self._total_cost

    def vertex_constraints(self):
        """
        Return the list of vertex constraints of the node.
        """
        return self._vertex_constraints

    def edge_constraints(self):
        """
        Return the list of the edge constraints of the node.
        """
        return self._edge_constraints

    def is_valid(self):
        """
        Returns True if the solution of the node is valid i.e.the set of paths for all agents have no conflicts
        """
        if self._solution is None:
            return False

        self.conflict = check_conflicts_with_type(self._solution)

        if self.conflict is None:
            return True
        else:
            return False

    def solution(self):
        return self._solution

    def __str__(self):
        string = '[Constraints:' + str(self._vertex_constraints) + \
                 ' Transactional constraints:' + str(self._edge_constraints) + \
                 ' Total Cost:' + str(self._total_cost) + \
                 ' PATH:' + str(self._solution) + ']'
        return string
