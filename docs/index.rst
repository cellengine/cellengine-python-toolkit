.. toctree::
  :maxdepth: 2
  :caption: Contents:

  client
  compensations
  experiments
  fcsfiles

CellEngine API Toolkit for Python
======================================

Getting started
---------------

Install ``cellengine`` using ``pip``:

.. code-block:: console

  $ pip install git+https://github.com/primitybio/cellengine-python-toolkit.git

Example
^^^^^^^

.. code-block:: python

  import cellengine
  client = cellengine.Client(username="jason")
  # password will be prompted
  experiment = client.get_experiment("My experiment")

Resources
~~~~~~~~~

* `GitHub <https://github.com/PrimityBio/cellengine-python-toolkit/>`__
* `API documentation <https://docs.cellengine.com/api/>`__
