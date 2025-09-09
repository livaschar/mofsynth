.. highlight:: python

|:rocket:| Tutorial
===================

As stated in :ref:`advantages`, all you need is a ``.cif`` file!

If you don't have one |:point_right:| :download:`example.cif<down/example.cif>`
or try MOFSynth in a mini database |:point_right:| :download:`example_database.zip<down/example_database.zip>`

First, create a directory for the tutorial:

    .. code-block:: console

        $ mkdir mofsynth_tutorial
        $ cd mofsynth_tutorial

Next, create a directory to store the CIF files:

    .. code-block:: console

        $ mkdir cifs_folder

Important: make sure that turbomole/6.5 is installed on your system by running:
    
    .. code-block:: console

        $ module avail

Next, create an input_data folder to store the config.yaml file and the .sh file
that runs the calculations using TURBOMOLE on your system
    
    .. code-block:: console

        $ mkdir config_dir

The config.yaml file should have the following format

.. code-block:: text

    optimization:
      command: sbatch
      file: <your_job>.sh
      cycles: 1000

You can find an example .sh script in the github repo at mofsynth/src/mofsynth/config_dir.

The final structure should look like this:

.. code-block:: text
   
   cifs_folder/
   └── example.cif
   config_dir/
   └── config.yaml
   └── <your_job>.sh

You are ready to run using the following command:

    .. code-block:: console

        $ mofsynth exec path/to/cifs_folder 10


After the calculations have completed, run:

    .. code-block:: console

        $ mofsynth report path/to/cifs_folder

Hurray! An **.xlsx file** containing the results will be created in the *mofsynth_tutorial/*
