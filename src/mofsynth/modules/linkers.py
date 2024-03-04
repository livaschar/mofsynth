
from dataclasses import dataclass
import os
import re
from . other import copy
from . mof import MOF


@dataclass
class Linkers:
    r"""
    Class for managing linker molecules and their optimization.

    Attributes
    ----------
    job_sh : str
        Default job script file name.
    run_str : str
        Default run string for optimization.
    opt_cycles : int
        Default number of optimization cycles.
    run_str_sp : str
        Default run string for single-point energy calculation.
    job_sh_path : str
        Default path for job script.
    settings_path : str
        Default path for settings file.
    instances : list
        List to store instances of the Linkers class.
    converged : list
        List to store converged linker instances.
    not_converged : list
        List to store not converged linker instances.

    Methods
    -------
    change_smiles(smiles)
        Change the SMILES code of a linker instance.

    opt_settings(run_str, opt_cycles, job_sh=None)
        Set optimization settings for all linker instances.

    optimize(rerun=False)
        Optimize the linker structure.

    check_optimization_status(linkers_list)
        Check the optimization status of linker instances.

    define_linker_opt_energies()
        Define the optimization energy for a converged linker instance.

    find_the_best_opt_energies()
        Find the best optimization energy for each SMILES code.
    """
    # Initial parameters that can be changed
    
    job_sh = 'job.sh'
    run_str = 'sbatch job.sh'
    opt_cycles = 1000
    
    # run_str_sp = f"bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    run_str_sp =  "bash -l -c 'module load turbomole/7.02; x2t linker.xyz > coord; uff; t2x -c > final.xyz'"
    
    job_sh_path = os.path.join('/'.join(__file__.split('/')[:-2]),'input_data')
    settings_path = os.path.join('/'.join(__file__.split('/')[:-2]),'input_data/settings.txt')

    instances = []
    converged = []
    not_converged = []

    def __init__(self, smiles, mof_name):
        r"""
        Initialize a Linkers instance.

        Parameters
        ----------
        smiles : str
            SMILES code of the linker molecule.
        mof_name : str
            Name of the associated MOF.
        """
        Linkers.instances.append(self)

        self.smiles = smiles
        # self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles) # is not used yet
        self.simple_smile = smiles
        self.mof_name = mof_name
        self.opt_path = os.path.join(MOF.linkers_path, self.simple_smile, self.mof_name)
        self.opt_energy = 0

        try:
            os.makedirs(self.opt_path, exist_ok = True)
        except:
            return None
    
    def change_smiles(self, smiles):
        """
        Change the SMILES code of the linker instance.

        Parameters
        ----------
        smiles : str
            New SMILES code.
        """        
        self.smiles = smiles
        self.simple_smile = re.sub(re.compile('[^a-zA-Z0-9]'), '', self.smiles)
        self.opt_path = os.path.join(MOF.linkers_path, self.simple_smile, self.mof_name)

    @classmethod
    def opt_settings(cls, run_str, opt_cycles, job_sh = None):
        r"""
        Set optimization settings for all linker instances.

        Parameters
        ----------
        run_str : str
            New run string for optimization.
        opt_cycles : int
            New number of optimization cycles.
        job_sh : str, optional
            New job script file name.
        """
        cls.run_str = run_str
        cls.opt_cycles = opt_cycles
        if job_sh != None:
            cls.job_sh = job_sh

    def optimize(self, rerun = False):
        r"""
        Optimize the linker structure.

        Parameters
        ----------
        rerun : bool, optional
            Whether to rerun the optimization.

        Notes
        -----
        This function updates the optimization settings, runs the optimization, and modifies necessary files.
        """
        if os.path.exists(os.path.join(self.opt_path, 'uffconverged')):
            return
        else:
            files_to_keep = ['linkers.cif', 'linker.xyz']
            for file_name in os.listdir(self.opt_path):
                file_path = os.path.join(self.opt_path, file_name)
                if file_name not in files_to_keep:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_name}: {str(e)}")
        
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

        # try:
        #     os.system(Linkers.run_str)
        # except Exception as e:
        #     print(f"An error occurred while running the command for turbomole: {str(e)}")
        
        os.chdir(MOF.src_dir)

    @staticmethod
    def check_optimization_status(linkers_list):
        r"""
        Check the optimization status of linker instances.

        Parameters
        ----------
        linkers_list : list
            List of linker instances.

        Returns
        -------
        Tuple
            A tuple containing lists of converged and not converged linker instances.
        """
        Linkers.converged = []
        Linkers.not_converged = []
        

        for linker in linkers_list:   

            ''' SKIP FOR NOW '''
            '''
            if os.path.exists(os.path.join(linker.opt_path)) == False:
                print(f'\n{linker.opt_path} does not exits. Please check the _Linkers_ folder.')
                new_smiles = input('Change the smiles to check again: ')
                linker.change_smiles(new_smiles)
                Linkers.converged.append(linker)
            '''
            ''' ---------- '''
            
            if os.path.exists(os.path.join(linker.opt_path, 'uffconverged')):
                # print(f'\nOptimization converged succesfully for {linker.smiles} [MOF = {linker.mof_name}]')
                Linkers.converged.append(linker)

            elif os.path.exists(os.path.join(linker.opt_path, 'not.uffconverged')):
                Linkers.not_converged.append(linker)
            
            elif os.path.exists(os.path.join(linker.opt_path, 'not.uffconverged')) == False and os.path.exists(os.path.join(linker.opt_path, 'energy')):
                print(f'\nOptimization run one circle for {linker.smiles} [MOF = {linker.mof_name}')
                Linkers.not_converged.append(linker)
        
            else:
                Linkers.not_converged.append(linker)
                #pass # print(f'\nOptimization did not run for {linker.smiles} [MOF = {linker.mof_name}')
        
        ''' PASS FOR NOW '''
        '''
        custom = []
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
        '''
        ''' -------------- '''
        return Linkers.converged, Linkers.not_converged
    
    def define_linker_opt_energies(self):   
        r"""
        Define the optimization energy for a converged linker instance.
        """        
        with open(os.path.join(self.opt_path, 'uffenergy')) as f:
            lines = f.readlines()
        self.opt_energy = lines[1].split()[-1]

    
    @classmethod
    def find_the_best_opt_energies(cls):
        r"""
        Find the best optimization energy for each SMILES code.

        Returns
        -------
        Dict
            A dictionary containing the best optimization energy and path for each SMILES code.
        """
        energy_dict = {}
        for instance in Linkers.converged:
            if instance.smiles in energy_dict:
                if float(instance.opt_energy) < float(energy_dict[instance.smiles][0]):
                    energy_dict[instance.smiles] = [instance.opt_energy, instance.opt_path]
            else:
                energy_dict[instance.smiles] = [instance.opt_energy, instance.opt_path]

        return energy_dict

