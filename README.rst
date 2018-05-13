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

Useful community-managed scripts can be found in click-odoo-contrib_.

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
                         the Odoo version, and include debug, info, warn, error.
                         [default: error]
    --logfile PATH       Specify the log file.
    --rollback           Rollback the transaction even if the script
                         does not raise an exception. Note that if
                         the script itself commits, this option has no
                         effect, this is why it is not named dry run.
                         This option is implied when an interactive
                         console is started.
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

By default ``click-odoo`` commits the transaction for you, unless your script
raises an exception. This is so that you don't need to put explicit commits
in your scripts, which are therefore easier to compose in larger transactions.

There is a ``--rollback`` option to force a rollback.

A rollback is always performed after an interactive session. If you need to
commit changes made before or during an interactive session, use ``env.cr.commit()``.

Logging
~~~~~~~

In version 8, Odoo logs to stdout by default. On other versions
it is stderr. ``click-odoo`` attempts to use stderr for Odoo 8 too.

Logging is controlled by the usual Odoo logging options (``--log-level``,
``--logfile``) or the Odoo configuration file.

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
                                    debug, info, warn, error.  [default: info]
    --logfile PATH                  Specify the log file.
    --rollback                      Rollback the transaction even if the script
                                    does not raise an exception. Note that if
                                    the script itself commits this option has no
                                    effect. This is why it is not named dry run.
                                    This option is implied when an interactive
                                    console is started.
    -i, --interactive / --no-interactive
                                    Inspect interactively after running the
                                    script.
    --shell-interface TEXT          Preferred shell interface for interactive
                                    mode. Accepted values are ipython, ptpython,
                                    bpython, python. If not provided they are
                                    tried in this order.
    --help                          Show this message and exit.

Most options above are the same as ``odoo`` options and behave identically.
Additional Odoo options can be set in the the configuration file.
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
--------------------------------

``@click_odoo.env_options()`` is a decorator that is used very much like
``@click.option()`` and inserts the list of predefined ``click-odoo``
options. Instead of passing down these options to the command, it prepares
an odoo ``Environment`` and passes it as a ``env`` parameter.

It is configurable with the following parameters:

default_log_level
  The default value for the ``-log-level`` option (default: 'info').

with_rollback
  Controls the presence of the ``--rollback`` option (default: True).
  This is useful for creating commands that commit and leave no possibility
  for rollback.

with_database
  Controls the presence of the ``--database`` option (default: True).
  This is useful to create scripts that have access to a pre-loaded Odoo
  configuration, without any database. In such case, the environment
  is not set (env is None).

database_required
  Controls if ``--database`` is a required option (default: True).
  If no database is provided, no environment is initialized (env is None).

click_odoo.odoo namespace
-------------------------

As a convenience ``click_odoo`` exports the ``odoo`` namespace, so
``from click_odoo import odoo`` is an alias for ``import odoo`` (>9)
or ``import openerp as odoo`` (<=9).

OdooEnvironment context manager (experimental)
----------------------------------------------

This package also provides an experimental ``OdooEnvironment`` context manager.

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

- pypi page: https://pypi.org/project/click-odoo
- code repository: https://github.com/acsone/click-odoo
- report issues at: https://github.com/acsone/click-odoo/issues

.. _Click: http://click.pocoo.org
.. _click-odoo-contrib: https://pypi.python.org/pypi/click-odoo-contrib

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
