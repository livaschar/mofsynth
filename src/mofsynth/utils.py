# This file is part of MOF-Synth.
# Copyright (C) 2024 Charalampos G. Livas

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

import re
import os
import sys
import pickle
from pathlib import Path
from . modules.mof import MOF
from . modules.linkers import Linkers
from . modules.other import (copy, config_from_file,
                             load_objects, write_txt_results, write_xlsx_results)

def main(directory, function, supercell_limit):
    r"""
    Acts as a dispatcher, directing the program to execute the specified function.

    Parameters
    ----------
    directory : str
        The path to the directory containing CIF files.
    function : str
        Name of the function to run. Supported values: 'main_run', 'check_opt', 'export_results'.
    supercell_limit: int
        The maximum length for each edge of the unit cell in Angstroms.

    Raises
    ------
    ValueError
        If an unsupported function name is provided.


    Supported Functions:
    - 'main_run': Executes the main_run function reading files from the given directory
    and the supercell limit
    - 'check_opt': Executes the check_opt function that checks
    which optimization runs are converged.
    - 'export_results': Executes the export_results function and
    creates files with the results.
    """
    if function == 'run':
        run(directory, supercell_limit)
    elif function == 'check_opt':
        check_opt(directory)
    elif function == 'export_results':
        export_results(directory)
    else:
        print('Wrong function. Aborting...')
        sys.exit()


def run(directory, supercell_limit):
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

    # Create a Path object from the directory string
    user_dir_temp = Path(directory)
    user_dir = user_dir_temp.resolve()
    # Get the parent directory (root path)
    root_path_temp = user_dir.parent
    root_path = root_path_temp.resolve()
    # Define the new directory path (root_path/Synth_folder)
    synth_folder_path = root_path / "Synth_folder"
    # Create the directory if it doesn't exist
    synth_folder_path.mkdir(parents=True, exist_ok=True)
    
    # If settings file exists, read settings from there else ask for user input
    Linkers.config_directory = root_path / "config_dir"
    if os.path.exists(Linkers.config_directory):
        config_file_path = Linkers.config_directory / "config.yaml"
        Linkers.run_str, Linkers.job_sh, Linkers.opt_cycles = config_from_file(config_file_path)
    else:
        print(f'\033[1;31m\n No configuration file found at {Linkers.config_directory}. Aborting session... \033[m')
        return False
    
    print(f'  \033[1;32m\nSTART OF SYNTHESIZABILITY EVALUATION\033[m')

    # A list of cifs from the user soecified directory
    # cifs = [item for item in os.listdir(user_dir) if item.endswith(".cif")]
    # for cif in cifs:
    #     sanitized_name = re.sub(r'[^a-zA-Z0-9-_]', '_', cif[:-4])
    #     cif_path = user_dir / cif
    #     cif_path.rename(user_dir / sanitized_name)
    
    cifs = []
    for cif in (item for item in user_dir.iterdir() if item.suffix == ".cif"):
        sanitized_name = re.sub(r'[^a-zA-Z0-9-_]', '_', cif.stem)  # Use .stem to get the filename without the extension
        cif.rename(user_dir / f"{sanitized_name}.cif")  # Rename the file with the new sanitized name
        cifs.append(f"{sanitized_name}.cif")
    
    if cifs == []:
        print(f"\n\033[1;31m\n WARNING: No cif was found in: {user_dir}. Aborting session... \033[m")
        return False
    
    MOF.initialize(root_path, synth_folder_path)
    
    
    # Start procedure for each cif
    for _, cif in enumerate(cifs):

        print(f'\n - \033[1;34mMOF under study: {cif[:-4]}\033[m -')
        sanitized_name = re.sub(r'[^a-zA-Z0-9-_]', '_', cif[:-4])

        # Initialize the mof name as an object of MOF class
        mof = MOF(cif[:-4])

        # Check if its already initialized a MOF object. Sometimes the code may break in the middle of a run.
        # This serves as a quick way to ignore already analyzed instances.
        final_xyz_path = mof.sp_path / "final.xyz"        
        if final_xyz_path.exists():
            continue
        else:
            # Copy .cif and job.sh in the mof directory
            copy(user_dir, mof.init_path, f"{mof.name}.cif")
            copy(Linkers.config_directory, mof.sp_path, Linkers.job_sh)

            # Create supercell, do the fragmentation, extract one linker,
            # calculate single point energy
            supercell_check, _ = mof.create_supercell(supercell_limit)
            if supercell_check is False:
                MOF.fault_supercell.append(mof.name)
                MOF.instances.pop()
                continue
            fragm_check, _ = mof.fragmentation()
            if fragm_check is False:
                MOF.fault_fragment.append(mof.name)
                MOF.instances.pop()
                continue            
            obabel_check, _ = mof.obabel()
            if obabel_check is False:
                MOF.instances.pop()
                continue            
            sp_check, _ = mof.single_point()
            if sp_check is False:
                MOF.instances.pop()
                continue 

    # Find the unique linkers from the whole set of MOFs
    smiles_id_dict = MOF.find_unique_linkers()
    
    # Proceed to the optimization procedure of every linker
    for linker in Linkers.instances:
        print(f'\n - \033[1;34mLinker under optimization study: {linker.smiles_code}, of {linker.mof_name}\033[m -')
        linker.optimize(False)
    
    # Right instances of MOF class
    with open(root_path / 'cifs.pkl', 'wb') as file:
        pickle.dump(MOF.instances, file)
        
    # Right instances of Linkers class
    with open(root_path / 'linkers.pkl', 'wb') as file:
        pickle.dump(Linkers.instances, file)

    if MOF.fault_fragment != []:
        with open(root_path / 'fault_fragmentation.txt', 'w') as file:
            for mof_name in MOF.fault_fragment:
                file.write(f'{mof_name}\n')

    if MOF.fault_smiles != []:
        with open(root_path / 'fault_smiles.txt', 'w') as file:
            for mof_name in MOF.fault_smiles:
                file.write(f'{mof_name}\n')
    
    with open(root_path / 'smiles_id_dictionary.txt', 'w') as file:
        for key, value in smiles_id_dict.items():
            file.write(f'{key} : {value}\n')

    return MOF.instances, Linkers.instances, MOF.fault_fragment, MOF.fault_smiles



