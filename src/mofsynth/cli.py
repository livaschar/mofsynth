
import os
import argparse
from . __init__ import __version__ as version


def _return_cli_parser():
    
    parser = argparse.ArgumentParser(
            prog='mofsynth-cli',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Access synthesizability from a directory containig ``.cif`` files.',
            epilog='''A command line utility based on the MOFSynth package.'''
            )

    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
        
    parser.add_argument('function', help='The function to be called. Choices: main, check_opt, export_results')

    parser.add_argument('directory')

    
    return parser


def _transaction_summary(args):
    col_size, _ = os.get_terminal_size()

    gap = col_size // 6
    num_cifs = len([i for i in os.listdir(args.directory) if i.endswith('.cif')])

    
    print('\nTransaction Summary')
    # print(
    #     f'{"# CIFs":<{gap}}', f'{"Grid size":<{gap}}',
    #     f'{"Cutoff":<{gap}}', f'{"Epsilon":<{gap}}',
    #     f'{"Sigma":<{gap}}', f'{"Cubic-box":>{gap}}',
    #     sep=''
    #     )
    print(col_size*"=")
    print('\nReading from directory:')
    print(f'  \033[1;31m{args.directory}\033[m')
    print(f'\nCalculate for:')
    print(f'  \033[1;31m{num_cifs}\033[m')
    print('\nExecuting the Function')
    print(f'  \033[1;31m{args.function}\033[m')
    print(col_size*"=")