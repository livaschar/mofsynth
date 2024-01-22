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
# import openpyxl



hard = ['OPT_tfi_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_stx_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_fog_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_lil_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_tfq_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_lim_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_stj_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_tfb_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_tfa_sym_5_mc_2_sym_3_on_2_NTN_NTN',
'OPT_fog_sym_5_mc_2_sym_3_on_2_L_12_NTN']

# wrong smiles
fault_1 = ['OPT_lim_sym_5_mc_2_sym_3_on_2_NTN_L_12',
           'OPT_phw_sym_5_mc_2_sym_3_on_2_NTN_L_12']
#wrong linker
fault_2 = ['OPT_tfa_sym_5_mc_2_sym_3_on_2_NTN_L_12',
           'OPT_lim_sym_5_mc_2_sym_3_on_2_L_12_NTN']



def synth_eval(directory):
    os.makedirs("Synth_folder", exist_ok=True)
    
    if os.path.exists(Linkers.settings_path):
        run_str, job_sh, opt_cycles = settings_from_file(Linkers.settings_path)
    else:
        pass
        #run_str, job_sh, opt_cycles = user_settings()
    
    run_str, job_sh, opt_cycles = 'sbatch job.sh', 'job.sh', '1000'
    
    Linkers.opt_settings(run_str, opt_cycles, job_sh)
    
    print(f'  \033[1;32m\nSTART OF SYNTHESIZABILITY EVALUATION\033[m')
    
    user_dir = os.path.join("./%s" %directory)
    
    cifs = [item for item in os.listdir(user_dir) if item.endswith(".cif")]
    if cifs == []:
        print("\nWARNING: No cif was found in: %s\n" %user_dir)
        return 0
    
    for i, cif in enumerate(cifs):

        print(f'\n - \033[1;34mCIF under study: {cif[:-4]}\033[m -')

        mof = MOF(cif[:-4])

        if os.path.exists(os.path.join(mof.turbomole_path, "linker.xyz")):
            continue

        copy(user_dir, mof.init_path, f"{mof.name}.cif")
        copy(Linkers.job_sh_path, mof.sp_path, job_sh)

        mof.create_supercell()

        if cif[:-4] in hard:
            os.remove(os.path.join(mof.fragmentation_path, f"{mof.name}_supercell.cif"))
            copy(mof.cif2cell_path, mof.fragmentation_path, f"{mof.name}.cif", f"{mof.name}_supercell.cif")
    
        mof.fragmentation()
        mof.obabel()
        mof.single_point()        
        check = mof.check_fragmentation()
        if check == False:
            question = input('Do you want to skip this MOF? [y/n]: ')
            if question.lower() == 'y':
                MOF.fault_fragment.append(mof)
                MOF.instances.remove(mof)
                del mof
                cifs.remove(mof)
        cifs[i] = mof
        
    MOF.find_unique_linkers()
    
    for linker in Linkers.instances:
        print(f'\n - \033[1;34mLinker under study: {linker.smiles} of {linker.mof_name}\033[m -')
        print(f'\n \033[1;31mOptimization calculation\033[m')
        linker.optimize()
    
    with open('cifs.pkl', 'wb') as file:
        pickle.dump(MOF.instances, file)
    
    with open('linkers.pkl', 'wb') as file:
        pickle.dump(Linkers.instances, file)

    return MOF.instances, Linkers.instances, MOF.fault_fragment

def check_opt():
    cifs, linkers = load_objects()

    converged, not_converged = Linkers.check_optimization(linkers)
    
    return(converged, not_converged)

