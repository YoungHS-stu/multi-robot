import pathlib
from .Visualize import Visualize
from MAPFSolver import *
from MAPFSolver.Utilities.SolverSettings import SolverSettings
from MAPFSolver.Utilities.Reader import Reader, MAPS_NAMES_LIST
#from GUI.start_simulation import prepare_simulation
from GUI.macros import *
from tkinter import *
from PIL import Image, ImageTk

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
    frame.update()
    window.initialize_window()



class StartMenu:
    """
    This class represent the GUIdd start menu. On the GUIdd you can select the desired settings in order to visualize the
    MAPF simulation.
    """

    def __init__(self):
        """
        Initialize the start menu of the GUIdd
        """
        self.font_titles = ("Helvetica", 13)
        self.pady_titles = 5
        self.color_titles = "purple"

        # Root: root frame for the gui
        self.root = Tk()
        self.root.title("MULTI AGENT PATH FINDING SIMULATOR by 【杨鸿申 and 宋浩瑞】")
        self.root.maxsize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.root.resizable(False, False)

        # Variables
        self.map_images_list = []
        self.random_images_list = []
        self.buttons_list = []
        self.goal_occupation_time_down_button = None
        self.goal_occupation_time_up_button = None
        self.reader = Reader()

        # GUIdd selectable variables
        self.waiting_var = StringVar()
        self.selected_algorithm_var = StringVar()
        self.independence_detection_var = BooleanVar()
        self.selected_map_var = IntVar()
        self.selected_heuristic_var = StringVar()
        self.selected_objective_function_var = StringVar()
        self.selected_goal_occupation_time = IntVar()
        self.selected_n_of_agents = IntVar()
        self.selected_scene_number = IntVar()
        self.time_out_var = IntVar()

        self.initialize_variables()

        # Frame: external frame inside the root
        self.frame = Frame(self.root, width=MAIN_WINDOW_WIDTH, height=MAIN_WINDOW_HEIGHT)
        self.frame.pack()

        # Settings Frame: placed in the left part of the Frame, it contains all the settings that can be selected
        self.settings_frame = Frame(self.frame, width=SETTINGS_FRAME_WIDTH, height=SETTINGS_FRAME_HEIGHT)
        self.settings_frame.pack_propagate(False)
        self.settings_frame.bind("<Button-1>", self.callback)
        self.settings_frame.pack(fill=Y, expand=False, side=LEFT)

        # Simulation Frame: placed in the right part of the frame, it will display the MAPF simulation
        self.simulation_frame = Frame(self.frame, width=SIMULATION_FRAME_WIDTH_AND_HEIGHT,
                                      height=SIMULATION_FRAME_WIDTH_AND_HEIGHT, highlightbackground="#AAAAAA",
                                      highlightthickness=1)
        self.simulation_frame.pack_propagate(False)
        self.simulation_frame.pack(fill=None, expand=False, side=LEFT)

        # Choose Map Frame: placed in the left part of the Settings Frame, it contains all the possible maps
        self.choose_map_frame = Frame(self.settings_frame)
        self.choose_map_frame.bind("<Button-1>", self.callback)
        self.choose_map_frame.pack(fill=Y, padx=10, pady=2, side=LEFT)

        # Choose Map Canvas: placed inside the Choose Map Frame
        self.choose_map_canvas = Canvas(self.choose_map_frame, width="165")
        self.choose_map_canvas.pack(fill=Y, padx=10, pady=2, side=LEFT)

        self.choose_map_frame_initialization()

        # Algorithm Settings Frame: placed in the right part of the Settings Frame, it contains all the settings
        self.algorithm_settings_frame = Frame(self.settings_frame)
        self.algorithm_settings_frame.bind("<Button-1>", self.callback)
        self.algorithm_settings_frame.pack(fill=Y, padx=20, pady=5, side=LEFT)

        self.algorithm_settings_frame_initialization()

        self.do_loop()

    def callback(self, event):
        self.frame.focus_set()

    def initialize_variables(self):
        """
        Initialize the widgets values.
        """
        self.selected_algorithm_var.set("Cooperative A*")
        self.independence_detection_var.set(False)
        self.selected_map_var.set(0)
        self.selected_heuristic_var.set("Manhattan")
        self.selected_objective_function_var.set("SOC")
        self.selected_goal_occupation_time.set(1)
        self.selected_n_of_agents.set(5)
        self.selected_scene_number.set(1)


        self.time_out_var.set(0)
        self.waiting_var.set("")

    def choose_map_frame_initialization(self):
        """
        Initialize the Choose Map Frame, which containing the list of all the possible selectable maps as Radiobuttons
        and with a scrollbar for a better visualization.
        """
        # Set up Scrollbar
        scrollbar = Scrollbar(self.choose_map_frame, command=self.choose_map_canvas.yview)
        scrollbar.pack(side=RIGHT, fill='y')

        self.choose_map_canvas.configure(yscrollcommand=scrollbar.set)
        self.choose_map_canvas.bind('<Configure>', self.on_configure)

        # Frame that will contains all the widgets
        frame = Frame(self.choose_map_canvas)
        self.choose_map_canvas.create_window((0, 0), window=frame, anchor='nw')

        # Map Label
        lbl_title = Label(frame, text="MAP", font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, ipady=self.pady_titles)

        for map_number in MAPS_NAMES_LIST:
            png_path = "./Maps/pngs/" + MAPS_NAMES_LIST[map_number] + ".png"
            load = Image.open(png_path)
            load = load.resize((90, 90), Image.ANTIALIAS)
            self.map_images_list.append(ImageTk.PhotoImage(load))


        # Maps Radiobuttons
        for i, img in enumerate(self.map_images_list):
            width = 100
            b = Radiobutton(frame, image=img, height=80, width=width, variable=self.selected_map_var, borderwidth=0,
                            value=i, command=self.set_reader_map)
            self.buttons_list.append(b)
            b.pack(anchor=W)

    def set_reader_map(self):
        self.reader.set_map(self.selected_map_var.get())

    def on_configure(self, event):
        self.choose_map_canvas.configure(scrollregion=self.choose_map_canvas.bbox('all'))

    def algorithm_settings_frame_initialization(self):
        """
        Initialize the Algorithm Settings Frame, which containing the selection of the algorithm, the independence
        detection options, the heuristics, the permanence time and the number of agents
        """
        # Algorithm Label
        lbl_title = Label(self.algorithm_settings_frame, text="ALGORITHM", font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, ipady=self.pady_titles)

        # Algorithm Radiobuttons
        for text, mode in ALGORITHMS_MODES:
            b = Radiobutton(self.algorithm_settings_frame, text=text,
                            variable=self.selected_algorithm_var,
                            borderwidth=0, value=mode)
            self.buttons_list.append(b)
            b.pack(anchor=W)

        # Independence Detection Checkbutton
        # id_button = Checkbutton(self.algorithm_settings_frame, text="Independence Detection",
        #                         variable=self.independence_detection_var, onvalue=True, offvalue=False)
        # self.buttons_list.append(id_button)
        # id_button.pack(anchor=W, pady=(self.pady_titles, 0))

        # Heuristics Label
        lbl_title = Label(self.algorithm_settings_frame, text="HEURISTICS", font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, pady=self.pady_titles)

        heuristic_label = Label(self.algorithm_settings_frame,text="Manhattan Distance")
        heuristic_label.pack(anchor=W)


        # Objective Function Label
        lbl_title = Label(self.algorithm_settings_frame, text="OBJECTIVE FUNCTION", font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, pady=self.pady_titles)

        # Objective function Radiobuttons
        for text, mode in OBJECTIVE_FUNCTION_MODES:
            b = Radiobutton(self.algorithm_settings_frame, text=text, variable=self.selected_objective_function_var,
                            borderwidth=0, value=mode)
            self.buttons_list.append(b)

            b.pack(anchor=W)


        # Scene Selection Label
        lbl_title = Label(self.algorithm_settings_frame, text="SCENE SELECTION (TYPE AND FILE NUMBER)",
                          font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, pady=self.pady_titles)

        # Scene Selection Canvas
        scene_selection_canvas = Canvas(self.algorithm_settings_frame)
        scene_selection_canvas.pack(fill=X)
        self.initialize_scene_selection_canvas(scene_selection_canvas)

        # Number of Agents Label
        lbl_title = Label(self.algorithm_settings_frame, text="NUMBER OF AGENTS",
                          font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, pady=self.pady_titles)

        # Number of Agents Canvas
        number_of_agents_canvas = Canvas(self.algorithm_settings_frame)
        number_of_agents_canvas.pack(fill=X)
        self.initialize_n_of_agents_canvas(number_of_agents_canvas)

        # Edge Conflicts Label
        lbl_title = Label(self.algorithm_settings_frame, text="EDGE CONFLICTS", font=self.font_titles, fg=self.color_titles)
        lbl_title.pack(anchor=W, pady=self.pady_titles)

    

        # Time out Label
        time_out_label = Label(self.algorithm_settings_frame, text="TIME OUT", font=self.font_titles, fg=self.color_titles)
        time_out_label.pack(anchor=W, pady=self.pady_titles)

        # Time out canvas
        time_out_canvas = Canvas(self.algorithm_settings_frame, highlightthickness=0)
        time_out_canvas.pack(fill=X)
        self.initialize_time_out_canvas(time_out_canvas)

        # Prepare Button
        prepare_button = Button(self.algorithm_settings_frame, text="PREPARE", command=self.prepare_simulation_function)
        self.buttons_list.append(prepare_button)
        prepare_button.pack(anchor=E, pady=self.pady_titles*2)

    def fun(self):
        print(self.time_out_var.get())

    def initialize_scene_selection_canvas(self, canvas):
        """
        Initialize the Scene Selection Canvas
        """
        # Load button images
        root_path = pathlib.Path(__file__).parent

        arrow_up_img = self.load_image(root_path / "Images/arrow_up.png", (20, 20))
        arrow_down_img = self.load_image(root_path / "Images/arrow_down.png", (20, 20))


        # Scene File Number Down Button
        scene_file_number_down_button = Button(canvas, image=arrow_down_img, command=self.scene_file_number_down_button)
        scene_file_number_down_button.pack(side=LEFT, padx=(10, 15))
        self.buttons_list.append(scene_file_number_down_button)

        # Scene File Number Text
        scene_file_text = Label(canvas, textvariable=self.selected_scene_number, justify=LEFT,
                                font=("Lucida Console", 10))
        scene_file_text.pack(side=LEFT, padx=0)

        # Scene File Number Up Button
        scene_file_number_up_button = Button(canvas, image=arrow_up_img, command=self.scene_file_number_up_button)
        scene_file_number_up_button.pack(side=LEFT, padx=(15, 0))
        self.buttons_list.append(scene_file_number_up_button)

    def initialize_n_of_agents_canvas(self, canvas):
        """
        Initialize the Number of Agents Canvas
        """
        # Load button images
        root_path = pathlib.Path(__file__).parent

        arrow_up_img = self.load_image(root_path / "Images/arrow_up.png", (20, 20))
        arrow_down_img = self.load_image(root_path / "Images/arrow_down.png", (20, 20))

        # Number of Agents Down Button
        n_of_agents_down_button = Button(canvas, image=arrow_down_img, command=self.n_of_agents_down_button)
        n_of_agents_down_button.pack(side=LEFT, padx=(10, 15))
        self.buttons_list.append(n_of_agents_down_button)

        # Number of Agents Text
        n_of_agents_txt = Label(canvas, textvariable=self.selected_n_of_agents, justify=LEFT,
                                font=("Lucida Console", 10))
        n_of_agents_txt.pack(side=LEFT, padx=0)

        # Number of Agents Up Button
        n_of_agents_up_button = Button(canvas, image=arrow_up_img, command=self.n_of_agents_up_button)
        self.buttons_list.append(n_of_agents_up_button)
        n_of_agents_up_button.pack(side=LEFT, padx=(15, 20))


    def initialize_time_out_canvas(self, canvas):
        """
        Initialize the time out Canvas
        """
        # Time out entry
        time_out_entry = Entry(canvas, textvariable=self.time_out_var, width=4, highlightthickness=0)
        self.buttons_list.append(time_out_entry)
        time_out_entry.pack(side=LEFT, padx=0)

        # seconds label
        seconds_lbl = Label(canvas, text="seconds")
        seconds_lbl.pack(side=LEFT, padx=0)

    def prepare_simulation_function(self):
        """
        Launch the simulation and display it on the Simulation Frame.
        """
        # Waiting label
        waiting_lbl = Label(self.simulation_frame, text="Wait for the solution to be computed...")
        waiting_lbl.place(relx=.5, rely=.5, anchor="center")
        self.simulation_frame.update()

        # Disable all the Buttons
        self.disable_settings_buttons()

        # Create an instance of the class SolverSettings
        solver_settings = SolverSettings(self.selected_objective_function_var.get(),
                                         self.selected_goal_occupation_time.get(),
                                         self.time_out_var.get())

        # Prepare to show the simulation on the given frame
        prepare_simulation(self.reader, self.simulation_frame, self.selected_algorithm_var.get(),
                           solver_settings, self.selected_n_of_agents.get())

        # Enable all the Buttons
        try:
            self.enable_settings_buttons()
            waiting_lbl.destroy()
        except TclError:
            exit(-1)


    def scene_file_number_down_button(self):
        if self.selected_scene_number.get() > 1:
            self.selected_scene_number.set(self.selected_scene_number.get()-1)
            self.reader.set_scenario_file_number(self.selected_scene_number.get())

    def scene_file_number_up_button(self):
        if self.selected_scene_number.get() < 5:
            self.selected_scene_number.set(self.selected_scene_number.get()+1)
            self.reader.set_scenario_file_number(self.selected_scene_number.get())

    def n_of_agents_down_button(self):
        if self.selected_n_of_agents.get() > 1:
            self.selected_n_of_agents.set(self.selected_n_of_agents.get()-1)

    def n_of_agents_up_button(self):
        self.selected_n_of_agents.set(self.selected_n_of_agents.get()+1)

    def enable_settings_buttons(self):
        for radio_button in self.buttons_list:
            radio_button.configure(state=NORMAL)


    def disable_settings_buttons(self):
        for button in self.buttons_list:
            button.configure(state=DISABLED)

    def load_image(self, url, size):
        """
        Load an image. It is also stored in the random_images_list otherwise is not visualized on the GUIdd
        :param url: local path to the image
        :param size: desired image size
        :return: the image resized
        """
        load = Image.open(url)
        load = load.resize(size, Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.random_images_list.append(img)
        return img

    def do_loop(self):
        self.frame.mainloop()


