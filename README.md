# MOFSynth
<h1 align="center">
<!--   <img alt="Logo" src="https://raw.githubusercontent.com/livaschar/mofsynth/main/docs/source/images/final_grey-removebg-preview.png" style="width: 500px;"/> -->
<!--   <img alt="Logo" src="https://github.com/livaschar/mofsynth/blob/main/docs/source/images/final_grey-removebg-preview.png" style="width: 500px;"/> -->
  <img alt="Logo" src="https://github.com/livaschar/mofsynth/blob/main/docs/source/images/mofsynth_logo.svg" style="width: 500px;"/>
</h1>


<h4 align="center">

[![Requires Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=yellow&label=Python&labelColor=black&color=blue)](https://www.python.org/downloads/)
[![Read the Docs](https://img.shields.io/badge/stable-green?logo=readthedocs&logoColor=blue&label=Read%20the%20Docs&labelColor=black)](https://mofsynth.readthedocs.io)
[![Documentation Status](https://readthedocs.org/projects/mofsynth/badge/?version=latest)](https://mofsynth.readthedocs.io/en/latest/?badge=latest)
[![Licensed under GPL-3.0-only](https://img.shields.io/badge/GPL--3.0--only-gold?label=License&labelColor=black)](https://spdx.org/licenses/GPL-3.0-only.html)

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
```sh
  @article{doi:10.1021/acs.jcim.4c01298,
  author = {Livas, Charalampos G. and Trikalitis, Pantelis N. and Froudakis, George E.},
  title = {MOFSynth: A Computational Tool toward Synthetic Likelihood Predictions of MOFs},
  journal = {Journal of Chemical Information and Modeling},
  volume = {64},
  number = {21},
  pages = {8193-8200},
  year = {2024},
  doi = {10.1021/acs.jcim.4c01298},
  note ={PMID: 39481084},
  URL = {https://doi.org/10.1021/acs.jcim.4c01298},
  eprint = {https://doi.org/10.1021/acs.jcim.4c01298}
  }
```

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
1. **mofid**: A Python library for MOF identification and characterization. [snurr-group/mofid ](https://github.com/snurr-group/mofid)
2. **TURBOMOLE**: A computational chemistry program package.
   - Ensure turbomole/6.5 is properly installed and configured in your system. Refer to the [TURBOMOLE installation guide](https://www.turbomole.org/).
   

## 💻 Browser-Based MOFSynth
Web version of the tool at [link](https://mofsynth.website)

## 📖 Usage example
Check the [tutorial](https://mofsynth.readthedocs.io/en/latest/tutorial.html).

## :warning: Problems?
Don't hesitate to communicate via [email](mailto:chemp1167@edu.chemistry.uoc.gr)

## 📑 License
MOFSynth is released under the [GNU General Public License v3.0 only](https://spdx.org/licenses/GPL-3.0-only.html).