def results():
    cifs, linkers = load_objects()

    Linkers.check_optimization(linkers)

    for linker in Linkers.converged:
        linker.define_linker_opt_energies()
        Linkers.instances.append(linker)
        # if linker.mof_name in fault_1:
        #     print("FAULT1: ", linker.mof_name)
        #     print("smiles: ", linker.smile)
    
    for linker in linkers:
        if linker.mof_name in fault_1:
            linker.smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
            linker.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', linker.smiles)
        
        if linker.mof_name in fault_2:
            if linker.mof_name == fault_2[0]:
                linker.opt_energy = 0.4145538622 #define manually
                linker.smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
                linker.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', linker.smiles)
            elif linker.mof_name == fault_2[1]:
                linker.opt_energy == 0.5855769699 #define manually
                linker.smiles = '[O-]C(=O)c1ccc(cc1)c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1ccc(cc1)C(=O)[O-]'
                linker.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', linker.smiles)
            
    for mof in cifs:
        if mof.name in fault_1:
            mof.linker_smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
    
        if mof.name in fault_2:
            if mof.name == fault_2[0]:
                mof.linker_smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
            elif mof.name == fault_2[1]:
                mof.linker_smiles = '[O-]C(=O)c1ccc(cc1)c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1ccc(cc1)C(=O)[O-]'        
    
 
    energy_dict = Linkers.find_the_best_opt_energies()

    MOF.analyse(cifs, linkers, energy_dict)
    
    return MOF.results_txt_path


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
    unique_linkers = set()

    def __init__(self, name):
        MOF.instances.append(self)
        self.name = name
        self.initialize_paths()

        # self.linker_smiles = None
        # self.linker_sp_energy = None
        # self.rmsd = None
        # self.de = None
    
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
    
    def fragmentation(self):
    
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
    
    # def turbomole_opt(self, rerun = False):    
    #     """ OPT CALCULATION """
    #     copy(self.turbomole_path, self.opt_path, "linker.xyz")
    #     os.chdir(self.opt_path)
    #     print(f'\n \033[1;31mOptimization calculation\033[m')
    #     if rerun:
    #         os.system('rm *')
    #     run_str_sp = "bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    #     try:
    #         os.system(run_str_sp + " > /dev/null 2>&1")
    #     except Exception as e:
    #         print(f"An error occurred while running the command for turbomole: {str(e)}")
    #     with open("control", 'r') as f:
    #         lines = f.readlines()
    #     words = lines[2].split()
    #     words[0] = str(self.opt_cycles)
    #     lines[2] = ' '.join(words) +'\n'
    #     with open("control",'w') as f:
    #         f.writelines(lines)
    #     try:
    #         os.system(MOF.run_str)
    #     except Exception as e:
    #         print(f"An error occurred while running the command for turbomole: {str(e)}")
    #     os.chdir(MOF.src_dir)
    
    def check_fragmentation(self):
        file_size = os.path.getsize(os.path.join(self.fragmentation_path,"Output/MetalOxo/linkers.cif"))
        if file_size < 550:
            print(f'  \033[1;31mWARNING: Fragmentation workflow did not find any linkers in the supercell."\033[m')
            return False
        print(f'\n \033[1;31m Fragmentation check over\033[m ')
        return True
    
    # @classmethod
    # def check_optimization(cls):
    #     for instance in cls:
    #         if os.path.exists(os.path.join(instance.opt_path, 'not.uffconverged')):
    #             print(f'\nWARNING: Optimization did not converge for {instance.name}\n')
    #             question = input('\nDo you want to rerun the optimization procedure with more cycles? [y/n]: ')
    #             if question == 'y':
    #                 instance.opt_cycles = input(f'\nPlease specify the number of optimization cycles (Last opt was run with {instance.opt_cycles}): ')
    #                 instance.turbomole_opt(True)
    
    @classmethod
    def find_unique_linkers(cls):
        for instance in cls.instances:
            file = os.path.join(instance.fragmentation_path, 'Output','python_smiles_parts.txt')

            with open(file) as f:
                lines = f.readlines()

            instance.linker_smiles = str(lines[1].split()[-1])

            if instance.linker_smiles not in cls.unique_linkers:
                cls.unique_linkers.add(instance.linker_smiles)
            
            linker = Linkers(lines[1].split()[-1], instance.name)

            instance.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', instance.linker_smiles)

            try:
                copy(os.path.join(instance.fragmentation_path,"Output/MetalOxo"), os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linkers.cif', f'linker_{instance.linker_smiles}.cif')
                copy(instance.obabel_path, os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linker.xyz', f'linker_{instance.linker_smiles}.xyz')
            except:
                copy(os.path.join(instance.fragmentation_path,"Output/MetalOxo"), os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linkers.cif', 'linkers.cif')
                copy(instance.obabel_path, os.path.join(MOF.linkers_path,instance.simple_smile, instance.name), 'linker.xyz', 'linker.xyz')

        return Linkers.instances, MOF.unique_linkers


    @staticmethod
    def analyse(cifs, linkers, dict):
        results_list = []

        for mof in cifs:
            linker = next((obj for obj in linkers if obj.smiles == mof.linker_smiles and obj.mof_name == mof.name), None)

            if linker != None:
                de = calc_de(mof, dict)
                rmsd = calc_rmsd(mof, dict)
                results_list.append([mof.name, de, rmsd, mof.linker_smiles, mof.linker_sp_energy])
            else:
                print("DID NOT FOUND LINKER OF MOF: ", mof.name)
                de = 0.
                rmsd = 0.
                with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if "cycle" in line:
                        mof.linker_sp_energy = float(line.split()[6])
                        break
                results_list.append([mof.name, de, rmsd, mof.linker_smiles, mof.linker_sp_energy])

        with open(MOF.results_txt_path,"w") as f:
            f.write('{:<50} {:<37} {:<30} {:<60} {:<30}\n'.format("NAME", "ENERGY (OPT-SP)", "RMSD", "LINKER (SMILES)", "Linker SinglePointEnergy"))
            for i in results_list:
                f.write(f"{i[0]:<50} {i[1]:<37.3f} {i[2]:<30.3f} {i[3]:<60} {i[4]:<30.3f}\n")

        # write_results_to_excel(results_list, MOF.results_xlsx_path)
                
@dataclass         
class Linkers:
    
    # linkers_path = "./Synth_folder/_Linkers_"
    settings_path = os.path.join(os.getcwd(), 'settings.txt')
    job_sh = 'job.sh'
    run_str = 'sbatch job.sh'
    opt_cycles = 1000

    run_str_sp = f"bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    # run_str_sp = "bash -c '/opt/turbomole/7.02/scripts/x2t linker.xyz > coord; /opt/turbomole/7.02/bin/em64t-unknown-linux-gnu/uff; /opt/turbomole/7.02/scripts/t2x -c > final.xyz'"

    # job_sh_path = os.path.join(MOF.src_dir,"MOFSynth", "Files")
    job_sh_path = os.path.join(MOF.src_dir, "Files")
    instances = []
    converged = []
    not_converged = []

    def __init__(self, smiles, mof_name):
        Linkers.instances.append(self)

        self.smiles = smiles
        pattern = re.compile('[^a-zA-Z0-9]')
        self.simple_smile = re.sub(pattern, '', self.smiles)
        
        self.mof_name = mof_name
        self.opt_path = os.path.join(MOF.linkers_path, self.simple_smile, self.mof_name)
        self.opt_energy = 0

        os.makedirs(self.opt_path, exist_ok = True)
    
    @classmethod
    def opt_settings(cls, run_str, opt_cycles, job_sh = None):
        cls.run_str = run_str
        cls.opt_cycles = opt_cycles
        if job_sh!=None:
            cls.job_sh = job_sh

    def optimize(self, rerun = False):

        copy(Linkers.job_sh_path, self.opt_path, Linkers.job_sh)
        
        os.chdir(self.opt_path)
                
        if rerun == False and not os.path.exists('linker.xyz'):
            print(self.opt_path)
            os.rename(f'linker_{self.smiles}.xyz', 'linker.xyz')
        
        try:
            #os.system(Linkers.run_str_sp + " > /dev/null 2>&1")
            os.system(Linkers.run_str_sp)
        except Exception as e:
            print(f"An error occurred while running the command for turbomole: {str(e)}")
        

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

        for linker in linkers_list:
            if os.path.exists(os.path.join(linker.opt_path, 'not.uffconverged')):
                Linkers.not_converged.append(linker)
            else:
                print(f'\nOptimization converged succesfully for {linker.smiles} [MOF = {linker.mof_name}]')
                Linkers.converged.append(linker)
        
        for linker in Linkers.not_converged:
                print(f'\nWARNING: Optimization did not converge for {linker.smiles} [MOF = {linker.mof_name}]')
                question = input('Do you want to rerun the optimization procedure with more cycles? [y/n]: ')
                if question.lower() == 'y':
                    linker.opt_cycles = input(f'Please specify the number of optimization cycles (Last opt was run with {linker.opt_cycles}): ')
                    linker.optimize(True)
        
        return Linkers.converged, Linkers.not_converged
    
    def define_linker_opt_energies(self):       
        
        # define manually
        # if self.mof_name in fault_1:
        #     self.smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
        #     self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles)
        
        # if self.mof_name in fault_2:
        #     if self.mof_name == fault_2[0]:
        #         self.opt_energy = 0.4145538622 #define manually
        #         self.smiles = '[O-]C(=O)c1cc(cc(c1)C(=O)[O-])c1ccc(cc1)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]'
        #         self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles)
        #     elif self.mof_name == fault_2[1]:
        #         self.opt_energy == 0.5855769699 #define manually
        #         self.smiles = '[O-]C(=O)c1ccc(cc1)c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1cc(cc(c1)c1ccc(cc1)C(=O)[O-])c1ccc(cc1)C(=O)[O-]'
        #         self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles)
        #     return
        #####################################

        with open(os.path.join(self.opt_path, 'uffenergy')) as f:
            lines = f.readlines()
        self.opt_energy = lines[1].split()[-1]
    
    @classmethod
    def find_the_best_opt_energies(cls):
        energy_dict = {}
        for instance in cls.instances:
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
        linker_opt_energy = dict[smiles][0]

    with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "cycle" in line:
                mof.linker_sp_energy = float(line.split()[6])
                break
    
    mof.de = float(linker_opt_energy) - float(mof.linker_sp_energy)
    return mof.de

def calc_rmsd(mof, dict):
    

    smiles = mof.linker_smiles
    

    copy(dict[mof.linker_smiles][1], mof.rmsd_path, 'final.xyz', 'final_opt.xyz')
    copy(mof.sp_path, mof.rmsd_path, 'final.xyz', 'final_sp.xyz')
    
    os.chdir(mof.rmsd_path)

    try:
        os.system("calculate_rmsd -e final_sp.xyz final_opt.xyz > result.txt")
    except Exception as e:
        print(f"An error occurred while running the command calculate_rmsd: {str(e)}")
        return 0, False

    with open("result.txt",'r') as rmsd_file:
        for line in rmsd_file:
            rmsd_diff = line.split()[0]
    
    try:
        mof.rmsd = float(rmsd_diff)
    except:
        print(" CALCULATING RMSD FOR: ")
        print("MOFNAME: ", mof.name)
        print("SMILES: ", smiles)


    os.chdir(mof.src_dir)

    return mof.rmsd

# def write_results_to_excel(results_list, excel_file):
#     # Create a new workbook and select the active sheet
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active

#     # Write headers
#     headers = ["NAME", "ENERGY (OPT-SP)", "RMSD", "LINKER (SMILES)", "Linker SinglePointEnergy"]
#     sheet.append(headers)

#     # Write results
#     for result_row in results_list:
#         sheet.append(result_row)

#     # Save the workbook to the specified Excel file
#     workbook.save(excel_file)



# os.system('shopt -s extglob')
# os.system(f'rm * !(linker_{self.smiles}.xyz|linker_{self.smiles}.cif)')


