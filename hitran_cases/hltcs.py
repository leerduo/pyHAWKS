# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HLtcs class, derived from the base Ltcs class, with methods for
# writing and parsing the quantum numbers of closed-shell linear triatomic
# molecules from the HITRAN database.

from lbl.ltcs import Ltcs

class HLtcs(Ltcs):
    
    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if self.molec_id == 2:  # CO2
            if qn_name == 'F':    # hyperfine coupling with 17O
                return [('nuclearSpinRef','O1'),]

        elif self.molec_id == 23 and qn_name == 'F':  # HCN
            # hyperfine coupling with 14N
            return [('nuclearSpinRef','N1'),]

        return []

    def get_qn_xml_attr_tuples(self, qn_name):
        if self.molec_id == 2 and qn_name == 'r':
            return [('name', 'Fermi resonance rank'),]
        else:
            return self.get_qn_attr_tuples(qn_name)
