def load_map_from_file(file_path):
    """
    Load the map infos from a .map file.
    :param file_path: path of the file to load.
    :return: a Map object.
    """
    import os
    from .Map import Map

    occupied_char = '@'
    valid_chars = {'@', '.', 'T'}

    if not os.path.isfile(file_path):
        print("Map file not found!")
        exit(-1)
    map_ls = open(file_path, 'r').readlines()
    height = int(map_ls[1].replace("height ", ""))
    width = int(map_ls[2].replace("width ", ""))
    map_ls = map_ls[4:]
    map_ls = [l.replace('\n', '') for l in map_ls]
    occupancy_lst = set()
    assert (len(map_ls) == height)
    for y, l in enumerate(map_ls):
        assert (len(l) == width)
        for x, c in enumerate(l):
            assert (c in valid_chars)
            if c == occupied_char:
                occupancy_lst.add((x, y))

    return Map(height, width, occupancy_lst)


def load_scenario(scene_file_path, map_width, map_height, occupancy_lst, n_of_agents=10):
    """
    Load the instances from the scene file. It Returns a list of n agents.
    :param scene_file_path: path of the scene file to load.
    :param map_width: width of the map.
    :param map_height: height of the map.
    :param occupancy_lst: list of the obstacles in the map.
    :param n_of_agents: number of agents to return.
    """
    import os
    from .Agent import Agent

    if not os.path.isfile(scene_file_path):
        print("Scenario file not found!")
        exit(-1)
    ls = open(scene_file_path, 'r').readlines()
    if "version 1" not in ls[0]:
        print(".scen version type does not match!")
        exit(-1)
    scene_instances = [convert_nums(l.split('\t')) for l in ls[1:]]
    scene_instances.sort(key=lambda e: e[0])

    for i in scene_instances:
        assert (i[2] == map_width)
        assert (i[3] == map_height)

    instances = [((i[4], i[5]), (i[6], i[7])) for i in scene_instances]
    for start, goal in instances:
        assert(start not in occupancy_lst), "Overlapping error"
        assert(goal not in occupancy_lst), "Overlapping error"
    return [Agent(i, a[0], a[1]) for i, a in enumerate(instances[:n_of_agents])]


def convert_nums(lst):
    """
    Convert list of strings into nums.
    :param lst: string to convert.
    :return: list of int or float.
    """
    for i in range(len(lst)):
        try:
            lst[i] = int(lst[i])
        except ValueError:
            try:
                lst[i] = float(lst[i])
            except ValueError:
                ""
    return lst


def load_map(reader):
    """
    Return the map object given the number of the chosen map.
    :param reader: Reader object.
    :return: a Map object.
    """
    from .Map import Map

    print("Loading map...")
    map_width, map_height, occupancy_list = reader.load_map_file()
    print("Map loaded.")

    return Map(map_height, map_width, occupancy_list)


def load_agents(reader, problem_map, n_of_agents):
    """
    Return the Agent list for the specified scene number of the given map and the selected number of agents.
    """
    from .Agent import Agent

    print("Loading scenario file...")
    agents = reader.load_scenario_file(problem_map.get_obstacles_xy(), problem_map.get_width(),
                                       problem_map.get_height(), n_of_agents=n_of_agents)
    print("Scenario loaded.")

    return [Agent(i, a[0], a[1]) for i, a in enumerate(agents)]


def get_free_lst(problem_map):
    """
    Given a map it returns the list of free positions. (no obstacle cells)
    :param problem_map: map of the problem.
    :return: list of positions.
    """
    free_lst = set()

    for x in range(problem_map.get_width()):
        for y in range(problem_map.get_height()):
            if not (x, y) in problem_map.get_obstacles_xy():
                free_lst.add((x, y))

    return free_lst

