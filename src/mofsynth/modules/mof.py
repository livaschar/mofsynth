
from dataclasses import dataclass
import os
import subprocess
from mofid.run_mofid import cif2mofid
from pymatgen.io.cif import CifWriter
from pymatgen.core.structure import IStructure
from rdkit import Chem
from . other import copy
import numpy as np


@dataclass
class MOF:
    src_dir = os.getcwd()

    synth_path = "./Synth_folder"
    output_file_name = 'synth_results'

    path_to_linkers_directory = os.path.join(synth_path, '_Linkers_')
    results_txt_path = os.path.join(synth_path, f'{output_file_name}.txt')
    results_xlsx_path = os.path.join(synth_path, f'{output_file_name}.xlsx')
    run_str_sp = "bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"

    instances = []
    fault_supercell = []
    fault_fragment = []
    fault_smiles = []    
    smiles_id_dict = {}
    new_instances = []

    def __init__(self, name):
        r"""
        Initialize a new MOF instance.
        
        Parameters
        ----------
        name : str
            The name of the MOF instance.
        
        Explanation
        -----------
        This constructor method initializes a new instance of the 'mof' class with the provided name.
        It adds the newly created instance to the list of instances stored in the 'instances' attribute of the 'MOF' class.
        Additionally, it assigns the provided name to the 'name' attribute of the instance.
        It then calls the '_initialize_paths()' method to set up any necessary paths for the instance.
        Finally, it initializes several attributes, including 'opt_energy', 'sp_energy', 'de', and 'rmsd', with NaN values using NumPy's 'np.nan'.
        
        Example
        -------
        To create a new MOF instance named 'MOF1', you would call the constructor as follows:
            mof_instance = MOF('MOF1')
        This would create a new instance of the 'mof' class with the name 'MOF1', and initialize its attributes accordingly.
        """

        MOF.instances.append(self)
        self.name = name
        self._initialize_paths()
        self.linker_smiles = ''
        self.opt_energy = np.nan
        self.sp_energy = np.nan
        self.de = np.nan
        self.rmsd = np.nan


    def _initialize_paths(self):
        r"""
        Initialize paths for the MOF instance.
        
        Explanation
        -----------
        This method sets up various paths necessary for the operation of the MOF instance.
        It constructs paths for initialization, fragmentation, CIF2Cell, OpenBabel, Turbomole, single point calculations (SP),
        and root-mean-square deviation (RMSD) calculations.
        These paths are derived based on the synthetic path stored in the 'synth_path' attribute of the 'MOF' class
        and the name of the MOF instance.
        Directories corresponding to each path are created if they do not already exist using 'os.makedirs()'.
        
        Example
        -------
        Consider a 'MOF' instance named 'MOF1' with a synthetic path '/path/to/synth'.
        Calling this method on 'MOF1' would create the following directory structure:
            - '/path/to/synth/MOF1'
            - '/path/to/synth/MOF1/fragmentation'
            - '/path/to/synth/MOF1/cif2cell'
            - '/path/to/synth/MOF1/obabel'
            - '/path/to/synth/MOF1/turbomole'
            - '/path/to/synth/MOF1/turbomole/sp'
            - '/path/to/synth/MOF1/turbomole/rmsd'
        """

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
    

    def create_supercell(self, limit):
        r"""
        Create a supercell for the MOF instance.

        Returns
        -------
        bool
            True if the supercell creation is successful, False otherwise.
        """        
        copy(self.init_path, self.cif2cell_path, f"{self.name}.cif")
        
        os.chdir(self.cif2cell_path)
       
        ''' cif2cell way '''
        # command = ["cif2cell", "-f", f"{self.name}.cif", "--supercell=[2,2,2]", "-o", f"{self.name}_supercell.cif", "-p", "cif"]   
        # try:
        #     subprocess.run(command, capture_output=True, text=True, check=True)
        # except ModuleNotFoundError:
        #     raise ModuleNotFoundError
        ''' ----------- '''

        ''' pymatgen way '''
        try:
            structure = IStructure.from_file(f"{self.name}.cif")
            if limit is not None and all(cell_length > 30 for cell_length in structure.lattice.abc):
                os.rename(f"{self.name}.cif",f"{self.name}_supercell.cif")
            else:
                supercell = structure*2
                w = CifWriter(supercell)
                w.write_file(f"{self.name}_supercell.cif")
        except:
            return False
        ''' ----------- '''

        os.chdir(MOF.src_dir)

        copy(self.cif2cell_path, self.fragmentation_path, f"{self.name}_supercell.cif")

        return True, f"{self.name}_supercell.cif"

    def fragmentation(self, rerun = False):
        r"""
        Perform the fragmentation process for the MOF instance.

        Parameters
        ----------
        rerun : bool, optional
            If True, rerun the fragmentation process, by default False.

        Notes
        -----
        The function relies on the `cif2mofid` and `copy` functions.

        """
        if rerun == False:
            os.chdir(self.fragmentation_path)

            mofid = cif2mofid(f"{self.name}_supercell.cif")

            os.chdir(MOF.src_dir)

        copy(os.path.join(self.fragmentation_path,"Output/MetalOxo"), self.obabel_path, "linkers.cif")
 
    def obabel(self):
        r"""
        Convert the linkers.cif file to XYZ and MOL formats and keep the longest linker contained in CIF file.

        Raises
        ------
        ModuleNotFoundError
            If Open Babel is not found in the system.

        Notes
        -----
        This function uses the Open Babel tool.

        """        
        
        os.chdir(self.obabel_path)

        ''' CIF TO XYZ '''
        command = ["obabel", "-icif", "linkers.cif", "-oxyz", "-Olinkers_prom_222.xyz", "-r"]   
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except:
            raise ModuleNotFoundError
    
        os.rename("linkers_prom_222.xyz","linker.xyz")
        ''' ----------- '''

        ''' CIF TO MOL '''
        command = ["obabel", "-icif", "linkers.cif", "-omol", "-Olinkers_prom_222.mol", "-r"]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except:
            raise ModuleNotFoundError
        ''' ----------- '''
    
        os.chdir(MOF.src_dir)
    
        copy(self.obabel_path, self.turbomole_path, "linker.xyz")
            
    def single_point(self):
        r"""
        Perform a single-point calculation using Turbomole.

        Raises
        ------
        Exception
            If an error occurs while running the Turbomole command.

        Notes
        -----
        This function executes a Turbomole command for single-point calculation.
        The Turbomole command is specified by the `run_str_sp` attribute.

        """

        copy(self.turbomole_path, self.sp_path, "linker.xyz")

        """ SINGLE POINT CALCULATION """
        os.chdir(self.sp_path)

        try:
            os.system(MOF.run_str_sp)
        except Exception as e:
            print(f"An error occurred while running the command for turbomole: {str(e)}")

        os.chdir(MOF.src_dir)


    def check_fragmentation(self):
        r"""
        Check if the fragmentation workflow successfully found any linkers in the supercell.

        Returns
        -------
        bool
            True if linkers are found, False otherwise.

        Notes
        -----
        This function checks the size of the linkers.cif file generated by the fragmentation workflow.
        If the file size is less than 550, it indicates that no linkers were found.

        """        
        file_size = os.path.getsize(os.path.join(self.fragmentation_path,"Output/MetalOxo/linkers.cif"))
        if file_size < 550:
            # print(f'  \033[1;31mWARNING: Fragmentation workflow did not find any linkers in the supercell."\033[m')
            return False
        # print(f'\n \033[1;31m Fragmentation check over\033[m ')
        return True
    
    def check_smiles(self):
        r"""
        Check if the Smiles code file was successfully generated during the fragmentation process.

        Returns
        -------
        bool
            True if Smiles code file is found, False otherwise.

        Notes
        -----
        This function checks the size of the python_smiles_parts.txt file generated by the fragmentation workflow.
        If the file size is less than 10, it indicates that the Smiles code was not found.

        """        
        file_size = os.path.getsize(os.path.join(self.fragmentation_path,"Output/python_smiles_parts.txt"))
        if file_size < 10:
            # print(f'  \033[1;31mWARNING: Smiles code was not found."\033[m')
            return False
        # print(f'\n \033[1;31m Smiles code check over\033[m ')
        return True


    def find_smiles_fragm(fragmentation_path):
        r"""
        Extract Smiles codes from the python_smiles_parts.txt file generated during fragmentation.

        Parameters
        ----------
        fragmentation_path : str
            Path to the directory containing the fragmentation output.

        Returns
        -------
        Tuple[List[str], int]
            A tuple containing a list of Smiles codes and the total number of linkers found.

        Notes
        -----
        This function reads the python_smiles_parts.txt file in the specified `fragmentation_path` directory
        and extracts Smiles codes associated with linkers. The function returns a list of Smiles codes and the
        total number of linkers found.

        """        
        smiles = []

        file = os.path.join(fragmentation_path, 'Output','python_smiles_parts.txt')

        with open(file) as f:
            lines = f.readlines()

        for line in lines:
            if line.split()[0] == 'linker':
                number_of_linkers += 1
                smiles.append(str(lines[1].split()[-1]))

        return smiles, number_of_linkers

    def find_smiles_obabel(obabel_path):
        r"""
        Extract Smiles code from the obabel-generated Mol file.

        Parameters
        ----------
        obabel_path : str
            Path to the directory containing the obabel output.

        Returns
        -------
        str or None
            The Smiles code if found, otherwise None.

        Notes
        -----
        This function changes the current working directory to the specified `obabel_path`, reads the
        linkers_prom_222.mol file, and attempts to extract the Smiles code using RDKit. If successful,
        it returns the Smiles code; otherwise, it returns None.

        """

        os.chdir(obabel_path)

        smiles = None
        
        mol = Chem.MolFromMolFile('linkers_prom_222.mol')
        
        if mol is not None:
            smiles = Chem.MolToSmiles(mol)
        else:
            print("Error: The RDKit molecule is None.")

        os.chdir(MOF.src_dir)
        
        return smiles


    @classmethod
    def find_unique_linkers(cls):
        r"""
        Process MOF instances to assign unique identifiers to their SMILES codes and organize data for linkers.
        
        Returns
        -------
        Tuple
            A tuple containing two dictionaries: `smiles_id_dictionary` mapping SMILES codes to unique identifiers,
            and `id_smiles_dictionary` mapping unique identifiers to SMILES codes.
        
        Explanation
        -----------
        This code block iterates through each MOF instance stored in the class's `instances` attribute.
        For each instance, it attempts to extract the SMILES code using the `find_smiles_obabel` method from the `MOF` class.
        If extraction is successful, the instance is appended to a list named `new_instances`. If extraction fails,
        the instance's name is added to a list named `fault_smiles`, and processing continues to the next instance.
        
        For instances with successfully extracted SMILES codes, the block assigns a unique identifier to each SMILES code
        if it's not already present in the `smiles_id_dictionary`.
        The unique identifier is a numerical value incremented for each new SMILES code encountered.
        The mapping of SMILES codes to unique identifiers is stored in `smiles_id_dictionary`,
        while the reverse mapping is stored in `id_smiles_dictionary`.
        
        Additionally, the block performs several operations:
        - It sets the `linker_smiles` attribute of each instance to its corresponding unique identifier from `smiles_id_dictionary`.
        - It creates `Linkers` objects for each instance using the instance's `linker_smiles` and name.
        - It copies certain files from the instance's directories to a new location based on the linker's SMILES code.
        
        Finally, the block updates the class's list of instances to contain only the instances for which the SMILES code
        was successfully extracted, and returns the `smiles_id_dictionary` and `id_smiles_dictionary`.
        
        Note
        ----
        This code block modifies class attributes directly and performs file operations outside of its scope.
        Ensure proper class and file management within the calling context.
        
        Example
        -------
        Consider a class `MOFProcessor` with several MOF instances stored in its `instances` attribute.
        Executing this code block would process each instance, assign unique identifiers to SMILES codes,
        organize data, and return the resulting dictionaries.
        """

        from . linkers import Linkers

        # Iterate through mof instances
        unique_id = 0
        for instance in cls.instances:

            # Take the smiles code for this linker
            # smiles, number_of_linkers = MOF.find_smiles_fragm(instance.fragmentation_path)
            smiles = MOF.find_smiles_obabel(instance.obabel_path)

            if smiles != None:
                cls.new_instances.append(instance)
            else:
                MOF.fault_smiles.append(instance.name)
                continue

            # This sets the smile code equal to a unique id code
            if smiles not in cls.smiles_id_dict.keys():
                unique_id += 1
                cls.smiles_id_dict[smiles] = str(unique_id) # smiles - unique_id

            instance.linker_smiles = cls.smiles_id_dict[smiles]

            Linkers(instance.linker_smiles, instance.name)

            copy(os.path.join(instance.fragmentation_path,"Output/MetalOxo"), os.path.join(MOF.path_to_linkers_directory, instance.linker_smiles, instance.name), 'linkers.cif', 'linkers.cif')
            copy(instance.obabel_path, os.path.join(MOF.path_to_linkers_directory, instance.linker_smiles, instance.name), 'linker.xyz', 'linker.xyz')

        cls.instances = cls.new_instances

        return cls.smiles_id_dict

    # def change_smiles(self, new_smiles):
        
    #     if new_smiles in linkers_dictionary:
    #         self.linker_smiles = linkers_dictionary[new_smiles]
    #         self.simple_smile = self.linker_smiles
    #     else:
    #         # SEE THIS MORE. WHAT HAPPENS IF THERE IS AN ETERNAL LOOP
    #         new_smiles = input('Please provide a valid smiles that already exists')
    #         Linkers.change_smiles(new_smiles)

    @staticmethod
    def analyse(cifs, linkers, best_opt_energy_dict, id_smiles_dict):
        r"""
        Analyze MOF instances based on calculated energies and linkers information.

        Parameters
        ----------
        cifs : List[MOF]
            List of MOF instances to analyze.
        linkers : List[Linkers]
            List of Linkers instances.
        best_opt_energy_dict : Dict
            Dictionary containing optimization energies for linkers.
        linkers_dictionary : Dict
            Dictionary mapping Smiles codes to instance numbers.

        Returns
        -------
        List[List]
            List of analysis results for each MOF instance.

        Notes
        -----
        This static method performs analysis on MOF instances, calculating binding energies,
        RMSD values, and storing the results in a list.
        """
        results_list = []

        for mof in cifs:
            linker = next((obj for obj in linkers if obj.smiles == mof.linker_smiles and obj.mof_name == mof.name), None)

            with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
                lines = f.readlines()
            for line in lines:
                if "cycle" in line:
                    mof.sp_energy = float(line.split()[6])
                    break
            
            if linker != None and linker.smiles in best_opt_energy_dict.keys():
                mof.opt_energy = float(linker.opt_energy)
                mof.opt_status = linker.opt_status
                mof.calc_de(mof.sp_energy, best_opt_energy_dict)
                mof.calc_rmsd(best_opt_energy_dict)
            
                ''' SKIP FOR NOW '''
                '''
                question = input(f'\nDid not find linker for: {mof.name}. Change smiles for {mof.name}? [y/n]: ')
                if question == 'n':
                    print(f"Did not find linker for: {mof.name}. Zero values will be appointed")
                    mof.opt_energy = 0.
                    mof.de = 0.
                    mof.rmsd = 0.
                    with open(os.path.join(mof.sp_path, "uffgradient"), 'r') as f:
                        lines = f.readlines()
                    for line in lines:
                        if "cycle" in line:
                            mof.sp_energy = float(line.split()[6])
                            break
                else:
                    new_smiles = input(f'\nNew smile code: ')
                    mof.change_smiles(new_smiles)
                    linker = next((obj for obj in linkers if obj.smiles == mof.linker_smiles and obj.mof_name == mof.name), None)
                    mof.opt_energy = float(linker.opt_energy)
                    mof.calc_de(dict)
                    mof.calc_rmsd(mof, dict)
                '''
                ''' ----------- ''' 
            
            results_list.append([mof.name, mof.de, mof.de*627.51, mof.rmsd, mof.linker_smiles, id_smiles_dict[mof.linker_smiles], mof.sp_energy, mof.opt_energy, mof.opt_status])
        
        return results_list
    
    def calc_de(self, best_opt_energy_dict):
        r"""
        Calculate the binding energy (DE) for the MOF instance.

        Parameters
        ----------
        best_opt_energy_dict : Dict
            Dictionary containing the best optimization energy for each linker.

        Notes
        -----
        This method calculates the binding energy (DE) for the MOF instance using the
        best optimization energy for the corresponding linker.
        """

        smiles = self.linker_smiles
        
        if smiles in best_opt_energy_dict and best_opt_energy_dict[smiles] is not None:
            best_opt_energy = best_opt_energy_dict[smiles][0]
            self.de = float(best_opt_energy) - float(self.sp_energy)
        else:
            self.de = 0
        
        return self.de

    def calc_rmsd(self, best_opt_energy_dict):
        r"""
        Calculate the RMSD (Root Mean Square Deviation) for the MOF instance.

        Parameters
        ----------
        best_opt_energy_dict : Dict
            Dictionary containing the best optimization energy for each linker.

        Notes
        -----
        This method calculates the RMSD for the MOF instance by comparing the optimized
        structure with the supercell structure.
        """
    
        rmsd = []        
    
        copy(best_opt_energy_dict[self.linker_smiles][1], self.rmsd_path, 'final.xyz', 'final_opt.xyz')
        copy(self.sp_path, self.rmsd_path, 'final.xyz', 'final_sp.xyz')
        
        os.chdir(self.rmsd_path)
    
        check = MOF.rmsd_p()

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
        
    
        try:
            minimum = float(rmsd[0].stdout)
        except:
            minimum = 10000
            print('WARNING: Error in float rmsd for: ', self.name, '\n')
            print(f"Warning: Unable to convert {i.stdout} to float for {i.args}")

        for i in rmsd:
            try:
                current_value = float(i.stdout)
                if current_value < minimum:
                    minimum = float(i.stdout)
                    args = i.args
            except ValueError:
                print(f"Warning: Unable to convert {i.stdout} to float for {i.args}")

    
        with open('result.txt', 'w') as file:
            file.write(str(minimum))
            file.write('\n')
            try:
                file.write(args)
            except:
                print(f'Args not found for mof {self.rmsd_path}')
                    
        self.rmsd = minimum
    
        os.chdir(self.src_dir)
    
    @staticmethod
    def rmsd_p(reorder = False, recursion_depth = 0):
        r"""
        Creating another instance using new reordering method not include in the original calculate_rmsd tool.

        Parameters
        ----------
        reorder : bool, optional
            Whether to perform reordering, by default False.
        recursion_depth : int, optional
            Recursion depth to handle potential errors, by default 0.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """        
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
                    return MOF.rmsd_p(reorder=True, recursion_depth=recursion_depth + 1)
    
                symbol = atomic_symbols.get(atomic_number)
                coordinates = [float(coord) for coord in parts[1:4]]
                data.append((symbol, coordinates))
    
        with open('final_sp_mod.xyz', 'w') as output_file:
            output_file.write(f"{len(data)}\n")
            output_file.write("\n")
            for symbol, coords in data:
                output_file.write(f"{symbol} {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f}\n")
        
        return True

