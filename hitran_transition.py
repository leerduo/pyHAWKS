# -*- coding: utf-8 -*-
# hitran_transition.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# Defines the HITRANTransition class, an extension of the base class,
# Transition, to describe a radiative transition in the line-by-line part
# of the HITRAN database.

from lbl.transition import Transition
from lbl.state import State
from hitran_param import HITRANParam
import hitran_meta
import xn_utils

class HITRANTransition(Transition):
    """
    An extension of the base class, Transition, to describe a radiative
    transition of the HITRAN database.

    """

    def __init__(self):
        # initialize the base class
        Transition.__init__(self)

        # a duplicate of the .par line, for convenience and speed
        self.par_line = None
        # HITRAN molecule ID:
        self.molec_id = None
        # HITRAN isotopologue ID:
        self.iso_id = None
        # vacuum wavenumber (cm-1)
        self.nu = None
        # line intensity at 296 K(cm-1/(molec.cm-2). NB in the native
        # HITRAN format, this is weighted by isotopologue abundance
        self.Sw = None
        # (Einstein A-coefficient initialised in base class)
        # air-broadened HWHM at 296 K (cm-1.atm-1)
        self.gamma_air = None
        # self-broadened HWHM at 296 K (cm-1.atm-1)
        self.gamma_self = None
        # (lower-state energy initialised in base class)
        # T-dependence exponent for gamma_air
        self.n_air = None
        # air pressure-induced line shift at 296 K (cm-1.atm-1)
        self.delta_air = None

        # global (V) and local (Q) quantum numbers
        self.Vp = None
        self.Vpp = None
        self.Qp = None
        self.Qpp = None

        # the multipole of the transition: 'E1', 'E2', 'M1' for electric
        # dipole, electric quadrupole and magnetic dipole respectively
        self.multipole = None

        # a single-character flag: in the HITRAN2004+ format, '*'
        # signifies that line-mixing data is available for this transition
        self.flag = ' '

        # upper and lower state degeneracies
        self.gp = None
        self.gpp = None

        # the HITRAN case module, for parsing and writing transitions
        # in the native .par format
        self.case_module = None

    @classmethod    # NB Python 2.4+
    def parse_par_line(self, line):
        """
        Parse a text line in (HITRAN2004+) .par format from the HITRAN
        database and construct a HITRANTransition from it, which is
        returned. If something went wrong, return None.

        """

        # strip newline characters such as '\r\n' from the end of line
        line.rstrip()
        if not line:
            # blank line
            return None

        this_trans = HITRANTransition()
        this_trans.par_line = line

        Ierr = line[127:133]
        Iref = line[133:145]
        
        try:
            # HITRAN molecule ID
            this_trans.molec_id = int(line[:2])
            # HITRAN isotopologue ID
            this_trans.iso_id = int(line[2])
            # vacuum wavenumber (cm-1)
            this_trans.nu = HITRANParam(val=float(line[3:15]),
                ref=int(Iref[:2]), name='nu', ierr=int(Ierr[0]))

            # line intensity at 296 K(cm-1/(molec.cm-2). NB in the native
            # HITRAN format, this is weighted by isotopologue abundance
            this_trans.Sw = HITRANParam(val=float(line[15:25]),
                ref=int(Iref[2:4]), name='Sw', ierr=int(Ierr[1]),
                relative=True)

            # Einstein A-coefficient (s-1)
            this_trans.A = HITRANParam(val=float(line[25:35]),
                ref=int(Iref[2:4]), name='A', ierr=int(Ierr[1]), relative=True)
            # air-broadened HWHM at 296 K (cm-1.atm-1)
            this_trans.gamma_air = HITRANParam(val=float(line[35:40]),
                ref=int(Iref[4:6]), name='gamma_air', ierr=int(Ierr[2]),
                relative=True)
            # self-broadened HWHM at 296 K (cm-1.atm-1)
            if line[40:45] != '0.000':
                this_trans.gamma_self = HITRANParam(val=float(line[40:45]),
                    ref=int(Iref[6:8]), name='gamma_self', ierr=int(Ierr[3]),
                    relative=True)
            # lower-state energy (cm-1)
            this_trans.Elower = float(line[45:55])
            # missing lower state energies are indicated by -1.
            if this_trans.Elower < 0.:
                this_trans.Elower = None
            # deduce the upper state energy because nu = Ep - Epp
            if this_trans.Elower is not None:
                this_trans.set_Eupper()
            # T-dependence exponent for gamma_air
            this_trans.n_air = HITRANParam(val=float(line[55:59]),
                ref=int(Iref[8:10]), name='n_air', ierr=int(Ierr[4]),
                relative=True)
            # air pressure-induced line shift at 296 K (cm-1.atm-1)
            # NB missing data is presented as '0.000000'
            if line[59:67] != '0.000000':
                this_trans.delta_air = HITRANParam(val=float(line[59:67]),
                    ref=int(Iref[10:12]), name='delta_air', ierr=int(Ierr[5]))

            # line-mixing flag
            if line[145] != ' ':
                this_trans.flag = line[145]

            # statistical weights for the upper (gp) and lower (gpp) states
            # NB for some reason, these are given as floats. Cast them to
            # integers, but only save them if they are physically meaningful
            gp = int(float(line[146:153]) + 0.1)
            if gp > 0:
                this_trans.gp = gp
            gpp = int(float(line[153:160]) + 0.1)
            if gpp > 0:
                this_trans.gpp = gpp

            # global (V) and local (Q) quantum numbers
            this_trans.Vp = line[67:82]
            this_trans.Vpp = line[82:97]
            this_trans.Qp = line[97:112]
            this_trans.Qpp = line[112:127]

            # parse the quantum numbers into State objects and attach them
            # to the transition; also determine the transition multipole and
            # get a reference to the appropriate HITRAN case module (which
            # implements the get_hitran_quanta() method for writing the
            # states out in the native HITRAN .par format
            this_trans.case_module, this_trans.statep, this_trans.statepp,\
                this_trans.multipole = hitran_meta.get_states(this_trans)

            # XXX error and reference indices
            #this_trans.Ierr = line[127:133]
            #this_trans.parse_Ierr()
            #this_trans.Iref = line[133:145]
            #this_trans.parse_Iref()

        except Exception, e:
            print 'parse error in parse_par_line'
            print e
            print 'The bad line was:'
            print line
            raise       # for debugging
            return None

        return this_trans

    def statep_get(self, qn_name, default=None):
        """
        Get the value of quantum number qn_name for the upper state. If
        the upper state isn't defined return None. If it is, but qn_name
        isn't defined in the upper state, return default.

        """

        if self.statep is None:
            return None
        return self.statep.get(qn_name, default)

    def statepp_get(self, qn_name, default=None):
        """
        Get the value of quantum number qn_name for the lower state. If
        the lower state isn't defined return None. If it is, but qn_name
        isn't defined in the lower state, return default.

        """

        if self.statepp is None:
            return None
        return self.statepp.get(qn_name, default)

    def validate_as_par(self):
        """
        Check the data we have for this line can be turned into the
        HITRAN par_line we read in in the first place.

        """
            
        return self.get_par_str() == self.par_line

    def get_par_str(self):
        """
        Return a version of this line formatted to the .par native
        HITRAN2004+ format.

        """

        s_delta_air = xn_utils.prm_to_str(self.delta_air, '%8.6f', '0.000000')
        s_delta_air = s_delta_air.replace('-0.', '-.')

        s_n_air = xn_utils.prm_to_str(self.n_air, '%4.2f', ' '*4)
        s_n_air = s_n_air.replace('-0.', '-.')

        s_gamma_air = xn_utils.prm_to_str(self.gamma_air, '%5.4f', ' '*5)
        # XXX isn't there a better way?
        s_gamma_air = s_gamma_air.replace('0.', '.')

        s_gamma_self = xn_utils.prm_to_str(self.gamma_self, '%5.3f', '0.000')

        # missing lower energies are indicated with -1.
        s_Elower = xn_utils.to_str(self.Elower, '%10.4f', '   -1.0000')

        # statistical weights (degeneracies) are given as floats
        # and missing values are indicated with 0.0
        if self.gp is None:
            s_gp = '    0.0'
        else:
            s_gp = '%7.1f' % float(self.gp)
        if self.gpp is None:
            s_gpp = '    0.0'
        else:
            s_gpp = '%7.1f' % float(self.gpp)

        # the global and local quanta fields
        if self.case_module is None:
            Vp = Vpp = Qp = Qpp = '?'*15
        else:
            Vp, Vpp, Qp, Qpp = self.case_module.get_hitran_quanta(self)

        # XXX for now, just grab these fields from the original line:
        s_Ierr = self.par_line[127:133]
        s_Iref = self.par_line[133:145]

        s_molec_id = xn_utils.to_str(self.molec_id, '%2d', '??')
        s_iso_id = xn_utils.to_str(self.iso_id, '%1d', '?')
        s_nu = xn_utils.prm_to_str(self.nu, '%12.6f', '?'*12)
        s_Sw = xn_utils.prm_to_str(self.Sw, '%10.3E', '?'*10)
        s_A = xn_utils.prm_to_str(self.A, '%10.3E', '?'*10)

        # this handles the case that self.flag has been set to None when
        # it ought to be ' '
        s_flag = ' '
        if self.flag:
            s_flag = self.flag

        s_trans = ('%s'*19) % (s_molec_id, s_iso_id, s_nu, s_Sw,
            s_A, s_gamma_air, s_gamma_self, s_Elower, s_n_air,
            s_delta_air, Vp, Vpp, Qp, Qpp, s_Ierr, s_Iref, s_flag,
            s_gp, s_gpp)
        return s_trans

    def set_param(self, prm_name, prm_val, fmt):
        """
        Set the parameter prm_name (e.g. 'multipole', 'nu.val',
        'nu.err', 'nu.ref'), making the conversion to int, float or string
        according to the format fmt.

        """

        try:
            #print 'self.%s = %s' % (prm_name, xn_utils.conv_str(fmt, prm_val))
            exec('self.%s = %s' % (prm_name,
                xn_utils.conv_str(fmt, prm_val)))
        except ValueError:
            exec('self.%s = None' % prm_name)

    def get_param_attr(self, prm_name, attr):
        """
        Get the parameter attribute ('val', 'err', 'ref') for parameter
        prm_name.

        """

        try:
            return eval('self.%s.%s' % (prm_name, attr))
        except AttributeError:
            return None
