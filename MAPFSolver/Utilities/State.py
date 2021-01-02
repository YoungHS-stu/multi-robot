import abc


class State(object):
    """
    Abstract class for singleAgent and MultiAgents
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, parent=None):
        """
        Initialize the state. If it is a child node, the parent state must be passed.
        :param parent:
        """
        self._g = None
        self._h = None
        if parent is not None:
            self._time_step = parent.time_step()+1
        else:
            self._time_step = 0

        self._parent = parent

    def parent(self):
        return self._parent

    def g_value(self):

        return self._g

    def h_value(self):
        return self._h

    def f_value(self):
        return self._g + self._h

    def is_root(self):
        return self._parent is None

    def set_time_step(self, ts):
        self._time_step = ts

    def time_step(self):
        return self._time_step


    @abc.abstractmethod
    def expand(self):
        """expand current state according to problemInstance"""

    @abc.abstractmethod
    def goal_test(self):
        """test if state is goal state"""

    @abc.abstractmethod
    def compute_heuristics(self):
        """Set hValue"""

    @abc.abstractmethod
    def compute_cost(self):
        """Calculate gValue"""