def check_opt(directory):
    r"""
    Check the optimization status of linker molecules.

    Returns
    -------
    Tuple
        A tuple containing lists of converged and not converged linker instances.
    """
    # Get the parent directory (root path)
    root_path = Path(directory).parent

    _, linkers, _ = load_objects(root_path)

    converged, not_converged = Linkers.check_optimization_status(linkers)
    
    with open(root_path / 'converged.txt', 'w') as f:
        for instance in converged:
            f.write(f"{instance.smiles_code} {instance.mof_name}\n")
        
    with open(root_path / 'not_converged.txt', 'w') as f:
        for instance in not_converged:
            f.write(f"{instance.smiles_code} {instance.mof_name}\n")
    
    return Linkers.converged, Linkers.not_converged
   
def export_results(directory):
    r"""
    Export the results of the synthesizability evaluation.

    Returns
    -------
    Tuple
        A tuple containing file paths for the generated text and Excel result files.
    """
    root_path = Path(directory).parent
    synth_folder_path = root_path / "Synth_folder"
    MOF.initialize(root_path, synth_folder_path)
    cifs, linkers, id_smiles_dict= load_objects(root_path)

    converged, _ = Linkers.check_optimization_status(linkers)

    # Best opt for each smiles code. {smile code as keys and value [opt energy, opt_path]}
    best_opt_energy_dict = Linkers.define_best_opt_energy()

    results_list = MOF.analyse(cifs, linkers, converged, best_opt_energy_dict, id_smiles_dict)

    # write_txt_results(results_list, MOF.results_txt_path)
    write_xlsx_results(results_list, MOF.results_xlsx_path)

    return MOF.results_txt_path, MOF.results_xlsx_path
