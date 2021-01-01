import os
import pathlib
import numpy as np


# Dictionary Map Number and corresponding String
MAPS_NAMES_LIST = {
    0: "empty-8-8",             # 8.8
    1: "empty-16-16",           # 16.16
    2: "narrow_corridor",       # 2.9
    3: "random-32-32-10",       # 32.32
    4: "room-32-32-4",          # 32.32
    5: "maze-32-32-2",         # 32.32


}


class Reader:
    """
    This class takes care of the loading of map and agents from the corresponding map files and scenario files.
    In order to load a certain file the methods set_map(), set_scenario_type() and set_scenario_file_number() must be
    called before calling the corresponding load_map_file() or load_scenario_file().
    """

    def __init__(self, map_number=0, scenario_file_number=1):
        """
        Initialize a reader object.
        :param map_number: map number to load.
        :param scenario_type: scenario type to load.
        :param scenario_file_number: scenario file number to load.
        """
        self._map_number = map_number
        self._scenario_file_number = scenario_file_number

        self._reload_instances = True  # If False it loads scenario instances already loaded
        #self._change_scenario_instances = False

        self._scenario_instances = None

    def load_map_file(self, occupied_char='@', valid_chars={'@', '.', 'T'}):
        """
        Load the map infos from a .map file.
        :param occupied_char: Char representing an occupied cell.
        :param valid_chars: chars valid in the map file.
        :return: width of the map, height of the map and the list of the obstacles in the map.
        """
        assert(self._map_number is not None), "Map Number Not Set"

        root_path = pathlib.Path(__file__).parent.parent.parent
        map_path = str(root_path / "Maps/maps/" / MAPS_NAMES_LIST.get(self._map_number)) + ".map"
        print(map_path)
        if not os.path.isfile(map_path):
            print("Map file not found!")
            exit(-1)
        map_ls = open(map_path, 'r').readlines()
        height = int(map_ls[1].replace("height ", ""))
        width = int(map_ls[2].replace("width ", ""))
        map_ls = map_ls[4:]
        map_ls = [l.replace('\n', '') for l in map_ls]
        occupancy_lst = set()
        print("mapls",map_ls)
        print("height: ",height)
        assert(len(map_ls) == height)
        for y, l in enumerate(map_ls):
            assert(len(l) == width)
            for x, c in enumerate(l):
                assert(c in valid_chars)
                if c == occupied_char:
                    occupancy_lst.add((x, y))
        return width, height, occupancy_lst

    def load_scenario_file(self, occupancy_lst, map_width, map_height, n_of_agents=10):
        """
        Load a set of agents from scenario file. This method keep into account those class variables:
        - self._map_number: in order to find the corresponding scenario file.
        - self._scenario_type: the scenario files can be Even or Random.
        - self._scenario_file_number: number of the scenario file to pick.
        - self._reload_instances: this is False if I want to use the already loaded instances. If I've changed map or
                                  scenario this will be True since the instances need to be reloaded. This variable is
                                  useful in order to keep into memory the last instances that could have been loaded
                                  randomly.
        - self._change_scenario_instances: is True if I want to select another bucket of agents from the scenario file
                                           (if Even) or another random bucket from the scenario file(if Random).
        :param occupancy_lst: list of the obstacles.
        :param map_width: width of the map.
        :param map_height: height of the map.
        :param n_of_agents: number of agents to return.
        :return: array of start and destination couples. (Agents starts and goals)
        """
        scenario_file_path = get_scenario_file_path(self._map_number,  self._scenario_file_number)

        if self._reload_instances:
            self.load_instances(scenario_file_path, map_width, map_height)
            self._reload_instances = False



        instances = [((i[4], i[5]), (i[6], i[7])) for i in self._scenario_instances]
        for start, goal in instances:
            assert(start not in occupancy_lst), "Overlapping error"
            assert(goal not in occupancy_lst), "Overlapping error"

        print("INSTANCES: ", instances[:n_of_agents])
        return instances[:n_of_agents]


    def load_instances(self, scenario_file_path, map_width, map_height):
        """
        Load the instances from the scenario file.
        :param scenario_file_path: path of the scenario file to load.
        :param map_width: width of the map.
        :param map_height: height of the map.
        """
        if not os.path.isfile(scenario_file_path):
            print("Scenario file not found!")
            exit(-1)
        ls = open(scenario_file_path, 'r').readlines()
        if "version 1" not in ls[0]:
            print(".scen version type does not match!")
            exit(-1)
        self._scenario_instances = [convert_nums(l.split('\t')) for l in ls[1:]]
        print(self._scenario_instances[:10])
        self._scenario_instances.sort(key=lambda e: e[0])
        print(self._scenario_instances[:10])

        for i in self._scenario_instances:
            assert (i[2] == map_width)
            assert (i[3] == map_height)

    def set_map(self, map_number):
        """
        Set the map number to load.
        :param map_number: map number to set.
        """
        self._map_number = map_number
        self._reload_instances = True



    def set_scenario_file_number(self, scenario_file_number):
        """
        Set the scenario file number to load.
        :param scenario_file_number: scenario file number to set.
        """
        self._scenario_file_number = scenario_file_number
        self._reload_instances = True


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


def get_scenario_file_path(map_number,  scenario_number):
    """
    Given the number of the map, the type and the number of the scenario, it returns the path of the .scen file.
    :param map_number: number of the chosen map.
    :param scenario_type: type of the chosen scenario.
    :param scenario_number: number if the chosen scenario.
    :return: path of the scenario file.
    """
    map_name = MAPS_NAMES_LIST.get(map_number)
    root_path = pathlib.Path(__file__).parent.parent.parent
    scenario_file_path = str(root_path / "Maps/scenarios-") + "even" + "/" + map_name + "-" + "even" + "-" + str(
        scenario_number) + ".scen"
    return scenario_file_path

