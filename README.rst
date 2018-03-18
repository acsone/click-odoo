odoo-script
===========

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/odoo-script.svg
    :target: http://badge.fury.io/py/odoo-script
.. image:: https://travis-ci.org/acsone/odoo-script.svg?branch=master
   :target: https://travis-ci.org/acsone/odoo-script
.. image:: https://coveralls.io/repos/acsone/odoo-script/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/acsone/odoo-script?branch=master

``odoo-script`` helps you run python scripts in an initialized Odoo environment.

.. contents::

Install it in a (preferably virtual) environment where Odoo is installed::

  pip install odoo-script

Assuming the following script named ``list-users.py``.

.. code:: python

   #!/usr/bin/env odoo-script
   from __future__ import print_function
   for u in env['res.users'].search([]):
       print(u.login, u.name)

It can be run with::

  odoo-script -d dbname list-users.py

or::

  ./list-users.py -d dbname

Supported Odoo versions
~~~~~~~~~~~~~~~~~~~~~~~

Odoo version 8, 9, 10 and 11 are supported.

Database transactions
~~~~~~~~~~~~~~~~~~~~~

``odoo-script`` does not commit the transaction for you.
To persist changes made to the database, use ``env.cr.commit()``.

Script arguments
~~~~~~~~~~~~~~~~

An important feature of ``odoo-script`` compared to, say, ``odoo shell`` is
the capability to pass arguments to scripts.

In order to avoid confusion between ``odoo-script`` options and your script
options and argument, it is recommended to separate them with ``--``::

  odoo-script -d dbname -- list-users.py -d a b
  ./list-users.py -d dbname -- -d a b

In both examples above, ``sys.argv[1:]`` will contain ``['-d', 'a', 'b']``
in the script.

Command line interface
~~~~~~~~~~~~~~~~~~~~~~

.. code::

  Usage: odoo-script [OPTIONS] [SCRIPT] [SCRIPT_ARGS]...

    Execute a python script in an initialized Odoo environment. The script has
    access to a 'env' global variable which is the odoo.api.Environment
    initialized for the given database. If no script is provided, the script
    is read from stdin or an interactive console is started if stdin appears
    to be a terminal.

  Options:
    -c, --config TEXT               Specify the Odoo configuration file. Other
                                    ways to provide it are with the ODOO_RC or
                                    OPENERP_SERVER environment variables, or
                                    ~/.odoorc (Odoo >= 10) or
                                    ~/.openerp_serverrc.
    -d, --database TEXT             Specify the database name.
    --log-level TEXT                Specify the logging level. Accepted values
                                    depend on the Odoo version, and include
                                    debug, info (default), warn, error.
    -i, --interactive / --no-interactive
                                    Inspect interactively after running the
                                    script.
    --shell-interface TEXT          Preferred shell interface for interactive
                                    mode. Accepted values are ipython, ptpython,
                                    bpython, python. If not provided they are
                                    tried in this order.
    --help                          Show this message and exit.

API
~~~

This package proides an ``OdooEnvironment`` context manager.

.. warning::

   This API is considered experimental, contrarily to the scripting mechanism
   (ie passing ``env`` to scripts) which is a stable feature.
   Should you have a specific usage for the API and would like it to become stable,
   get it touch to discuss your requirements.

Example:

.. code:: python

  from odoo_script import OdooEnvironment

  with OdooEnvironment(database='dbname') as env:
      env['res.users'].search([])

Useful links
~~~~~~~~~~~~

- pypi page: https://pypi.python.org/pypi/odoo-script
- code repository: https://github.com/acsone/odoo-script
- report issues at: https://github.com/acsone/odoo-script/issues

Credits
~~~~~~~

Author:

  - Stéphane Bidoul (`ACSONE <http://acsone.eu/>`_)

Inspiration has been drawn from:

- `anybox.recipe.odoo <https://github.com/anybox/anybox.recipe.odoo>`_
- `anthem by Camptocamp <https://github.com/camptocamp/anthem>`_
- odoo's own shell command

Maintainer
~~~~~~~~~~

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: https://www.acsone.eu

This project is maintained by ACSONE SA/NV.
