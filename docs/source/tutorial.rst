.. highlight:: python

|:rocket:| Tutorial
===================

As stated in :ref:`advantages`, all you need is a ``.cif`` file!

If you don't have one |:point_right:| :download:`example.cif<down/example.cif>`.

First, create a directory for the tutorial:

    .. code-block:: console

        $ mkdir mofsynth_tutorial
        $ cd mofsynth_tutorial

Next, create a directory to store the CIF files:

    .. code-block:: console

        $ mkdir cifs_folder
        $ cd mofsynth_tutorial

Important: make sure that TURBOMOLE is installed on your system.


Ensure that TURBOMOLE is installed on your system.

In the input_data folder, ensure the presence of the following files:
1. settings.txt
2. A .sh script that runs the calculations using TURBOMOLE on your system

To run the main function, use the following command:

    .. code-block:: console

        $ python -m mofsynth main_run cifs_folder 10


After the calculations have completed, run:

    .. code-block:: console

        $ python -m mofsynth export_results

An .xlsx file containing the results will be created in the mofsynth_tutorial/Synth_folder.
