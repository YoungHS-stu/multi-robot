MAIN_WINDOW_WIDTH = 1300
MAIN_WINDOW_HEIGHT = 700

SETTINGS_FRAME_WIDTH = 600
SETTINGS_FRAME_HEIGHT = 700

SIMULATION_FRAME_WIDTH_AND_HEIGHT = 700

MAP_FRAME_WIDTH_AND_HEIGHT = SIMULATION_FRAME_WIDTH_AND_HEIGHT-120


def get_frame_dimension(n_row, n_col):
    if n_row > n_col:
        frame_height = MAP_FRAME_WIDTH_AND_HEIGHT
        frame_width = (MAP_FRAME_WIDTH_AND_HEIGHT/n_row) * n_col
    elif n_row < n_col:
        frame_height = (MAP_FRAME_WIDTH_AND_HEIGHT/n_col) * n_row
        frame_width = MAP_FRAME_WIDTH_AND_HEIGHT
    else:
        frame_height = MAP_FRAME_WIDTH_AND_HEIGHT
        frame_width = MAP_FRAME_WIDTH_AND_HEIGHT
    return frame_width, frame_height



ALGORITHMS_MODES = [
    ("A*", "A*"),
    ("M*", "M*"),
    ("Cooperative A*", "Cooperative A*"),
    ("Conflict Based Search", "Conflict Based Search"),
]

OBJECTIVE_FUNCTION_MODES = [
    ("Sum the costs", "SOC"),
    ("Makespan", "Makespan")
]

COLORS_LIST =["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#C0C0C0", "#800000",
              "#808000", "#008000", "#800080", "#008080", "#000080", "#FF7F50", "#FF8C00", "#9ACD32", "#FFC0CB",
              "#F5DEB3", "#D2691E"]

FRAME_MARGIN = 10
N_OF_STEPS = 50  # N of step for a move. (From a cell to another)