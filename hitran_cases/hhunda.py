# Christian Hill, 17/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HHundA class, derived from the base HundA class, with methods for
# writing and parsing the quantum numbers of diatomic molecules described
# well by the Hund's case (a) coupling scheme from the HITRAN database.

from lbl.hunda import HundA

class HHundA(HundA):
    
    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name != 'F':
            return []

        if self.molec_id == 13:
            # Hyperfine coupling is only resolved for H and D in OH 
            return [('nuclearSpinRef','H1'),]
        elif self.molec_id == 8:
            # Hyperfine coupling resolved for 14N in (14N)(16O)
            return [('nuclearSpinRef','N1'),]
        elif self.molec_id == 18:
            # Hyperfine coupling resolved for 35Cl and 37Cl in ClO
            return [('nuclearSpinRef','Cl1'),]

        print 'Warning! unbound F quantum number'
        return []
