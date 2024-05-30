Basic Usage
===========

.. _with_install:

With Installation
-----------------

You can create menu entries for MEAFS by typing in the terminal or cmd:  

.. code-block:: bash

   meafs-desktop-create

| Then, search in the menu for *MEAFS*, and in Windows, a Desktop link will also be created.  
| Or, you can just type in the terminal or cmd: 

.. code-block:: bash

   meafs

Or:

.. code-block:: bash

   python -m meafs

For the command line option, do not forget to activate the Anaconda environment if you are using it. For the menu entry, this is done automatically if necessary.

.. _without_installation:

Without Installation
--------------------

Simply execute the file ``meafs_code/gui.py`` and it will power the GUI.


.. _flags:

Flags and Arguments
-------------------

There are some flags that can be passed with the command-line.

-h, --help              Show the help section.
-v, --version           Show version number.
-l, --last              Load the last closed session. Default location is ``meafs_code/auto_save_last.pkl``.
-s, --load-auto-save    Load the auto saved session. Default location is: ``meafs_code/auto_save.pkl``.

Also, any saved section can be passed as an argument and meafs will power the GUI with it:

.. code-block:: bash
   
   meafs path/to/session.pkl

If no argument is given, the GUI will power with a new empty session.

Auto Save
---------

| In the *File* menu there is an *Auto Save* option. When checked, MEAFS will save the session every 5 seconds in a file named ``auto_save.pkl``.  
| Also, if auto save is enabled, when MEAFS is closed, it will save the session in the ``auto_save_last.pkl`` file.  
| These files are located under the MEAFS directory and the ``-h`` :ref:`flag <flags>` will show the location.  
| To load any of these files, simply use the :ref:`flags <flags>` or load them in the *File* - *Open...* menu.
