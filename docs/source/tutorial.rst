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
        $ cd mofsynth_tutorial

Important: make sure that TURBOMOLE is installed on your system.

Next, create an input_data folder to store the settings.txt file and the .sh file
that runs the calculations using TURBOMOLE on your system
    
    .. code-block:: console

        $ mkdir input_data

The final structure should look like this

.. code-block:: text

   input_data/
   └── settings.txt


You are ready to run using the following command:

    .. code-block:: console

        $ python -m mofsynth main_run cifs_folder 10


After the calculations have completed, run:

    .. code-block:: console

        $ python -m mofsynth export_results

An .xlsx file containing the results will be created in the mofsynth_tutorial/Synth_folder.
