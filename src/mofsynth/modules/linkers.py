from dataclasses import dataclass
import subprocess
from mofsynth.modules.other import copy


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
    best_opt_energy_dict : dictionary
        Dictionary containing the smile_codes as a key and value is a list of the opt_energy and the opt_path

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

    read_linker_opt_energies()
        Read the optimization energy for a converged linker instance.

    define_the_best_opt_energies()
        Define the best optimization energy for each SMILES code.
    """
    
    # Initial parameters that can be changed
    run_str_sp = ''
    run_str_opt = ''
    job_sh_sp = ''
    job_sh_opt = ''
    opt_cycles = 1
    
    # settings_path = os.path.join(os.getcwd(),'input_data/settings.txt')
    config_path = ''
    # job_sh_path = os.path.join(os.getcwd(),'input_data')
    job_sh_path = ''
    
    # config dir path
    config = ''

    instances = []
    converged = []
    not_converged = []
    best_opt_energy_dict = {}

    def __init__(self, smiles_code, mof_name, Linkers_dir):
        r"""
        Initialize a Linkers instance.

        Parameters
        ----------
        smiles_code : str
            SMILES code of the linker molecule.
        mof_name : str
            Name of the associated MOF.
        """
        Linkers.instances.append(self)

        self.smiles_code = smiles_code
        self.mof_name = mof_name
        self.opt_path = Linkers_dir / self.smiles_code / self.mof_name
        self.opt_path.mkdir(parents=True, exist_ok=True)
        self.opt_energy = 0
        self.opt_status = 'not_converged'

    def optimize(self, rerun):
        r"""
        Optimize the linker structure.

        Parameters
        ----------
        rerun : bool, optional
            Whether to run again the uncoverged cases.

        Notes
        -----
        This function updates the optimization settings, runs the optimization, and modifies necessary files.
        """
        
        copy(Linkers.config_directory, self.opt_path, Linkers.job_sh_opt)
        job_sh_path = self.opt_path / Linkers.job_sh_opt
        self.run_str_opt = f'sbatch {job_sh_path}'
        try:
            p = subprocess.Popen(self.run_str_opt, shell=True, cwd=self.opt_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            return False, "xtb optimization procedure"
        
        return True, ''

    @classmethod
    def check_optimization_status(cls, linkers_list):
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

        for linker in linkers_list:
            opt_output_file = linker.opt_path / "check.out"
    
            try:
                with open(opt_output_file, 'r') as f:
                    content = f.read()
            except:
                linker.opt_status = 'no_output_file'
                cls.not_converged.append(linker)
                continue

            
            # Check convergence status
            if "GEOMETRY OPTIMIZATION CONVERGED" in content:
                linker.opt_status = 'converged'
                cls.converged.append(linker)
                
                # Extract energy if converged
                for line in content.split('\n'):
                    if "| TOTAL ENERGY" in line:
                        linker.opt_energy = float(line.split()[3])
                        break
            
            elif "FAILED TO CONVERGE GEOMETRY OPTIMIZATION" in content:
                linker.opt_status = 'not_converged'
                cls.not_converged.append(linker)
        
        return cls.converged, cls.not_converged
    
    @classmethod
    def define_best_opt_energy(cls):

        for instance in Linkers.converged:
            if instance.smiles_code not in cls.best_opt_energy_dict:
                cls.best_opt_energy_dict[instance.smiles_code] = [instance.opt_energy, instance.opt_path]
            else:
                if float(instance.opt_energy) < float(cls.best_opt_energy_dict[instance.smiles_code][0]):
                    cls.best_opt_energy_dict[instance.smiles_code] = [instance.opt_energy, instance.opt_path]

        return cls.best_opt_energy_dict