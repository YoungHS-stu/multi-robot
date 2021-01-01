def calculate_soc(paths,  goal_occupation_time):
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


def calculate_makespan(paths, goal_occupation_time):
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
