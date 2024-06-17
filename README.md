# MOFSynth

<h1 align="center">
  <img alt="Logo" src="https://raw.githubusercontent.com/livaschar/mofsynth/blob/0.2/docs/images/synth_logo_cropped.svg"/>
</h1>

<h1 align="center">
  <img alt="Logo" src="https://github.com/livaschar/mofsynth/blob/0.2/docs/images/synth_logo_cropped.png" style="width: 300px;"/>
</h1>


<h4 align="center">
  
[![Requires Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=yellow&label=Python&labelColor=black&color=blue)](https://www.python.org/downloads/)
[![Licensed under GPL-3.0-only](https://img.shields.io/badge/GPL--3.0--only-gold?label=License&labelColor=black)](https://spdx.org/licenses/GPL-3.0-only.html)
[![Read the Docs](https://img.shields.io/badge/stable-green?logo=readthedocs&logoColor=blue&label=Read%20the%20Docs&labelColor=black)](https://moxel.readthedocs.io)
[![pip install pymoxel](https://img.shields.io/badge/install-blue?logo=pypi&logoColor=yellow&label=PyPI&labelColor=black)](https://pypi.org/project/pymoxel/)
[![Documentation Status](https://readthedocs.org/projects/moxel/badge/?version=stable)](https://moxel.readthedocs.io/en/stable/?badge=stable)
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

## ⚙️  Installation
It is strongly recommended to **perform the installation inside a virtual environment**.

Check the [installation steps](https://moxel.readthedocs.io/en/stable/installation.html).

Assuming an activated virtual environment:
```sh
pip install pymoxel
```

## 📖 Usage
Check the [tutorial](https://moxel.readthedocs.io/en/stable/tutorial.html).

<p align="center">
  <img alt="Voxels" src="https://raw.githubusercontent.com/adosar/moxel/master/docs/source/images/voxels.gif" width="25%"/>
</p>

## 📰 Citing MOXελ
If you use ΜΟΧελ in your research, please consider citing the following work:

    @article{Sarikas2024,
    title = {Gas adsorption meets deep learning: voxelizing the potential energy surface of metal-organic frameworks},
    volume = {14},
    ISSN = {2045-2322},
    url = {http://dx.doi.org/10.1038/s41598-023-50309-8},
    DOI = {10.1038/s41598-023-50309-8},
    number = {1},
    journal = {Scientific Reports},
    publisher = {Springer Science and Business Media LLC},
    author = {Sarikas,  Antonios P. and Gkagkas,  Konstantinos and Froudakis,  George E.},
    year = {2024},
    month = jan
    }

## 📇 TODO
1. CLI for training [RetNet](https://www.nature.com/articles/s41598-023-50309-8).
2. Improve performance
3. Improve voxelization scheme
4. Improve modeling of interactions

## 📑 License
MOXελ is released under the [GNU General Public License v3.0 only](https://spdx.org/licenses/GPL-3.0-only.html).
