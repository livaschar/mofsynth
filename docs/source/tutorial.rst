.. highlight:: python

|:rocket:| Tutorial
===================

As stated in :ref:`advantages`, all you need is a ``.cif`` file!

If you don't have one |:point_right:| :download:`example.cif<down/example.cif>`.

Create a folder to run the tutorial:

```sh
mkdir <mofsynth_tutorial>
cd <mofsynth_tutorial>
```
Create the folder containing all the cifs:

```sh
mkdir <cifs_folder>
Then make sure that TURBOMOLE is installed on your system.
```

In the input_data folder, there must be two files present:

The settings.txt
The .sh script that runs the calculations using TURBOMOLE on your system
Run the main function:

```sh
python -m mofsynth main_run cifs 10
```

After the calculations have finished running, run:

```sh
python -m mofsynth export_results
```

A .xlsx file with the results will be created in the mofsynth_tutorial/Synth_folder.
