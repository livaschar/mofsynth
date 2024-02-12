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


from dataclasses import dataclass
from enum import unique
import os
import shutil
import subprocess
import pickle
from mofid.run_mofid import cif2mofid
from settings import user_settings, settings_from_file
from general import copy
import re
import openpyxl


def synth_eval(directory):
    
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
    user_dir = os.path.join("./%s" %directory)
    cifs = [item for item in os.listdir(user_dir) if item.endswith(".cif")]
    
    if cifs == []:
        print(f"\nWARNING: No cif was found in: {user_dir}. Please check run.py\n")
        return 0
    
    # Start procedure for each cif
    for i, cif in enumerate(cifs):

        print(f'\n - \033[1;34mMOF under study: {cif[:-4]}\033[m -')

        # Initialize the mof name as an object of MOF class
        mof = MOF(cif[:-4])

        # Check If its already initialized a MOF object
        if os.path.exists(os.path.join(mof.turbomole_path, "linker.xyz")):
            continue

        # Copy .cif and job.sh in the mof directory
        copy(user_dir, mof.init_path, f"{mof.name}.cif")
        copy(Linkers.job_sh_path, mof.sp_path, job_sh)

        # Create supercell, do the fragmentation, distinguish one linker, calculate single point energy
        mof.create_supercell()
        mof.fragmentation()
        mof.obabel()
        mof.single_point()

        # Check if fragmentation procedure found indeed a linker
        fragm_check = mof.check_fragmentation()
        if fragm_check == False:
            question = input(f'Do you want to skip {mof.name}? [y/n]: ')
            if question.lower() == 'y':
                MOF.fault_fragment.append(mof.name)
                MOF.instances.pop()
                continue
            else:
                print(f'Please manually put linkers.cif at this path {os.path.join(mof.fragmentation_path,"Output/MetalOxo")}. When ready please...')
                input('Press Enter to continue')
                mof.fragmentation(rerun = True)
        
        # Check if fragmentation procedure found a smiles code for this linker
        smile_check = mof.check_smiles()
        if smile_check == False:
            question = input(f'Do you want to skip {mof.name}? [y/n]: ')
            if question.lower() == 'y':
                MOF.fault_smiles.append(mof.name)
                MOF.instances.pop()
                continue
            else:
                
                print(f'Please manually write smiles code at {os.path.join(mof.fragmentation_path,"Output/python_smiles_parts.txt")}. When ready please...')
                input('Press Enter to continue')
    
    # Find the unique linkers from the whole set of MOFs
    MOF.find_unique_linkers()

    # Proceed to the optimization procedure of every linker
    for linker in Linkers.instances:
        print(f'\n - \033[1;34mLinker under study: {linker.smiles} of {linker.mof_name}\033[m -')
        print(f'\n \033[1;31mOptimization calculation\033[m')
        linker.optimize(rerun = False)
    
    # Right instances of MOF class
    with open('cifs.pkl', 'wb') as file:
        pickle.dump(MOF.instances, file)
    
    # Right instances of Linkers class
    with open('linkers.pkl', 'wb') as file:
        pickle.dump(Linkers.instances, file)

    if MOF.fault_fragment!=[]:
        with open('fault_fragmentation.txt', 'w') as file:
            for mof_name in MOF.fault_fragment:
                file.write(f'{mof_name}\n')

    if MOF.fault_smiles!=[]:
        with open('fault_smiles.txt', 'w') as file:
            for mof_name in MOF.fault_smiles:
                file.write(f'{mof_name}\n')

    return MOF.instances, Linkers.instances, MOF.fault_fragment, MOF.fault_smiles

def check_opt():
    cifs, linkers = load_objects()

    converged, not_converged = Linkers.check_optimization(linkers)
    
    return(converged, not_converged)

def results():
    cifs, linkers = load_objects()

    Linkers.check_optimization(linkers)

    for linker in Linkers.converged:
        linker.define_linker_opt_energies()
    
    # Best opt for each smiles code. {smile code as keys and value [opt energy, opt_path]}
    energy_dict = Linkers.find_the_best_opt_energies()

    results_list = MOF.analyse(cifs, linkers, energy_dict)

    txt_file_path = write_txt_results(results_list)
    xlsx_file_path = write_xlsx_results(results_list)
    
    return txt_file_path, xlsx_file_path


