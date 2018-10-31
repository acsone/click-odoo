#!/usr/bin/env python
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import logging
import runpy
import sys
from contextlib import closing

import click

from . import console
from .env import OdooEnvironment, odoo, parse_config

_logger = logging.getLogger(__name__)


def _remove_click_option(func, name):
    for o in func.__click_params__:
        if o.name == name:
            func.__click_params__.remove(o)
            return


def _db_exists(dbname):
    conn = odoo.sql_db.db_connect("postgres")
    with closing(conn.cursor()) as cr:
        cr._obj.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower(%s)",
            (dbname,),
        )
        return bool(cr.fetchone())


def env_options(
    default_log_level="info",
    with_rollback=True,
    with_database=True,
    database_required=True,
    database_must_exist=True,
    environment_manager=OdooEnvironment,
):
    def inner(func):
        @click.option(
            "--config",
            "-c",
            envvar=["ODOO_RC", "OPENERP_SERVER"],
            type=click.Path(exists=True, dir_okay=False),
            help="Specify the Odoo configuration file. Other "
            "ways to provide it are with the ODOO_RC or "
            "OPENERP_SERVER environment variables, "
            "or ~/.odoorc (Odoo >= 10) "
            "or ~/.openerp_serverrc.",
        )
        @click.option(
            "--addons-path",
            envvar=["ODOO_ADDONS_PATH"],
            help="Specify the addons path. If present, this "
            "parameter takes precedence over the addons path "
            "provided in the Odoo configuration file.",
        )
        @click.option(
            "--database",
            "-d",
            envvar=["PGDATABASE"],
            help="Specify the database name. If present, this "
            "parameter takes precedence over the database "
            "provided in the Odoo configuration file.",
        )
        @click.option(
            "--log-level",
            default=default_log_level,
            show_default=True,
            help="Specify the logging level. Accepted values depend "
            "on the Odoo version, and include debug, info, "
            "warn, error.",
        )
        @click.option(
            "--logfile", type=click.Path(dir_okay=False), help="Specify the log file."
        )
        @click.option(
            "--rollback",
            is_flag=True,
            help="Rollback the transaction even if the script "
            "does not raise an exception. Note that if the "
            "script itself commits, this option has no effect. "
            "This is why it is not named dry run. This option "
            "is implied when an interactive console is "
            "started.",
        )
        @click.pass_context
        @functools.wraps(func)
        def wrapped(
            ctx,
            config,
            log_level,
            logfile,
            addons_path=None,
            database=None,
            rollback=False,
            *args,
            **kwargs
        ):
            try:
                parse_config(config, database, log_level, logfile, addons_path)
                if not database:
                    database = odoo.tools.config["db_name"]
                if with_database and database_required and not database:
                    raise click.UsageError(
                        "No database provided, please provide one with the -d "
                        "option or the Odoo configuration file."
                    )
                if (
                    with_database
                    and database
                    and (database_must_exist or _db_exists(database))
                ):
                    with environment_manager(
                        ctx, database=database, rollback=rollback
                    ) as env:
                        return func(ctx, env, *args, **kwargs)
                else:
                    with odoo.api.Environment.manage():
                        return func(ctx, None, *args, **kwargs)
            except Exception as e:
                _logger.error("exception", exc_info=True)
                raise click.ClickException(str(e))

        if not with_database:
            _remove_click_option(wrapped, "database")
        if not with_rollback or not with_database:
            _remove_click_option(wrapped, "rollback")
        return wrapped

    return inner


@click.command(
    help="Execute a python script in an initialized Odoo "
    "environment. The script has access to a 'env' global "
    "variable which is an odoo.api.Environment "
    "initialized for the given database. If no script is "
    "provided, the script is read from stdin or an "
    "interactive console is started if stdin appears "
    "to be a terminal."
)
@env_options(database_required=False)
@click.option(
    "--interactive/--no-interactive",
    "-i",
    help="Inspect interactively after running the script.",
)
@click.option(
    "--shell-interface",
    help="Preferred shell interface for interactive mode. Accepted "
    "values are ipython, ptpython, bpython, python. If not "
    "provided they are tried in this order.",
)
@click.argument("script", required=False, type=click.Path(exists=True, dir_okay=False))
@click.argument("script-args", nargs=-1)
def main(_ctx, env, interactive, shell_interface, script, script_args):
    global_vars = {"env": env}
    if script:
        sys.argv[1:] = script_args
        global_vars = runpy.run_path(
            script, init_globals=global_vars, run_name="__main__"
        )
    if not script or interactive:
        if console._isatty(sys.stdin):
            if not env:
                _logger.info("No environment set, use `-d dbname` to get one.")
            console.Shell.interact(global_vars, shell_interface)
            if env:
                env.cr.rollback()
        else:
            sys.argv[:] = [""]
            global_vars["__name__"] = "__main__"
            exec(sys.stdin.read(), global_vars)
