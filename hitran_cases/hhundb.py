# Christian Hill, 30/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HHundB class, derived from the base HundB class, with methods for
# writing and parsing the quantum numbers of diatomic molecules described
# well by the Hund's case (b) coupling scheme from the HITRAN database.

from lbl.hundb import HundB

class HHundB(HundB):
    
    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name != 'F':
            return []

        # only (17O) has I>0, and only the 16O17O isotopologue is in
        # HITRAN. The ID of the 17O for this isotopologue is 'O2'
        # in our CML definition of its structure:
        return [('nuclearSpinRef','O2'),]