@dataclass
class MOF:
    src_dir = os.getcwd()

    synth_path = "./Synth_folder"
    linkers_path = os.path.join(synth_path, '_Linkers_')
    results_txt_path = os.path.join(synth_path, 'synth_results.txt')
    results_xlsx_path = os.path.join(synth_path, 'synth_results.xlsx')
    run_str_sp = "bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    
    instances = []
    fault_fragment = []
    fault_smiles = []
    unique_linkers = []
    # linker_smiles, simple_smile might not be needed

    def __init__(self, name):
        MOF.instances.append(self)
        self.name = name
        self.initialize_paths()
 
    def initialize_paths(self):
        self.init_path = os.path.join(MOF.synth_path, self.name)
        self.fragmentation_path = os.path.join(MOF.synth_path, self.name, "fragmentation")
        self.cif2cell_path = os.path.join(MOF.synth_path, self.name, "cif2cell")
        self.obabel_path = os.path.join(MOF.synth_path, self.name, "obabel")
        self.turbomole_path = os.path.join(MOF.synth_path, self.name, "turbomole")
        self.sp_path = os.path.join(self.turbomole_path, "sp")
        self.rmsd_path = os.path.join(self.turbomole_path, "rmsd")
        os.makedirs(self.init_path, exist_ok = True)
        os.makedirs(self.cif2cell_path, exist_ok = True)
        os.makedirs(self.fragmentation_path, exist_ok = True)
        os.makedirs(self.obabel_path, exist_ok = True)
        os.makedirs(self.turbomole_path, exist_ok = True)
        os.makedirs(self.sp_path, exist_ok = True)
        os.makedirs(self.rmsd_path, exist_ok = True)
    

    def create_supercell(self):
        
        copy(self.init_path, self.cif2cell_path, f"{self.name}.cif")
        
        os.chdir(self.cif2cell_path)
       
        command = ["cif2cell", "-f", f"{self.name}.cif", "--supercell=[2,2,2]", "-o", f"{self.name}_supercell.cif", "-p", "cif"]   
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except ModuleNotFoundError:
            raise ModuleNotFoundError
        
        os.chdir(MOF.src_dir)
    
        copy(self.cif2cell_path, self.fragmentation_path, f"{self.name}_supercell.cif")
        
        print(f'\n \033[1;31mSupercell created\033[m ')
    
    def fragmentation(self, rerun = False):

        if rerun == False:
            os.chdir(self.fragmentation_path)
            
            mofid = cif2mofid(f"{self.name}_supercell.cif")
            
            os.chdir(MOF.src_dir)

        copy(os.path.join(self.fragmentation_path,"Output/MetalOxo"), self.obabel_path, "linkers.cif")
        
        print(f'\n \033[1;31mFragmentation done\033[m')

    def obabel(self):
        os.chdir(self.obabel_path)
    
        command = ["obabel", "-icif", "linkers.cif", "-oxyz", "-Olinkers_prom_222.xyz", "-r"]   
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except:
            raise ModuleNotFoundError
    
        os.rename("linkers_prom_222.xyz","linker.xyz")
    
        os.chdir(MOF.src_dir)
    
        copy(self.obabel_path, self.turbomole_path, "linker.xyz")
        
        print(f'\n \033[1;31mObabel done\033[m')
    
    def single_point(self):

        copy(self.turbomole_path, self.sp_path, "linker.xyz")    
        
        """ SINGLE POINT CALCULATION """
        os.chdir(self.sp_path)

        try:
            os.system(MOF.run_str_sp)
        except Exception as e:
            print(f"An error occurred while running the command for turbomole: {str(e)}")

        os.chdir(MOF.src_dir)
        
        print(f'\n \033[1;31mSinlge point linker calculation done\033[m ')
    
    def check_fragmentation(self):
        file_size = os.path.getsize(os.path.join(self.fragmentation_path,"Output/MetalOxo/linkers.cif"))
        if file_size < 550:
            print(f'  \033[1;31mWARNING: Fragmentation workflow did not find any linkers in the supercell."\033[m')
            return False
        print(f'\n \033[1;31m Fragmentation check over\033[m ')
        return True
    
    def check_smiles(self):
        file_size = os.path.getsize(os.path.join(self.fragmentation_path,"Output/python_smiles_parts.txt"))
        if file_size < 10:
            print(f'  \033[1;31mWARNING: Smiles code was not found."\033[m')
            return False
        print(f'\n \033[1;31m Smiles code check over\033[m ')
        return True
    
    @classmethod
    def find_unique_linkers(cls):

        # Iterate through mof instances
        for instance in cls.instances:
            
            # Take the smiles code for this linker
            file = os.path.join(instance.fragmentation_path, 'Output','python_smiles_parts.txt')
            with open(file) as f:
                lines = f.readlines()
            instance.linker_smiles = str(lines[1].split()[-1])
            instance.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', instance.linker_smiles)

            # Save the smiles code in the unique linkers
            if instance.linker_smiles not in cls.unique_linkers:
                cls.unique_linkers.append(instance.linker_smiles)
            
            # Init this linker as a 'Linkers' class object
            Linkers(instance.linker_smiles, instance.name)

            # Copy the linkers.cif and linker.xyz. Try-except because some smiles code are too long and an error pops up
            # try:
            #     copy(os.path.join(instance.fragmentation_path,"Output/MetalOxo"), os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linkers.cif', f'linker_{instance.linker_smiles}.cif')
            #     copy(instance.obabel_path, os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linker.xyz', f'linker_{instance.linker_smiles}.xyz')
            # except:
            copy(os.path.join(instance.fragmentation_path,"Output/MetalOxo"), os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linkers.cif', 'linkers.cif')
            copy(instance.obabel_path, os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linker.xyz', 'linker.xyz')


    @staticmethod
    def analyse(cifs, linkers, dict):
        results_list = []

        for mof in cifs:
            linker = next((obj for obj in linkers if obj.smiles == mof.linker_smiles and obj.mof_name == mof.name), None)

            if linker != None and linker.smiles in dict.keys():
                mof.opt_energy = float(linker.opt_energy)
                de = calc_de(mof, dict)
                rmsd = calc_rmsd(mof, dict)            
            else:
                print(f"Did not find linker for: {mof.name}. Zero values will be appointed")
                mof.opt_energy = 0.
                de = 0.
                rmsd = 0.
                with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if "cycle" in line:
                        mof.sp_energy = float(line.split()[6])
                        break
            
            results_list.append([mof.name, de, de*627.51, rmsd, mof.linker_smiles, mof.sp_energy, mof.opt_energy])
        
        return results_list
            # if linker in Linkers.not_converged:
            #     print(f'Linker optimization is not converged for: {mof.name}. Proceed with caution. Maybe this will be the best optimized linker')



                
@dataclass         
class Linkers:
    
    # Initial parameters that can be changed
    settings_path = os.path.join(os.getcwd(), 'settings.txt')
    job_sh = 'job.sh'
    run_str = 'sbatch job.sh'
    opt_cycles = 1000
    run_str_sp = f"bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    job_sh_path = os.path.join(MOF.src_dir, "Files")

    instances = []
    converged = []
    not_converged = []

    def __init__(self, smiles, mof_name):
        Linkers.instances.append(self)

        self.smiles = smiles
        self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles) # is not used yet
        self.mof_name = mof_name
        self.opt_path = os.path.join(MOF.linkers_path, self.simple_smile, self.mof_name)
        self.opt_energy = 0

        os.makedirs(self.opt_path, exist_ok = True)
    
    @classmethod
    def opt_settings(cls, run_str, opt_cycles, job_sh = None):
        cls.run_str = run_str
        cls.opt_cycles = opt_cycles
        if job_sh != None:
            cls.job_sh = job_sh

    def optimize(self, rerun = False):

        # Must be before os.chdir(self.opt_path)
        if rerun == False:
            copy(Linkers.job_sh_path, self.opt_path, Linkers.job_sh)
        
        os.chdir(self.opt_path)

        if rerun == False:
            try:
                os.system(Linkers.run_str_sp)
            except Exception as e:
                print(f"An error occurred while running the command for turbomole: {str(e)}")
        
        # MIGHT DELETE
        if rerun == True:
            os.rename(f'linker.xyz', 'linker_original.xyz')
            os.rename(f'final.xyz', 'linker.xyz')

        with open("control", 'r') as f:
            lines = f.readlines()
        words = lines[2].split()
        words[0] = str(self.opt_cycles)
        lines[2] = ' '.join(words) +'\n'
        with open("control",'w') as f:
            f.writelines(lines)

        try:
            os.system(Linkers.run_str)
        except Exception as e:
            print(f"An error occurred while running the command for turbomole: {str(e)}")
        
        os.chdir(MOF.src_dir)

    @staticmethod
    def check_optimization(linkers_list):
        Linkers.converged = []
        Linkers.not_converged = []
        custom = []

        for linker in linkers_list:
            if os.path.exists(os.path.join(linker.opt_path, 'not.uffconverged')):
                Linkers.not_converged.append(linker)
            else:
                print(f'\nOptimization converged succesfully for {linker.smiles} [MOF = {linker.mof_name}]')
                Linkers.converged.append(linker)
        
        for linker in Linkers.not_converged:
                print(f'  \033[1;31m\nWARNING: Optimization did not converge for {linker.smiles} [MOF = {linker.mof_name}]\033[m')
                print('Path: ', linker.opt_path, '\n')
                print(' Option 1: Rerun optimization with more cycles\n',
                      f'Option 2: Manually add the uffconverged file and add the energy at the uffenergy file at {linker.opt_path}\n',
                      'Option 3: Skip this instance\n')
                question = input('[1/2/3]: ')
                if question == '1':
                    linker.opt_cycles = input(f'\nPlease specify the number of optimization cycles (Last opt was run with {linker.opt_cycles}): ')
                    linker.optimize(rerun = True)
                elif question == '2':
                    question = input(f'\nManually add the necessary files and values at {linker.opt_path}\n')
                    input('Press ENTER to continue...')
                    custom.append(linker)
                else:
                    pass
        
        if custom != []:
            Linkers.converged.extend(custom)
            Linkers.not_converged = [i for i in Linkers.not_converged if i not in custom]
        
        return Linkers.converged, Linkers.not_converged
    
    def define_linker_opt_energies(self):   
        
        with open(os.path.join(self.opt_path, 'uffenergy')) as f:
            lines = f.readlines()
        self.opt_energy = lines[1].split()[-1]

    
    @classmethod
    def find_the_best_opt_energies(cls):
        energy_dict = {}
        for instance in Linkers.converged:
            if instance.smiles in energy_dict:
                if float(instance.opt_energy) < float(energy_dict[instance.smiles][0]):
                    energy_dict[instance.smiles] = [instance.opt_energy, instance.opt_path]
            else:
                energy_dict[instance.smiles] = [instance.opt_energy, instance.opt_path]
                        
        return energy_dict

def load_objects():
    with open('cifs.pkl', 'rb') as file:
        cifs = pickle.load(file)
    with open('linkers.pkl', 'rb') as file:
        linkers = pickle.load(file)
    
    return cifs, linkers

def calc_de(mof, dict):

    smiles = mof.linker_smiles

    if smiles in dict and dict[smiles] is not None:
        best_opt_energy = dict[smiles][0]

    with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "cycle" in line:
                mof.sp_energy = float(line.split()[6])
                break
    
    mof.de = float(best_opt_energy) - float(mof.sp_energy)
    return mof.de

def calc_rmsd(mof, dict):

    rmsd = []

    smiles = mof.linker_smiles
    

    copy(dict[mof.linker_smiles][1], mof.rmsd_path, 'final.xyz', 'final_opt.xyz')
    copy(mof.sp_path, mof.rmsd_path, 'final.xyz', 'final_sp.xyz')
    
    os.chdir(mof.rmsd_path)

    print(" HEHEHEHEHE", mof.name)
    check = rmsd_p()
    if check == False:
        if input('Error while calculating the -p RMSD instance. Continue? [y/n]: ') == 'y':
            pass
        else:
            return 0

    try:
        for sp in ['final_sp.xyz', 'final_sp_mod.xyz']:
            command = f"calculate_rmsd -e final_opt.xyz {sp}"
            rmsd.append(subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
    
            command = f"calculate_rmsd -e --reorder-method hungarian final_opt.xyz {sp}"
            rmsd.append(subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        
            command = f"calculate_rmsd -e --reorder-method inertia-hungarian final_opt.xyz {sp}"
            rmsd.append(subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        
            command = f"calculate_rmsd -e --reorder-method distance final_opt.xyz {sp}"
            rmsd.append(subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))        
    
    except Exception as e:
        
        print(f"An error occurred while running the command calculate_rmsd: {str(e)}")
        
        return 0, False
    

    
    minimum = float(rmsd[0].stdout)
    for i in rmsd:
        if float(i.stdout) < minimum:
            minimum = float(i.stdout)
            args = i.args

    with open('result.txt', 'w') as file:
        file.write(str(minimum))
        file.write('\n')
        try:
            file.write(args)
        except:
            print(f'Args not found for mof {mof.rmsd_path}')
                
    rmsd_diff = minimum

    try:
        mof.rmsd = float(rmsd_diff)
    except:
        print(" CALCULATING RMSD FOR: ")
        print("MOFNAME: ", mof.name)
        print("SMILES: ", smiles)


    os.chdir(mof.src_dir)

    return mof.rmsd


def rmsd_p(reorder = False, recursion_depth = 0):
    
    # Define a dictionary to map atomic numbers to symbols
    atomic_symbols = {
        0: 'X', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
        11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar',
        19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe',
        27: 'Ni', 28: 'Co', 29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se',
        35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo',
        43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
        51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce',
        59: 'Pr', 60: 'Nd', 61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
        67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W',
        75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb',
        83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
        91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf',
        99: 'Es', 100: 'Fm', 101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg',
        107: 'Bh', 108: 'Hs', 109: 'Mt', 110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl',
        115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og',
    }

    if recursion_depth >= 3:
        print("Recursion depth limit reached. Exiting.")
        return False

    try:
        if reorder == False:
            os.system("calculate_rmsd -p final_opt.xyz final_sp.xyz > final_sp_mod.txt")
        else:
            os.system("calculate_rmsd -p --reorder final_opt.xyz final_sp.xyz > final_sp_mod.txt")

    except Exception as e:
        print(f"An error occurred while running the command calculate_rmsd: {str(e)}")
        return False

    data = []
    with open('final_sp_mod.txt', 'r') as input_file:
        lines = input_file.readlines()

        for line_number, line in enumerate(lines):
            
            atomic_number = 0
            if line_number < 2:
                continue
            
            parts = line.split()
            if parts == []:
                continue

            try:
                atomic_number = int(parts[0])
            except ValueError:
                input_file.close()
                return rmsd_p(reorder=True, recursion_depth=recursion_depth + 1)

            symbol = atomic_symbols.get(atomic_number)
            coordinates = [float(coord) for coord in parts[1:4]]
            data.append((symbol, coordinates))

    with open('final_sp_mod.xyz', 'w') as output_file:
        output_file.write(f"{len(data)}\n")
        output_file.write("\n")
        for symbol, coords in data:
            output_file.write(f"{symbol} {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f}\n")
    
    return True

def write_txt_results(results_list):

    with open(MOF.results_txt_path, "w") as f:
        f.write('{:<50} {:<37} {:<37} {:<30} {:<60} {:<30} {:<30}\n'.format("NAME", "ENERGY_(OPT-SP)_[au]", "ENERGY_(SP-OPT)_[kcal/mol]", "RMSD_[A]", "LINKER_(SMILES)", "Linker_SinglePointEnergy_[au]", "Linker_OptEnergy_[au]"))
        for i in results_list:
            f.write(f"{i[0]:<50} {i[1]:<37.3f} {i[2]:<37.3f} {i[3]:<30.3f} {i[4]:<60} {i[5]:<30.3f} {i[6]:<30.3f}\n")
    return MOF.results_txt_path

        
def write_xlsx_results(results_list):
    
    # Create a new workbook and select the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Write headers
    headers = ["NAME", "ENERGY_(OPT-SP)_[au]", "ENERGY_(SP-OPT)_[kcal/mol]", "RMSD_[A]", "LINKER_(SMILES)", "Linker_SinglePointEnergy_[au]", "Linker_OptEnergy_[au]"]
    sheet.append(headers)

    # Write results
    for result_row in results_list:
        sheet.append(result_row)

    # Save the workbook to the specified Excel file
    workbook.save(MOF.results_xlsx_path)
    
    return MOF.results_xlsx_path




