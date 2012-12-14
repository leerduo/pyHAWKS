# Christian Hill, 18/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HLpcs class, derived from the base Lpcs class, with methods for
# writing and parsing the quantum numbers of closed-shell linear
# molecules from the HITRAN database.

from lbl.lpcs import Lpcs
from hcase_globals import vib_qn_patt, vib_amqn_patt
import re

class HLpcs(Lpcs):
    # the canonical order for outputting quantum numbers for states of
    # this 'case'
    ordered_qn_list = ['ElecStateLabel', 'v1', 'v2', 'v3', 'v4', 'v5',
                       'v6', 'v7', 'l5', 'l6', 'l7',
                       'l', 'vibInv', 'vibRefl', 'J', 'F', 'r', 'parity',
                       'kronigParity']

    # the Python types for the quantum numbers
    qn_types = {'ElecStateLabel': str,
                'J': int,
                'v1': int, 'v2': int, 'v3': int, 'v4': int,
                'v5': int, 'v6': int, 'v7': int,
                'l5': int, 'l6': int, 'l7': int,
                'l': int, 'F': float, 'r': int, 'vibInv': str,
                'vibRefl': str, 'parity': str, 'kronigParity': str}

    def get_qn_xml(self, qn_name):
        """
        Make and return an xml representation of the quantum number qn_name,
        valid to the XML Schema of the 'asymcs' case.

        """

        case_prefix = 'lpcs'
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
            m = re.match(vib_amqn_patt, qn_name)
            if m:
                qn_name = 'li'
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

        # match to 'v1', 'v2', 'v12', etc.
        m = re.match(vib_qn_patt, qn_name)
        if m:
            return [('mode', '%s' % m.group(1)),]
        m = re.match(vib_amqn_patt, qn_name)
        if m:
            return [('mode', '%s' % m.group(1)),]

        if qn_name == 'r':
            return [('name', 'l-type resonance rank'),]

        return []
