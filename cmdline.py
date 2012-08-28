# command line arguments for pyHAWKS update_db.py
import os
import sys
import argparse
import datetime
import xn_utils
vprint  = xn_utils.vprint

from pyHAWKS_config import SETTINGS_PATH, DATA_DIR
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import Molecule, Iso, RefsMap

parser = argparse.ArgumentParser(description='Update the HITRAN MySQL'
            ' database with a patch from the provided .par file in'
            ' native HITRAN2004+ format')
parser.add_argument('par_file', metavar='<par_file>',
        help='the .par file, and root of the filenames <filestem>.states'
             ' and <filestem>.trans')
parser.add_argument('-p', '--parse_par', dest='parse_par',
        action='store_const', const=True, default=False,
        help='parse .par file to  .states and .trans files and exit')
parser.add_argument('-s', '--stage', dest='stage_upload',
        action='store_const', const=True, default=False,
        help='stage: stage the upload by deciding which new transitions to'
             ' upload and which old transitions to expire')
parser.add_argument('-U', '--upload', dest='upload', action='store_const',
        const=True, default=False,
        help='actually upload the data to the database, expiring existing'\
             ' transitions for this molecule')
parser.add_argument('-u', '--upload_dry_run', dest='dry_run',
        action='store_const', const=True, default=False,
        help='dry-run: create the data structures and SQL INSERT statements'\
             ' but don\'t  actually upload the data to the database')
parser.add_argument('-O', '--overwrite', dest='overwrite',
        action='store_const', const=True, default=False,
        help='overwrite .states and .trans files, if present')
parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, default=3,
        help='set the level of output: 0-5 (0=errors only, 5=very verbose)')

def process_args(args):
    """ Process some of the command line arguments """

    xn_utils.verbosity = args.verbosity
    # check the par_file name is well-formed and exists
    filestem, ext = os.path.splitext(args.par_file)
    if ext not in ('', '.par'):
        print 'par_file must end in .par or be given without extension; I got:'
        print args.par_file
        sys.exit(1)
    args.par_file = '%s.par' % filestem
    if not os.path.exists(args.par_file):
        print 'par_file not found:', par_file
        sys.exit(1)
    args.filestem = os.path.basename(filestem)

    args.mod_date = datetime.date.fromtimestamp(
                        os.path.getmtime(args.par_file))
    args.s_mod_date = args.mod_date.isoformat()
    vprint('From file modification date, taking the from-date to be %s'
                        % args.s_mod_date, 4)

    # the output files will be:
    # $DATA_DIR/<filestem>-YYYY-MM-DD.states and .trans
    # where <filestem> is typically <molec_ID>_hit<yr> with <yr> the 2-digit
    # year of the update, and YYYY-MM-DD is the modification date of the
    # .par file
    args.trans_file = os.path.join(DATA_DIR, '%s.%s.trans'
                                    % (args.filestem, args.s_mod_date))
    args.states_file = os.path.join(DATA_DIR, '%s.%s.states'
                                    % (args.filestem, args.s_mod_date))
    args.db_trans_file = os.path.join(DATA_DIR, '%s.%s.db_trans'
                                    % (args.filestem, args.s_mod_date))
    args.db_trans_file_id = os.path.join(DATA_DIR, '%s.%s.db_trans_id'
                                    % (args.filestem, args.s_mod_date))
    args.db_expire_id = os.path.join(DATA_DIR, '%s.%s.db_expire_id'
                                    % (args.filestem, args.s_mod_date))
    args.trans_file_upload = os.path.join(DATA_DIR, '%s.%s.trans_upload'
                                    % (args.filestem, args.s_mod_date))
    args.diff_file = os.path.join(DATA_DIR, '%s.%s.diff'
                                    % (args.filestem, args.s_mod_date))

    # get the Molecule and Iso objects from the molecID, taken from
    # the par_file filename
    try:
        molecID = int(args.filestem.split('_')[0])
    except:
        print 'couldn\'t parse molecID from filestem %s' % args.filestem
        print 'the filename should start with "<molecID>_"'
        sys.exit(1)
    molecule = Molecule.objects.filter(pk=molecID).get()
    molec_name = molecule.ordinary_formula
    isos = Iso.objects.filter(molecule=molecule).order_by('isoID')

    # map local, HITRAN moledID and isoID to global isotopologue ID
    args.global_iso_ids = {}
    for iso in isos:
        args.global_iso_ids[(iso.molecule.id, iso.isoID)] = iso.id
    # map global isotopologue ID to local, HITRAN molecID and isoID
    args.hitran_ids = {}
    for iso in isos:
        args.hitran_ids[iso.id] = (iso.molecule.id, iso.isoID)

    # get the RefsMap objects for this molecule, which have
    # refID <molec_name>-<prm_name>-<id>, but '+' replaced with p,
    # e.g. NO+ -> NOp
    refs = RefsMap.objects.all().filter(refID__startswith='%s-'
                % molec_name.replace('+','p'))
    # a dictionary of references, keyed by refID, e.g. 'O2-gamma_self-2'
    d_refs = {}
    for ref in refs:
        d_refs[ref.refID]= ref
    vprint('%d references found for %s' % (refs.count(), molec_name))

    return molecule, isos, d_refs
