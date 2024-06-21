Help to install *mofid* module
============================

Run the following commands in a Debian system:

.. code-block:: shell

    apt-get -y install default-jre rapidjson-dev openbabel wx3.2-headers libxml2-dev libcairo2-dev libwxgtk3.2-dev
    mkdir mofid_module    
    cd mofid_module
    git clone -b v1.1.0 https://github.com/snurr-group/mofid.git
    cd mofid
    vim openbabel/include/openbabel/obutil.h
      Write *#include <ctime>* in line 47 and save it
    make init
    python3 set_paths.py
    source /opt/venv/bin/activate
    pip install .
