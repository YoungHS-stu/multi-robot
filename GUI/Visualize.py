from GUI.macros import *
from tkinter import *
import numpy as np
import PIL.ImageTk
import PIL.Image
import pathlib
import copy


class Visualize:

    def __init__(self, problem_instance,  frame, paths, output_infos):
        self._problem_instance = problem_instance
        self._frame = frame
        self._paths = paths
        self._output_infos = output_infos
        self.random_images_list = []
        self._goals_list = [a.get_goal() for a in self._problem_instance.get_agents()]

        self.animation_speed = 10
        self._frame_width, self._frame_height = get_frame_dimension(self._problem_instance.get_map().get_height(),
                                                                    self._problem_instance.get_map().get_width())

        # Visualize Frame: external frame
        self.visualize_frame = Frame(self._frame)
        self.visualize_frame.pack(ipady=5)

        # Visualize Map Canvas: inside the Visualize Frame
        self.visualize_canvas = Canvas(self.visualize_frame)
        self.visualize_canvas.pack(ipady=5)
        self.map_canvas = Canvas(self.visualize_canvas, width=self._frame_width, height=self._frame_height)
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        self.map_canvas.grid_rowconfigure(0, weight=1)
        self.map_canvas.grid_columnconfigure(0, weight=1)

        # Infos and Buttons Canvas
        self.infos_and_buttons_canvas = Canvas(self.visualize_frame)
        self.infos_and_buttons_canvas.pack(fill=X)
        if self._output_infos is not None:
            self.infos_txt_var = StringVar()
            self.infos = Label(self.infos_and_buttons_canvas, textvariable=self.infos_txt_var, justify=LEFT,
                               padx=5, pady=2, font=("Lucida Console", 10))
            self.infos_txt_var.set("N° OF GENERATED NODES: " +
                                   str(self._output_infos["generated_nodes"]) + "\nN° OF EXPANDED NODES: " +
                                   str(self._output_infos["expanded_nodes"]) + "\nCOMPUTATIONAL TIME: " +
                                   str(round(self._output_infos["computation_time"], 4)))
            self.infos.pack(side=LEFT)

        # Quit Button
        self.quit_button = Button(self.infos_and_buttons_canvas, text="QUIT", command=self.quit_function)
        self.quit_button.pack(side=RIGHT)

        # Start Button
        self.start_button = Button(self.infos_and_buttons_canvas, text="START", command=self.start_function)
        self.start_button.pack(side=RIGHT)

        # Reset Button
        self.reset_button = Button(self.infos_and_buttons_canvas, text="RESET", command=self.reset_function)
        self.reset_button.configure(state=DISABLED)
        self.reset_button.pack(side=RIGHT)


        # Time Step Counter
        self.time_step_counter = -1
        self.time_step_txt_var = StringVar()
        self.time_step_txt = Label(self.infos_and_buttons_canvas, textvariable=self.time_step_txt_var, justify=LEFT,
                                   font=("Lucida Console", 10))
        self.time_step_txt_var.set("TS: " + str(self.time_step_counter))
        self.time_step_txt.pack(side=RIGHT, padx=2)

        # Initialize Variables for Map draiwing
        self.cell_h, self.cell_w = self.get_cell_size()
        self.dynamic_cell_h, self.dynamic_cell_w = self.cell_h, self.cell_w
        self.vis_cells = np.zeros((self._problem_instance.get_map().get_height(),
                                   self._problem_instance.get_map().get_width()), dtype=int)
        self.agents_ovals = []
        self.agents_colors = []
        self.agent_text_list = []

        # For animation
        self.animating = True
        self.path_to_visit = []
        self.steps_count = [N_OF_STEPS] * len(self._problem_instance.get_agents())
        self.x_moves = [0] * len(self._problem_instance.get_agents())
        self.y_moves = [0] * len(self._problem_instance.get_agents())

    def initialize_window(self):
        print("cell_h ",self.cell_h)
        print("cell_w ",self.cell_w)
        print("map height ",self._problem_instance.get_map().get_height())
        print("map width ",self._problem_instance.get_map().get_width())
        self.draw_world()
        self._frame.update()
        self.draw_agents()
        self._frame.update()
        if not self._paths:
            self.start_button.configure(state=DISABLED)

            self.map_canvas.create_text(self._frame_width / 2, self._frame_height / 2, justify=CENTER,
                                        font=("Purisa", 16),
                                        fill="Red", text="PATHS NOT COMPUTED\nThe program is not able to compute the "
                                                         "solution\nin the given timeout")
        self.do_loop()


    def start_function(self):
        self.start_button.configure(state=DISABLED)
        self.quit_button.configure(state=DISABLED)
        self.start_animation(self._paths)

    def reset_function(self):
        for widget in self._frame.winfo_children():
            widget.destroy()
        self.__init__(self._problem_instance,  self._frame, self._paths, self._output_infos)
        self.draw_world()
        self.draw_agents()

    def quit_function(self):
        for widget in self._frame.winfo_children():
            widget.destroy()
        self._frame.quit()

    def draw_world(self):
        print("Frame margin ",FRAME_MARGIN)
        n_rows, n_cols = self._problem_instance.get_map().get_height(), self._problem_instance.get_map().get_width()
        for row in range(n_rows):
            for col in range(n_cols):
                self.vis_cells[row][col] = self.map_canvas.create_rectangle(FRAME_MARGIN + self.cell_w * col,
                                                                            FRAME_MARGIN + self.cell_h * row,
                                                                            FRAME_MARGIN + self.cell_w * (col + 1),
                                                                            FRAME_MARGIN + self.cell_h * (row + 1))
                if self._problem_instance.get_map().is_obstacle((col, row)):
                    self.map_canvas.itemconfig(self.vis_cells[row][col], fill='black', width=2)

    def draw_agents(self):
        for i, a in enumerate(self._problem_instance.get_agents()):
            s_col, s_row = a.get_start()
            g_col, g_row = a.get_goal()

            agent_color = COLORS_LIST[i % len(COLORS_LIST)]
            self.agents_colors.append(agent_color)
            self.agents_ovals.append(self.map_canvas.create_oval(FRAME_MARGIN + self.cell_w * s_col,
                                                                 FRAME_MARGIN + self.cell_h * s_row,
                                                                 FRAME_MARGIN + self.cell_w * (s_col + 1),
                                                                 FRAME_MARGIN + self.cell_h * (s_row + 1),
                                                                 outline='black', fill=agent_color))
            self.map_canvas.itemconfig(self.vis_cells[s_row][s_col], fill=agent_color, width=1.5)
            self.map_canvas.itemconfig(self.vis_cells[g_row][g_col], fill=agent_color, stipple="gray50", width=1.5)

            self.agent_text_list.append(self.map_canvas.create_text(FRAME_MARGIN + self.cell_w * s_col + self.cell_w / 2,
                                                                    FRAME_MARGIN + self.cell_h * s_row + self.cell_h / 2,
                                                                    font=("Purisa", 12),
                                                                    text="S"))

            self.agent_text_list.append(self.map_canvas.create_text(FRAME_MARGIN + self.cell_w * g_col + self.cell_w / 2,
                                                                    FRAME_MARGIN + self.cell_h * g_row + self.cell_h / 2,
                                                                    font=("Purisa", 12),
                                                                    text="G"))

    def start_animation(self, paths):
        self.path_to_visit = copy.deepcopy(paths)  # In order to copy by value also the nested lists
        self._frame.after(2000, self.animation_function)

    def animation_function(self):
        if self.animating:
            self._frame.after(int(self.animation_speed), self.animation_function)
            inc_time_step = True
            for i, agent in enumerate(self.agents_ovals):
                if self.steps_count[i] < N_OF_STEPS:
                    self.map_canvas.move(self.agents_ovals[i], self.x_moves[i], self.y_moves[i])
                    self.steps_count[i] += 1
                elif self.path_to_visit[i]:
                    if inc_time_step:
                        self.time_step_counter += 1
                        self.time_step_txt_var.set("TS: " + str(self.time_step_counter))

                        inc_time_step = False
                    current_position = self.path_to_visit[i].pop(0)

                    color = self.agents_colors[i]
                    if current_position not in self._goals_list:  # To not overwrite others goals
                        self.map_canvas.itemconfig(self.vis_cells[current_position[1]][current_position[0]],
                                                   fill=color, stipple="", width=1.5)
                    if self.path_to_visit[i]:
                        next_position = self.path_to_visit[i][0]
                        self.x_moves[i] = float((next_position[0] - current_position[0]) * self.dynamic_cell_w) / N_OF_STEPS
                        self.y_moves[i] = float((next_position[1] - current_position[1]) * self.dynamic_cell_h) / N_OF_STEPS
                        self.map_canvas.move(self.agents_ovals[i], self.x_moves[i], self.y_moves[i])
                        self.steps_count[i] = 1


            if not [i for i in self.path_to_visit if i]:  # For checking that all the arrays are empty
                self.animating = False

        else:
            # Animation ended
            self.start_button.configure(state=DISABLED)
            self.reset_button.configure(state=NORMAL)
            self.quit_button.configure(state=NORMAL)

    def get_cell_size(self):
        avail_h = self._frame_height - 2 * FRAME_MARGIN
        avail_w = self._frame_width - 2 * FRAME_MARGIN
        n_rows, n_cols = self._problem_instance.get_map().get_height(), self._problem_instance.get_map().get_width()
        cell_h = avail_h / n_rows
        cell_w = avail_w / n_cols
        return cell_h, cell_w

    def do_loop(self):
        self._frame.mainloop()

