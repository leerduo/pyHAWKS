# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The HSphcs class, derived from the base Sphcs class, with methods for
# writing and parsing the quantum numbers of closed-shell spherical top
# molecules from the HITRAN database.

from lbl.sphcs import Sphcs

class HSphcs(Sphcs):
    # the canonical order for outputting quantum numbers for states of
    # this 'case'
    ordered_qn_list = ['ElecStateLabel', 'v1', 'v2', 'v3', 'v4', 'vibSym', 'J',
                       'rovibSym', 'F', 'n', 'alpha']
    # the Python types for the quantum numbers
    qn_types = {'ElecStateLabel': str,
                'J': int,
                'v1': int, 'v2': int, 'v3': int, 'v4': int,
                'vibSym': str,
                'rovibSym': str,
                'n' int, 'alpha' int,
                'F': float}
    
    def get_qn_xml(self, qn_name):
        """
        Make and return an xml representation of the quantum number qn_name,
        valid to the XML Schema of the 'sphcs' case.

        """

        qn = self.qns.get(qn_name)
        if qn is None:
            return ''
        xml_attrs = self.serialize_xml_attrs(qn_name)
        # we do it this way to avoid the ugly space before the '>' in the
        # common case that there are no attributes
        if xml_attrs:
            # rename qn_name to its XML tag name if different
            if qn_name in ('v1', 'v2', 'v3', 'v4'):
                qn_name = 'vi'
            elif qn_name in ('n', 'alpha'):
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

        # For now, deal only with methane
        if qn_name in ('v1', 'v2', 'v3', 'v4'):
            return [('mode', '%s' % qn_name[1]),]
        elif qn_name == 'n':  # vibrational ranking index
            return [('name', 'n'),]
        elif qn_name == 'alpha':  # rotational ranking index
            return [('name', 'alpha'),]
        return []
