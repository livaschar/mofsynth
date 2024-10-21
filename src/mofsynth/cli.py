import os
import argparse
from . __init__ import __version__ as version


def _return_cli_parser():
    
    parser = argparse.ArgumentParser(
                                    prog='mofsynth',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description='Access synthesizability from a directory containig ``.cif`` files.',
                                    epilog='''A command line utility based on the MOFSynth package.'''
                                    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
        
    parser.add_argument('function', help='The function to be called. Choices: run, check_opt, export_results')

    parser.add_argument('directory', help='The path to the directory containing all CIF files.')

    parser.add_argument('supercell_limit', nargs='?', default=None, 
                        help='''\
        The maximum length for each edge of the unit cell in Angstroms.
        This limit is used to determine whether a supercell should be created based on the dimensions of the original unit cell.
        If not provided, the supercell creation will not be constrained by a specific limit. A limit helps with speed and convergence''')
    
    return parser


def _transaction_summary(args):
    col_size, _ = os.get_terminal_size()

    gap = col_size // 6
    num_cifs = len([i for i in os.listdir(args.directory) if i.endswith('.cif')])

    
    print('\nTransaction Summary')
    print(col_size*"=")
    print('\nReading from directory:')
    print(f'  \033[1;31m{args.directory}\033[m')
    print(f'\nCalculate for:')
    print(f'  \033[1;31m{num_cifs}\033[m')
    print('\nExecuting the Function')
    print(f'  \033[1;31m{args.function}\033[m')
    if args.supercell_limit is not None:
        print('\nSupercell creation limit set to:')
        print(f'  \033[1;31m{args.supercell_limit}\033[m')

    print(col_size*"=")
