class Agent:

    def __init__(self, id_agent, start, goal):
        self._id = id_agent
        self._start = start
        self._goal = goal

    def get_id(self):
        return self._id

    def get_start(self):
        return self._start

    def get_goal(self):
        return self._goal

    def __str__(self):
        return "Agent(id=" + str(self._id) + ", start=" + str(self._start) + ", goal=" + str(self._goal) + ")"
