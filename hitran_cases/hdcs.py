# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HDcs class, derived from the base Dcs class, with methods for writing
# and parsing the quantum numbers of closed-shell diatomic molecules from
# the HITRAN database.

from lbl.dcs import Dcs

class HDcs(Dcs):

    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name != 'F':
            return []

        if self.molec_id == 15: # HCl
            # F in HCl results from coupling to 35Cl / 37Cl in the
            # HITRAN database; this nucleus is known as 'Cl1'
            return [('nuclearSpinRef', 'Cl1'),]

        if self.molec_id == 16: # HBr
            # F in HBr results from coupling to 79Br / 81Br in the
            # HITRAN database; this nucleus is known as 'Br1'
            return [('nuclearSpinRef', 'Br1',)]

        if self.molec_id == 17:    # HI
            # F in HI results from coupling to 127I
            # HITRAN database; this nucleus is known as 'I1'
            return [('nuclearSpinRef', 'I1'),]

        return []
