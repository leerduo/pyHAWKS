# Christian Hill, 31/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HStcs class, derived from the base Stcs class, with methods for
# writing and parsing the quantum numbers of closed-shell symmetric top
# molecules from the HITRAN database.

from lbl.stcs import Stcs
from hcase_globals import vib_qn_patt
import re

class HStcs(Stcs):
    # the canonical order for outputting quantum numbers for states of
    # this 'case'
    ordered_qn_list = ['ElecStateLabel', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6',
                       'v7', 'v8', 'v9', 'v10', 'v11', 'v12',
                       'l', 'vibInv', 'vibSym', 'J', 'K', 'rovibSym', 'F']

    # the Python types for the quantum numbers
    qn_types = {'ElecStateLabel': str,
                'J': int, 'K': int,
                'v1': int, 'v2': int, 'v3': int, 'v4': int,
                'v5': int, 'v6': int, 'v7': int, 'v8': int,
                'v9': int, 'v10': int, 'v11': int, 'v12': int,
                'l': int, 'F': float,
                'vibInv': str,
                'vibSym': str,
                'rovibSym': str}

    def get_qn_xml(self, qn_name):
        """
        Make and return an xml representation of the quantum number qn_name,
        valid to the XML Schema of the 'stcs' case.

        """

        case_prefix = 'stcs'
        qn = self.qns.get(qn_name)
        if qn is None:
            return ''
        xml_attrs = self.serialize_xml_attrs(qn_name)
        # we do it this way to avoid the ugly space before the '>' in the
        # common case that there are no attributes
        if xml_attrs:
            # rename qn_name to its XML tag name if different
            m = re.match(vib_qn_patt, qn_name)
            if m:
                qn_name = 'vi'
            return '<%s:%s %s>%s</%s:%s>' % (case_prefix, qn_name,
                xml_attrs, str(qn), case_prefix, qn_name)
        # no attributes:
        return '<%s:%s>%s</%s:%s>' % (case_prefix, qn_name,
            str(qn), case_prefix, qn_name)

    def get_qn_xml_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name == 'F':
            if self.molec_id == 24: # CH3Cl
                return [('nuclearSpinRef', 'Cl1'),]
            else:
                print 'warning! unbound F quantum number'

        # match to 'v1', 'v2', 'v12', etc.
        m = re.match(vib_qn_patt, qn_name)
        if m:
            return [('mode', '%s' % m.group(1)),]

        if self.molec_id == 27:   # C2H6
            if qn_name == 'rovibSym':
                # symmetry species are given in the G18+ extended
                # permutation-inversion group
                return [('group', 'G18plus'),]

        return []

    def get_qn_attr_tuples(self, qn_name):
        """
        Return a list of (attribute-name, attribute-value) tuples for
        the quantum number qn_name. This is used to add relevant contextual
        meta-data such as ranking labels and references to nuclear spin
        identifiers (for hyperfine quantum numbers).

        """

        if qn_name == 'F':
            if self.molec_id == 24: # CH3Cl
                return [('nuclearSpinRef', 'Cl1'),]
            else:
                print 'warning! unbound F quantum number'
        return []

