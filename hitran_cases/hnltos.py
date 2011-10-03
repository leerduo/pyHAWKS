# Christian Hill, 11/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HNltos class, derived from the base Nltos class, with methods for
# writing and parsing the quantum numbers of open-shell non-linear triatomic
# molecules from the HITRAN database.

from lbl.nltos import Nltos

class HNltos(Nltos):
    
    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name != 'F':
            return []

        if self.molec_id == 10:  # NO2
            # hyperfine coupling with 14N
            return [('nuclearSpinRef', 'N1'),]
        if self.molec_id == 33:  # HO2
            # hyperfine coupling with 1H
            return [('nuclearSpinRef', 'H1'),]

        print 'Warning! unbound F quantum number'
        return []
