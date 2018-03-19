click-odoo
===========

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/click-odoo.svg
    :target: http://badge.fury.io/py/click-odoo
.. image:: https://travis-ci.org/acsone/click-odoo.svg?branch=master
   :target: https://travis-ci.org/acsone/click-odoo
.. image:: https://codecov.io/gh/acsone/click-odoo/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/acsone/click-odoo

``click-odoo`` helps you create and run beautiful and robust command line scripts
for Odoo. It is based on the excellent Click_ library.

.. contents::

Quick start
~~~~~~~~~~~

Install it in a (preferably virtual) environment where Odoo is installed::

  pip install click-odoo

Assuming the following script named ``list-users.py``.

.. code:: python

   #!/usr/bin/env click-odoo
   from __future__ import print_function

   for u in env['res.users'].search([]):
       print(u.login, u.name)

It can be run with::

  click-odoo -d dbname --log-level=error list-users.py

or::

  ./list-users.py -d dbname --log-level=error

The third technique to create scripts looks like this. Assuming
the following script named ``list-users2.py``.

.. code:: python

  #!/usr/bin/env python
  from __future__ import print_function
  import click

  import click_odoo


  @click.command()
  @click_odoo.env_options(default_log_level='error')
  @click.option('--say-hello', is_flag=True)
  def main(env, say_hello):
      if say_hello:
          click.echo("Hello!")
      for u in env['res.users'].search([]):
          print(u.login, u.name)


  if __name__ == '__main__':
      main()

It can be run like this::

  $ ./list-users2.py --help
  Usage: list-users2.py [OPTIONS]

  Options:
    -c, --config PATH    Specify the Odoo configuration file. Other ways to
                         provide it are with the ODOO_RC or OPENERP_SERVER
                         environment variables, or ~/.odoorc (Odoo >= 10) or
                         ~/.openerp_serverrc.
    -d, --database TEXT  Specify the database name.
    --log-level TEXT     Specify the logging level. Accepted values depend on
                         the Odoo version, and include debug, info warn, error.
                         [default: error]
    --say-hello
    --help               Show this message and exit.

  $ ./list-users2.py --say-hello -d dbname
  Hello!
  admin Administrator
  ...

Supported Odoo versions
~~~~~~~~~~~~~~~~~~~~~~~

Odoo version 8, 9, 10 and 11 are supported.

An important design goal is to provide a consistent behaviour
across Odoo versions.

Database transactions
~~~~~~~~~~~~~~~~~~~~~

``click-odoo`` does not commit the transaction for you.
To persist changes made to the database, use ``env.cr.commit()``.

Logging
~~~~~~~

In version 8, Odoo logs to stdout by default. On other versions
it is stderr. ``click-odoo`` attemps to use stderr for Odoo 8 too.

Logging is controlled by the usual Odoo logging options (--log-level,
--logfile) or the Odoo configuration file.

Command line interface (click-odoo)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

  Usage: click-odoo [OPTIONS] [SCRIPT] [SCRIPT_ARGS]...

    Execute a python script in an initialized Odoo environment. The script has
    access to a 'env' global variable which is an odoo.api.Environment
    initialized for the given database. If no script is provided, the script
    is read from stdin or an interactive console is started if stdin appears
    to be a terminal.

  Options:
    -c, --config PATH               Specify the Odoo configuration file. Other
                                    ways to provide it are with the ODOO_RC or
                                    OPENERP_SERVER environment variables, or
                                    ~/.odoorc (Odoo >= 10) or
                                    ~/.openerp_serverrc.
    -d, --database TEXT             Specify the database name.
    --log-level TEXT                Specify the logging level. Accepted values
                                    depend on the Odoo version, and include
                                    debug, info, warn, error. [default: info]
    -i, --interactive / --no-interactive
                                    Inspect interactively after running the
                                    script.
    --shell-interface TEXT          Preferred shell interface for interactive
                                    mode. Accepted values are ipython, ptpython,
                                    bpython, python. If not provided they are
                                    tried in this order.
    --help                          Show this message and exit.

Most options above are the same as ``odoo`` options and behave the same.
Additional options can be set the the configuration file.
Note however that most server-related options (workers, http interface etc)
are ignored because no server is actually started when running a script.

An important feature of ``click-odoo`` compared to, say, ``odoo shell`` is
the capability to pass arguments to scripts.

In order to avoid confusion between ``click-odoo`` options and your script
options and arguments, it is recommended to separate them with ``--``::

  click-odoo -d dbname -- list-users.py -d a b
  ./list-users.py -d dbname -- -d a b

In both examples above, ``sys.argv[1:]`` will contain ``['-d', 'a', 'b']``
in the script.

API
~~~

click_odoo.env_options decorator
---------------------------------

TODO

OdooEnvironment context manager (experimental)
----------------------------------------------

This package also provides an experimental an ``OdooEnvironment`` context manager.

.. warning::

   This API is considered experimental, contrarily to the scripting mechanism
   (ie passing ``env`` to scripts) and ``env_options`` decorator which are
   stable features. Should you have a specific usage for this API and would
   like it to become stable, get it touch to discuss your requirements.

Example:

.. code:: python

  from click_odoo import OdooEnvironment


  with OdooEnvironment(database='dbname') as env:
      env['res.users'].search([])

Useful links
~~~~~~~~~~~~

- pypi page: https://pypi.python.org/pypi/click-odoo
- code repository: https://github.com/acsone/click-odoo
- report issues at: https://github.com/acsone/click-odoo/issues

.. _Click: http://click.pocoo.org

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
