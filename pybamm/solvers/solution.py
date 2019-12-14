#
# Solution class
#
import numpy as np
import pickle
import pybamm


class Solution(object):
    """
    Class containing the solution of, and various attributes associated with, a PyBaMM
    model.

    Parameters
    ----------
    t : :class:`numpy.array`, size (n,)
        A one-dimensional array containing the times at which the solution is evaluated
    y : :class:`numpy.array`, size (m, n)
        A two-dimensional array containing the values of the solution. y[i, :] is the
        vector of solutions at time t[i].
    t_event : :class:`numpy.array`, size (1,)
        A zero-dimensional array containing the time at which the event happens.
    y_event : :class:`numpy.array`, size (m,)
        A one-dimensional array containing the value of the solution at the time when
        the event happens.
    termination : str
        String to indicate why the solution terminated

    """

    def __init__(self, t, y, t_event=None, y_event=None, termination="final time"):
        self.t = t
        self.y = y
        self.t_event = t_event
        self.y_event = y_event
        self.termination = termination
        # initialize empty inputs and model, to be populated later
        self.inputs = {}
        self.model = pybamm.BaseModel()

        # initiaize empty variables
        self._variables = {}

    @property
    def t(self):
        "Times at which the solution is evaluated"
        return self._t

    @t.setter
    def t(self, value):
        "Updates the solution times"
        self._t = value

    @property
    def y(self):
        "Values of the solution"
        return self._y

    @y.setter
    def y(self, value):
        "Updates the solution values"
        self._y = value

    @property
    def inputs(self):
        "Values of the inputs"
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        "Updates the input values"
        self._inputs = value

    @property
    def model(self):
        "Model used for solution"
        return self._model

    @model.setter
    def model(self, value):
        "Updates the model"
        assert isinstance(value, pybamm.BaseModel)
        self._model = value

    @property
    def t_event(self):
        "Time at which the event happens"
        return self._t_event

    @t_event.setter
    def t_event(self, value):
        "Updates the event time"
        self._t_event = value

    @property
    def y_event(self):
        "Value of the solution at the time of the event"
        return self._y_event

    @y_event.setter
    def y_event(self, value):
        "Updates the solution at the time of the event"
        self._y_event = value

    @property
    def termination(self):
        "Reason for termination"
        return self._termination

    @termination.setter
    def termination(self, value):
        "Updates the reason for termination"
        self._termination = value

    def append(self, solution):
        """
        Appends solution.t and solution.y onto self.t and self.y.
        Note: this process removes the initial time and state of solution to avoid
        duplicate times and states being stored (self.t[-1] is equal to solution.t[0],
        and self.y[:, -1] is equal to solution.y[:, 0]).

        """
        self.t = np.concatenate((self.t, solution.t[1:]))
        self.y = np.concatenate((self.y, solution.y[:, 1:]), axis=1)
        self.inputs = {
            name: np.concatenate((inp, solution.inputs[name][1:]))
            for name, inp in self.inputs.items()
        }
        self.solve_time += solution.solve_time

    @property
    def total_time(self):
        return self.set_up_time + self.solve_time

    def __getitem__(self, key):
        """Read a variable from the solution. Variables are created 'just in time', i.e.
        only when they are called.

        Parameters
        ----------
        key : str
            The name of the variable

        Returns
        -------
        :class:`pybamm.ProcessedVariable`
            A variable that can be evaluated at any time or spatial point. The
            underlying data for this variable is available in its attribute ".data"
        """
        try:
            # Try getting item
            # return it if it exists
            return self._variables[key]
        except KeyError:
            # otherwise create it and then return it
            var = 1
            self._variables[key] = var
            self.data[key] = var.data
            return var

    def save(self, filename):
        """Save the whole solution using pickle"""
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def save_data(self, filename):
        """Save solution data only (raw arrays) using pickle"""
        with open(filename, "wb") as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

