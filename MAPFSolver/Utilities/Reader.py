import os
import pathlib
import numpy as np


# Dictionary Map Number and corresponding String
MAPS_NAMES_LIST = {
    0: "empty-8-8",             # 8.8
    1: "empty-16-16",           # 16.16
    2: "demo",
    3: "narrow_corridor",       # 2.9
    4: "random-32-32-10",       # 32.32
    5: "room-32-32-4",          # 32.32
    6: "maze-32-32-2",         # 32.32


}


class Reader:

    def __init__(self, map_number=0, scenario_file_number=1):
        self._map_number = map_number
        self._scenario_file_number = scenario_file_number

        self._reload_instances = True  # If False it loads scenario instances already loaded
        #self._change_scenario_instances = False

        self._scenario_instances = None

    def load_map_file(self, occupied_char='@', valid_chars={'@', '.', 'T'}):
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
        if not os.path.isfile(scenario_file_path):
            print(scenario_file_path)
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
        self._map_number = map_number
        self._reload_instances = True



    def set_scenario_file_number(self, scenario_file_number):
        self._scenario_file_number = scenario_file_number
        self._reload_instances = True


def convert_nums(lst):
    for i in range(len(lst)):
        try:
            lst[i] = int(lst[i])
        except ValueError:
            try:
                lst[i] = float(lst[i])
            except ValueError:
                ""
    return lst


def get_scenario_file_path(map_number, scenario_number):
    map_name = MAPS_NAMES_LIST.get(map_number)
    root_path = pathlib.Path(__file__).parent.parent.parent
    scenario_file_path = str(root_path / "Maps/scenarios") + "/" + map_name + "-" + str(
        scenario_number) + ".scen"
    return scenario_file_path

