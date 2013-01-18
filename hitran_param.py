# hitran_param.py

# Christian Hill, 23/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# Defines a class, HITRANParam, to describe a parameter of a radiative
# transition from the HITRAN database, perhaps with an uncertainty and a
# reference.

from lbl.param import Param

class HITRANParam(Param):
    """
    A class, derived from the base Param class, to describe a parameter of
    a radiative transition from the HITRAN database (such as gamma_air, the
    air-broadened half-width), perhaps with an uncertainty and a reference.

    """

    # class attributes:
    # absolute error codes for nu and delta_air:
    abs_err_codes = {'unreported': 0, '> 1 cm-1': 0,
                     '0.1 - 1 cm-1': 1,
                     '0.01 - 0.1 cm-1': 2,
                     '0.001 - 0.01 cm-1': 3,
                     '0.0001 - 0.001 cm-1': 4,
                     '0.00001 - 0.0001 cm-1': 5,
                     '<0.00001 cm-1': 6}

    # the maximum absolute errors (in cm-1) for nu and delta_air: None
    # implies unreported or >1. cm-1 error, not zero error!
    abs_err_max = [None, 1., 0.1, 0.01, 0.001, 0.0001, 0.00001]

    # relative (percentage) error codes for S, gamma_air, gamma_self, and n_air:
    rel_err_codes = {'unreported': 0, 'unavailable': 0,
                     'unreported or unavailable': 0,
                     'default': 1, 'constant': 1,
                     'default or constant': 1,
                     'average': 2, 'estimate': 2,
                     'average or estimate': 2,
                     '>20%': 3,
                     '10% - 20%': 4,
                     '5% - 10%': 5,
                     '2% - 5%': 6,
                     '1% - 2%': 7,
                     '<1%': 8}

    # the maximum fractional errors for S, A (implied), gamma_air, gamma_self,
    # and n_air: None implies unreported or 'default' error, not zero error!
    rel_err_max = [None, None, None, None, 0.2, 0.1, 0.05, 0.02, 0.01]

    def __init__(self, val, err=None, ref=None, name=None, ierr=None,
                 rerr=None, relative=False, source_id=None):
        """
        Initialize an instance of the HITRANParam class. Initialization is
        as for the base Param class, except that the integer ierr argument
        represents the HITRAN error code and relative is a boolean argument
        which is True if ierr refers to a relative error and False if it
        refers to an absolute error. rerr is the relative (ie fractional
        error).

        """

        Param.__init__(self, val, err, ref, name)
        self.ierr = ierr
        self.relative = relative
        self.comment = None
        if self.relative:
            if self.ierr == 1:
                self.comment = 'default or constant'
            elif self.ierr == 2:
                self.comment = 'average or estimate'

        if self.err is None:
            if self.ierr is not None and not self.relative:
                self.set_abs_err()

        if self.relative:
            self.set_rel_err()
        self.source_id = source_id

    def set_ierr(self):
        if self.err is None or self.val is None:
            return
        self.ierr = 0
        if self.relative:
            if self.val == 0.:
                return
            self.rerr = self.err / abs(self.val)
            for i,e in reversed(list(enumerate(self.rel_err_max[4:]))):
                if self.rerr < e:
                    self.ierr = i+4
                    break
        else:
            for i,e in reversed(list(enumerate(self.abs_err_max[1:]))):
                if self.err < e:
                    self.ierr = i+1
                    break

    def set_abs_err(self):
        """
        Set the absolute error, self.err, from the HITRAN integer error code,
        ierr.

        """

        if 0 < self.ierr <= 6:
            self.err = HITRANParam.abs_err_max[self.ierr]
        else:
            self.err = None

    def set_rel_err(self):
        """
        Set the relative error, self.rerr, from the HITRAN integer error
        code, ierr.

        """

        if 3 < self.ierr <= 8:
            self.rerr = HITRANParam.rel_err_max[self.ierr]
            self.err = abs(self.val) * self.rerr
        else:
            self.rerr = None
            self.err = None

    def get_rel_err(self, fmt=None, percent=False):
        """
        Return the relative error as a string formatted by the fmt argument.
        If percent is True, return the percentage error; otherwise it is the
        fractional error that is returned.

        """

        if percent:
            rerr = self.rerr * 100.
        else:
            rerr = self.rerr

        if fmt is None:
            return str(rerr)

        return fmt % rerr

    def get_ierr(self):
        """ Get the HITRAN-style integer error code for this parameter """

        if self.ierr is not None:
            return self.ierr

        if self.relative:
            return self.get_rel_ierr()
        return self.get_abs_ierr()

