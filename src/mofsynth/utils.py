# This file is part of MOF-Synth.
# Copyright (C) 2023 Charalampos G. Livas

# MOF-Synth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import pickle
from . modules.mof import MOF
from . modules.linkers import Linkers
from . modules.other import (copy, settings_from_file,
                             user_settings, load_objects,
                             write_txt_results, write_xlsx_results)

def main(directory, function, supercell_limit):
    r"""
    Runs the specified function based on the provided parameters.

    Parameters
    ----------
    directory : str
        The path to the directory containing CIF files.
    function : str
        Name of the function to run. Supported values: 'main_run', 'check_opt', 'export_results'.

    Raises
    ------
    ValueError
        If an unsupported function name is provided.

    Notes
    -----
    The 'main' function acts as a dispatcher, executing the corresponding functionality
    based on the specified function name.

    Supported Functions:
    - 'main_run': Executes the main_run function with the given directory.
    - 'check_opt': Executes the check_opt function that checks
    which optimization runs are converged.
    - 'export_results': Executes the export_results function and
    creates files with the results.
    """
    if function == 'main_run':
        main_run(directory, supercell_limit)
    elif function == 'check_opt':
        check_opt()
    elif function == 'export_results':
        export_results()
    else:
        print('Wrong function. Aborting...')
        sys.exit()


def main_run(directory, supercell_limit):
    r"""
    Perform the synthesizability evaluation for MOFs in the specified directory.

    Parameters
    ----------
    directory : str
        The directory containing CIF files for synthesizability evaluation.

    Returns
    -------
    Tuple
        A tuple containing instances of MOF and Linkers classes, and lists of MOFs with
        faults in supercell creation and fragmentation procedures.
    """
    # Create the working directory
    os.makedirs("Synth_folder", exist_ok=True)

    # If settings file exists, read settings from there else ask for user input
    if os.path.exists(Linkers.settings_path):
        run_str, job_sh, opt_cycles = settings_from_file(Linkers.settings_path)
    else:
        run_str, job_sh, opt_cycles = user_settings()

    Linkers.opt_settings(run_str, opt_cycles, job_sh)

    print(f'  \033[1;32m\nSTART OF SYNTHESIZABILITY EVALUATION\033[m')

    # A list of cifs from the user soecified directory
    user_dir = os.path.join(f"./{directory}")
    cifs = [item for item in os.listdir(user_dir) if item.endswith(".cif")]

    if cifs == []:
        print(f"\nWARNING: No cif was found in: {user_dir}. Please check run.py\n")
        return 0

    # Start procedure for each cif
    for _, cif in enumerate(cifs):

        print(f'\n - \033[1;34mMOF under study: {cif[:-4]}\033[m -')

        # Initialize the mof name as an object of MOF class
        mof = MOF(cif[:-4])

        # Check if its already initialized a MOF object. Sometimes the code may break in the middle of a run.
        # This serves as a quick way to ignore already analyzed instances.
        if os.path.exists(os.path.join(mof.sp_path, "final.xyz")):
            supercell_check = True
        else:
            # Copy .cif and job.sh in the mof directory
            copy(user_dir, mof.init_path, f"{mof.name}.cif")
            copy(Linkers.job_sh_path, mof.sp_path, job_sh)

            # Create supercell, do the fragmentation, extract one linker,
            # calculate single point energy
            supercell_check, _ = mof.create_supercell(supercell_limit)
            mof.fragmentation()
            mof.obabel()
            mof.single_point()

        # Check if supercell procedure runned correctly
        if supercell_check is False:
            MOF.fault_supercell.append(mof.name)
            MOF.instances.pop()

        # Check if fragmentation procedure found indeed a linker
        fragm_check = mof.check_fragmentation()
        if fragm_check is False:
            MOF.fault_fragment.append(mof.name)
            MOF.instances.pop()

            ''' SKIP FOR NOW '''
            '''
            question = input(f'Do you want to skip {mof.name}? [y/n]: ')
            if question.lower() == 'y':
                MOF.fault_fragment.append(mof.name)
                MOF.instances.pop()
                continue
            else:
                print(f'Please manually put linkers.cif at this path
                {os.path.join(mof.fragmentation_path,"Output/MetalOxo")}. When ready please...')
                input('Press Enter to continue')
                mof.fragmentation(rerun = True)
            '''
            ''' ------------ '''

            ''' SKIP FOR NOW '''
            '''
            question = input(f'Do you want to skip {mof.name}? [y/n]: ')
            if question.lower() == 'y':
                MOF.fault_smiles.append(mof.name)
                MOF.instances.pop()
                continue
            else:
                print(f'Please manually write smiles code at
                {os.path.join(mof.fragmentation_path,"Output/python_smiles_parts.txt")}.
                When ready please...')
                input('Press Enter to continue')
            '''
            ''' ------------ '''

    # Find the unique linkers from the whole set of MOFs
    smiles_id_dict = MOF.find_unique_linkers()

    # Proceed to the optimization procedure of every linker
    for linker in Linkers.instances:
        print(f'\n - \033[1;34mLinker under optimization study: {linker.smiles_code}, of {linker.mof_name}\033[m -')
        linker.optimize(rerun = False)

    # Right instances of MOF class
    with open('cifs.pkl', 'wb') as file:
        pickle.dump(MOF.instances, file)
    
    # Right instances of Linkers class
    with open('linkers.pkl', 'wb') as file:
        pickle.dump(Linkers.instances, file)

    if MOF.fault_fragment != []:
        with open('fault_fragmentation.txt', 'w') as file:
            for mof_name in MOF.fault_fragment:
                file.write(f'{mof_name}\n')

    if MOF.fault_smiles != []:
        with open('fault_smiles.txt', 'w') as file:
            for mof_name in MOF.fault_smiles:
                file.write(f'{mof_name}\n')
    
    with open('smiles_id_dictionary.txt', 'w') as file:
        for key, value in smiles_id_dict.items():
            file.write(f'{key} : {value}\n')

    return MOF.instances, Linkers.instances, MOF.fault_fragment, MOF.fault_smiles



def check_opt():
    r"""
    Check the optimization status of linker molecules.

    Returns
    -------
    Tuple
        A tuple containing lists of converged and not converged linker instances.
    """
    _, linkers, _ = load_objects()

    converged, not_converged = Linkers.check_optimization_status(linkers)
    
    with open('converged.txt', 'w') as f:
        for instance in converged:
            f.write(f"{instance.smiles_code} {instance.mof_name}\n")
        
    with open('not_converged.txt', 'w') as f:
        for instance in not_converged:
            f.write(f"{instance.smiles_code} {instance.mof_name}\n")
    
    return Linkers.converged, Linkers.not_converged
   
def export_results():
    r"""
    Export the results of the synthesizability evaluation.

    Returns
    -------
    Tuple
        A tuple containing file paths for the generated text and Excel result files.
    """
    cifs, linkers, id_smiles_dict= load_objects()

    Linkers.check_optimization_status(linkers)

    for linker in Linkers.converged:
        linker.read_linker_opt_energies()

    # Best opt for each smiles code. {smile code as keys and value [opt energy, opt_path]}
    best_opt_energy_dict = Linkers.define_best_opt_energy()

    results_list = MOF.analyse(cifs, linkers, best_opt_energy_dict, id_smiles_dict)

    write_txt_results(results_list, MOF.results_txt_path)
    write_xlsx_results(results_list, MOF.results_xlsx_path)

    return MOF.results_txt_path, MOF.results_xlsx_path