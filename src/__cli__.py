import os
import argparse
from __init__ import __version__ as version

def _return_cli_parser():
    parser = argparse.ArgumentParser(
            prog='MOF-Synth',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Analyse the synthesizability of MOFs.',
            epilog='''A command line utility based on the MOF-Synth package.'''
            )

    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    
    # Add an argument for the function to be called with default value
    parser.add_argument('function', default = "start", help='The function to be called. Choices: start or analyse ')

    # Add an argument for the folder name
    parser.add_argument('directory', nargs='?', default = "sample", help="The folder name in which all cif files are stored")
    
    return parser

def _transaction_summary(args):
    
    if args.directory!="":
        num_cifs = len([i for i in os.listdir(args.directory) if i.endswith('.cif')])
        
        print(f'\nWorkflow for:')    
        print(f'  \033[1;31m{num_cifs} CIFs\033[m')
        
        print('\nReading from directory:')
        print(f'  \033[1;31m{args.directory}\033[m')
    else:
        print('\nReading from directory:')
        print(f'  \033[1;31mDirectory not specified\033[m')

    print('\nExecuting the Function')
    print(f'  \033[1;31m{args.function}\033[m')

