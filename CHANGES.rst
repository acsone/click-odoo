Changes
~~~~~~~

.. Future (?)
.. ----------
.. - ...

1.3.1 (unreleased)
------------------
- add support for launching with ``python -m click_odoo``. Fixes #20.

1.3.0 (2018-11-21)
------------------
- pass click ctx to environment_manager

1.2.0 (2018-11-18)
------------------
- refactor ``@click_odoo.env_options`` to allow propagating ``env``
  to subcommands through the click context. Fixes #16.
- do not log click Exit exception, which may be raised by subcommands as
  a result of --help.

Upgrading:
- click-odoo now requires click>=7

1.1.1 (2018-11-01)
------------------
- add ``with_addons_path`` option to ``@click_odoo.env_options``
  to control the presence of the ``--addons-path`` option. Defaults to False.
  Enabled for the ``click-odoo`` CLI.

1.1.0 (2018-10-31)
------------------
- add ``environment_manager`` to ``@click_odoo.env_options``, providing
  a hook on ``odoo.api.Environment`` creation.
- add ``--addons-path`` option to the CLI.
- add ``database_must_exist`` option to ``@click_odoo.env_options``
  so scripts can behave how they please in case the database is absent.

1.0.4 (2018-10-07)
------------------
- silence deprecation warning
- adapt tests for Odoo 12

1.0.3 (2018-06-05)
------------------
- clarify the behaviour of ``@env_option`` ``with_database`` and ``database_required``
  parameters; in particular, when ``with_database`` and ``database_required``
  are both set (the default), the ``--database`` option can be omitted
  as long as a database is declared in the Odoo configuration file.

1.0.2 (2018-06-01)
------------------
- refactor the OdooEnvironment class: it is much cleaner when
  it leaves the global Odoo config alone, so we completely move
  responsibility to initialize the Odoo config to the CLI part.

1.0.1 (2018-05-27)
------------------
- better error logging and handling: all exceptions occuring
  in scripts under click_odoo.env_options are logged and converted
  to ClickException so we are sure they are both in the log file
  and on the console (handled by click) for the user to see.
  The OdooEnvironment context manager does not do additional logging,
  leaving that responsibility to the caller.

1.0.0 (2018-05-20)
------------------
- close db connections when releasing OdooEnvironment
- expose click_odoo.odoo_bin (odoo or openerp-server depending on Odoo series).
  not documented yet, because it should ideally be a full path corresponding
  to the installed click_odoo.odoo, and I'm not sure how best to detect it yet.

1.0.0b4 (2018-05-17)
--------------------
- minor documentation improvements
- add the possibility to run script without ``--database`` (ie without env,
  but with a properly initialized Odoo library such as addons path)
- be more resilient in case we can't obtain a context for the user

1.0.0b3 (2018-03-22)
--------------------
- click_odoo now exports the odoo namespace: ``from click_odoo import odoo``
  is an alias for ``import odoo`` (>9) or ``import openerp as odoo`` (<=9)
- add a ``with_rollback`` option to the ``env_options`` decorator, to control
  the presence of the rollback option
- document the ``env_options`` decorator

1.0.0b2 (2018-03-21)
--------------------
- commit in case of success, so users do not need to commit in their
  scripts, therefore making scripts easier to compose in larger transactions
- add a --rollback option
- interactive mode forces --rollback

1.0.0b1 (2018-03-20)
--------------------
- clear cache when starting environment (mostly useful for tests)
- simplify and test transaction and exception handling
- when leaving the env, log the exception to be sure it is visible
  when using ``--logfile``

1.0.0a2 (2018-03-19)
--------------------
- improve transaction management: avoid some rare deadlock
- avoid masking original exception in case of error during rollback
- make sure scripts launched by click-odoo have ``__name__ == '__main__'``
- add ``--logfile option``

1.0.0a1 (2018-03-19)
--------------------
- first alpha
