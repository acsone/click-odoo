# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import logging
import runpy
import sys

import click

from . import console
from .env import OdooEnvironment, parse_config, odoo

_logger = logging.getLogger(__name__)


def _remove_click_option(func, name):
    for o in func.__click_params__:
        if o.name == name:
            func.__click_params__.remove(o)
            return


def env_options(default_log_level='info', with_rollback=True,
                with_database=True, database_required=True):
    def inner(func):
        @click.option('--config', '-c', envvar=['ODOO_RC', 'OPENERP_SERVER'],
                      type=click.Path(exists=True, dir_okay=False),
                      help="Specify the Odoo configuration file. Other "
                           "ways to provide it are with the ODOO_RC or "
                           "OPENERP_SERVER environment variables, "
                           "or ~/.odoorc (Odoo >= 10) "
                           "or ~/.openerp_serverrc.")
        @click.option('--database', '-d', envvar=['PGDATABASE'],
                      required=database_required,
                      help="Specify the database name.")
        @click.option('--log-level',
                      default=default_log_level,
                      show_default=True,
                      help="Specify the logging level. Accepted values depend "
                           "on the Odoo version, and include debug, info, "
                           "warn, error.")
        @click.option('--logfile',
                      type=click.Path(dir_okay=False),
                      help="Specify the log file.")
        @click.option('--rollback', is_flag=True,
                      help="Rollback the transaction even if the script "
                           "does not raise an exception. Note that if the "
                           "script itself commits, this option has no effect. "
                           "This is why it is not named dry run. This option "
                           "is implied when an interactive console is "
                           "started.")
        @functools.wraps(func)
        def wrapped(config, log_level, logfile, database=None, rollback=False,
                    *args, **kwargs):
            if database:
                with OdooEnvironment(
                    config=config,
                    database=database,
                    log_level=log_level,
                    logfile=logfile,
                    rollback=rollback,
                ) as env:
                    return func(env, *args, **kwargs)
            else:
                parse_config(config, None, log_level, logfile)
                with odoo.api.Environment.manage():
                    return func(None, *args, **kwargs)
        if not with_database:
            _remove_click_option(wrapped, 'database')
        if not with_rollback or not with_database:
            _remove_click_option(wrapped, 'rollback')
        return wrapped
    return inner


@click.command(help="Execute a python script in an initialized Odoo "
                    "environment. The script has access to a 'env' global "
                    "variable which is an odoo.api.Environment "
                    "initialized for the given database. If no script is "
                    "provided, the script is read from stdin or an "
                    "interactive console is started if stdin appears "
                    "to be a terminal.")
@env_options(database_required=False)
@click.option('--interactive/--no-interactive', '-i',
              help="Inspect interactively after running the script.")
@click.option('--shell-interface',
              help="Preferred shell interface for interactive mode. Accepted "
                   "values are ipython, ptpython, bpython, python. If not "
                   "provided they are tried in this order.")
@click.argument('script', required=False,
                type=click.Path(exists=True, dir_okay=False))
@click.argument('script-args', nargs=-1)
def main(env, interactive, shell_interface, script, script_args):
    global_vars = {'env': env}
    if script:
        sys.argv[1:] = script_args
        global_vars = runpy.run_path(
            script, init_globals=global_vars, run_name='__main__')
    if not script or interactive:
        if console._isatty(sys.stdin):
            if not env:
                _logger.info("No environment set, use `-d dbname` to get one.")
            console.Shell.interact(global_vars, shell_interface)
            if env:
                env.cr.rollback()
        else:
            sys.argv[:] = ['']
            global_vars['__name__'] = '__main__'
            exec(sys.stdin.read(), global_vars)
