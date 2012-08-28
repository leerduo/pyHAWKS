# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HNltcs class, derived from the base Nltcs class, with methods for
# writing and parsing the quantum numbers of closed-shell non-linear triatomic
# molecules from the HITRAN database.

from lbl.nltcs import Nltcs

class HNltcs(Nltcs):
    
    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name != 'F':
            return []

        if self.molec_id == 3:  # O3
            if self.local_iso_id == 4:    # (16O)(16O)(17O)
                return [('nuclearSpinRef', 'O3'),]
            if self.local_iso_id == 5:    # (16O)(17O)(16O)
                return [('nuclearSpinRef', 'O2'),]

        print 'Warning! unbound F quantum number'
        return []

    def get_qn_xml_attr_tuples(self, qn_name):
        if self.molec_id == 3 and qn_name == 'r':
            return [('name', 'Vibrational mixing rank'),]
        else:
            return self.get_qn_attr_tuples(qn_name)
