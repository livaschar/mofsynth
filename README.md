# MOFSynth
<h1 align="center">
  <img alt="Logo" src="https://github.com/livaschar/mofsynth/blob/0.2/docs/images/synth_logo_cropped.png" style="width: 300px;"/>
</h1>


<h4 align="center">

[![Requires Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=yellow&label=Python&labelColor=black&color=blue)](https://www.python.org/downloads/)
[![Licensed under GPL-3.0-only](https://img.shields.io/badge/GPL--3.0--only-gold?label=License&labelColor=black)](https://spdx.org/licenses/GPL-3.0-only.html)
[![pip install pymoxel](https://img.shields.io/badge/install-blue?logo=pypi&logoColor=yellow&label=PyPI&labelColor=black)](https://pypi.org/project/pymoxel/)
[![PyPI version](https://badge.fury.io/py/pymoxel.svg)](https://badge.fury.io/py/pymoxel)

</h4>

MOFSynth is a Python package for **MOF synthesizability evaluation**, with
emphasis on reticular chemistry.

In materials science, especially in the synthesis of metal-organic frameworks (MOFs),
a significant portion of time and effort is spent on the experimental process of synthesizing
and evaluating the viability of MOFs.

MOFSynth aims to provide a simple and efficient interface for evaluating
the synthesizability of metal-organic frameworks (MOFs) in an experiment-ready format,
minimizing the time and labor traditionally required for these experimental preprocessing steps.
This allows researchers to focus more on innovative synthesis and experimental validation
rather than on preparatory tasks.

## 📰 Citing MOFSynth
Paper under review

## ⚙️  Installation
It is strongly recommended to **perform the installation inside a virtual environment**.

```sh
python -m venv <venvir_name>
source <venvir_name>/bin/activate
```
```sh
pip install mofsynth
```

### Requires:
To run MOFSynth, the following modules and tools must be present in your system:
1. **pymatgen**: A robust materials analysis library. [materialsproject/pymatgen](https://github.com/materialsproject/pymatgen)
   - pip install pymatgen
2. **Open Babel**: An open-source chemistry toolbox for converting chemical file formats. [openbabel/openbabel](https://github.com/openbabel/openbabel)
   - pip install openbabel
3. **calculate_rmsd**: A tool for calculating root-mean-square deviations (RMSD). [charnley/rmsd](https://github.com/charnley/rmsd)
   - pip install calculate_rmsd
4. **mofid**: A Python library for MOF identification and characterization. [snurr-group/mofid ](https://github.com/snurr-group/mofid)
5. **TURBOMOLE**: A computational chemistry program package.
   - Ensure it is properly installed and configured in your system. Refer to the [TURBOMOLE installation guide](https://www.turbomole.org/).

## 💻 Browser-Based MOFid
Coming Soon

## 📖 Usage example
Check the [tutorial](https://moxel.readthedocs.io/en/stable/tutorial.html).

<p align="center">
  <img alt="Voxels" src="https://raw.githubusercontent.com/adosar/moxel/master/docs/source/images/voxels.gif" width="25%"/>
</p>

## :warning: Problems?
Don't hesitate to communicate via [email](mailto:chemp1167@edu.chemistry.uoc.gr)

## 📇 TODO


## 📑 License
MOFSynth is released under the [GNU General Public License v3.0 only](https://spdx.org/licenses/GPL-3.0-only.html).
