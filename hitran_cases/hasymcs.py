# Christian Hill, 6/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HAsymcs class, derived from the base Asymcs class, with methods for
# writing and parsing the quantum numbers of closed-shell symmetric top
# molecules from the HITRAN database.

from lbl.asymcs import Asymcs
from hcase_globals import vib_qn_patt
import re

class HAsymcs(Asymcs):
    # the canonical order for outputting quantum numbers for states of
    # this 'case'
    ordered_qn_list = ['ElecStateLabel', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6',
                       'v7', 'v8', 'v9', 'v10', 'v11', 'v12',
                       'J', 'Ka', 'Kc', 'F', 'r', 'n', 'tau']

    # the Python types for the quantum numbers
    qn_types = {'ElecStateLabel': str,
                'J': int, 'Ka': int, 'Kc': int,
                'v1': int, 'v2': int, 'v3': int, 'v4': int,
                'v5': int, 'v6': int, 'v7': int, 'v8': int,
                'v9': int, 'v10': int, 'v11': int, 'v12': int,
                'F': float,
                'r': int, 'n': int, 'tau': int}

    def get_qn_xml(self, qn_name):
        """
        Make and return an xml representation of the quantum number qn_name,
        valid to the XML Schema of the 'asymcs' case.

        """

        case_prefix = 'asymcs'
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
            if qn_name == 'n' or qn_name == 'tau':
                qn_name = 'r'
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
            print 'warning! unbound F quantum number'

        if self.molec_id == 25: # H2O2
            if qn_name == 'n':
                return [('name', 'n'),]
            if qn_name == 'tau':
                return [('name', 'tau'),]

        # match to 'v1', 'v2', 'v12', etc.
        m = re.match(vib_qn_patt, qn_name)
        if m:
            return [('mode', '%s' % m.group(1)),]

        return []

