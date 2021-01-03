from .ProblemInstance import ProblemInstance
from .SingleAgentState import SingleAgentState
from .StatesQueue import StatesQueue
from .Agent import Agent


class AStar:

    def __init__(self, solver_settings):
        self._solver_settings = solver_settings
        self._heuristics = None
        self._frontier = []
        self._closed_list = None  # Keep all the states already expanded
        self._closed_list_of_positions = None  # Keep all the positions already visited

    def find_path(self, problem_map, start_pos, goal_pos):
        self.initialize_problem(problem_map, start_pos, goal_pos)

        while not len(self._frontier)==0:
            self._frontier.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)
            cur_state = self._frontier.pop(0)

            if cur_state.goal_test():
                path = cur_state.get_path_to_root()
                goal = cur_state.get_position()
 
                return path

            if cur_state.get_position() not in self._closed_list_of_positions:
                self._closed_list_of_positions.append(cur_state.get_position())
                expanded_nodes = cur_state.expand()
                self._frontier.extend(expanded_nodes)

        return []

    def find_path_with_reservation_table(self, problem_map, start_pos, goal_pos, reservation_table, completed_pos=None):
        self.initialize_problem(problem_map, start_pos, goal_pos)

        while not len(self._frontier)==0:
            self._frontier.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)
            cur_state = self._frontier.pop(0)

            if cur_state.f_value() > 80:
                #print("time limit 100 exceed")
                break

            if cur_state.is_completed():
                return cur_state.get_path_to_root()

            if not self._closed_list.contains_state(cur_state):
                self._closed_list.add(cur_state)
                expanded_nodes = cur_state.expand()

                expanded_nodes_no_conflicts = []
                for state in expanded_nodes:
                    busy_times = reservation_table.get(state.get_position(), [])
                    cur_pos_busy_times = reservation_table.get(cur_state.get_position(), [])

                    # If the position is already occupied.
                    conflict_with_other_agent = state.time_step() in busy_times

                    # If True means that the position is busy due to an agent that occupy his goal forever.
                    conflict_with_goal = state.get_position() in completed_pos and \
                                            state.time_step() >= busy_times[len(busy_times) - 1]

                    # If True means exists another agent already planned that will pass on this position in future.

                    block_previous_agents_when_in_goal = state.goal_test() and not (len(busy_times) == 0) and \
                                                            any(y > state.time_step() for y in busy_times)

                    conflict_with_other_agent = conflict_with_other_agent or conflict_with_goal or \
                                                block_previous_agents_when_in_goal

                    if not conflict_with_other_agent:
                        if not (state.time_step()-1 in busy_times and state.time_step() in cur_pos_busy_times):
                            # not(if the time step before the position was busy and the before position is busy now)
                            expanded_nodes_no_conflicts.append(state)


                self._frontier.extend(expanded_nodes_no_conflicts)

        return []

    def find_path_with_constraints(self, problem_map, start_pos, goal_pos, vertex_constraints, edge_constraints=None):
        self.initialize_problem(problem_map, start_pos, goal_pos)
        if edge_constraints is None:
            edge_constraints = []

        while not len(self._frontier)==0:
            self._frontier.sort(key=lambda x: (x.f_value(), x.h_value()), reverse=False)
            cur_state = self._frontier.pop(0)

            if cur_state.is_completed():
                return cur_state.get_path_to_root()

            if not self._closed_list.contains_state(cur_state):
                self._closed_list.add(cur_state)
                expanded_nodes = cur_state.expand()

                expanded_nodes_no_conflicts = []
                for state in expanded_nodes:
                    if (state.get_position(), state.time_step()) not in vertex_constraints:
                        if (state.parent().get_position(), state.get_position(), state.time_step()) not in \
                                edge_constraints or edge_constraints is None:

                            if state.goal_test():
                                temp_bool = True
                                for pos, ts in vertex_constraints:
                                    if pos == state.get_position() and ts > state.time_step():
                                        temp_bool = False
                                if temp_bool:
                                    expanded_nodes_no_conflicts.append(state)
                            else:
                                expanded_nodes_no_conflicts.append(state)
                self._frontier.extend(expanded_nodes_no_conflicts)

        return []

    def initialize_problem(self, problem_map, start_pos, goal_pos):
        problem_instance = ProblemInstance(problem_map, [Agent(0, start_pos, goal_pos)])
        self._solver_settings.initialize_heuristic(problem_instance)

        self._frontier = []
        self._closed_list = StatesQueue()
        self._closed_list_of_positions = []

        starter_state = SingleAgentState(problem_map, goal_pos, start_pos, self._solver_settings)
        self._frontier.append(starter_state)
