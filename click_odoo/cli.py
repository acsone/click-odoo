# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import logging
import runpy
import sys

import click

from pkg_resources import iter_entry_points
from click_plugins import with_plugins

from . import options
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
        @click.pass_context
        @options.config_opt
        @options.db_opt
        @options.log_level_opt(default_log_level)
        @options.logfile_opt
        @options.rollback_opt
        @functools.wraps(func)
        def wrapped(ctx, config, log_level, logfile, database=None,
                    rollback=False, *args, **kwargs):
            try:
                parse_config(config, database, log_level, logfile)
                if not database:
                    database = odoo.tools.config['db_name']
                if with_database and database_required and not database:
                    raise click.UsageError(
                        "No database provided, please provide one with the -d "
                        "option or the Odoo configuration file."
                    )
                if with_database and database:
                    with OdooEnvironment(
                        database=database,
                        rollback=rollback,
                    ) as env:
                        return func(ctx, env, *args, **kwargs)
                else:
                    with odoo.api.Environment.manage():
                        return func(ctx, None, *args, **kwargs)
            except Exception as e:
                _logger.error("exception", exc_info=True)
                raise click.ClickException(str(e))
        if not with_database:
            _remove_click_option(wrapped, 'database')
        if not with_rollback or not with_database:
            _remove_click_option(wrapped, 'rollback')
        return wrapped
    return inner


@click.group(invoke_without_command=True)
@env_options(database_required=False)
@options.interactive_opt
@options.shell_interface_opt
@options.script_arg
@options.script_args_arg
@with_plugins(iter_entry_points('click_odoo.plugins'))
def main(ctx, env, interactive, shell_interface, script, script_args):
    """Execute a python script in an initialized Odoo environment. The script
    has access to a 'env' global variable which is an odoo.api.Environment
    initialized for the given database. If no script is provided, the script is
    read from stdin or an interactive console is started if stdin appears to be
    a terminal."""
    if ctx.invoked_subcommand is None:
        global_vars = {'env': env}
        if script:
            sys.argv[1:] = script_args
            global_vars = runpy.run_path(
                script, init_globals=global_vars, run_name='__main__')
        if not script or interactive:
            if console._isatty(sys.stdin):
                if not env:
                    _logger.info(
                        "No environment set, use `-d dbname` to get one.")
                console.Shell.interact(global_vars, shell_interface)
                if env:
                    env.cr.rollback()
            else:
                sys.argv[:] = ['']
                global_vars['__name__'] = '__main__'
                exec(sys.stdin.read(), global_vars)
