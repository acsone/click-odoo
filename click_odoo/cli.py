#!/usr/bin/env python
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import runpy
import sys
from contextlib import closing

import click

from . import console, options
from .env import OdooEnvironment, odoo

_logger = logging.getLogger(__name__)


def _db_exists(dbname):
    conn = odoo.sql_db.db_connect("postgres")
    with closing(conn.cursor()) as cr:
        cr._obj.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower(%s)",
            (dbname,),
        )
        return bool(cr.fetchone())


class CommandWithOdooEnv(click.Command):
    def __init__(self, env_options=None, *args, **kwargs):
        if not env_options:
            env_options = {}
        super(CommandWithOdooEnv, self).__init__(*args, **kwargs)
        self.database = None
        self.rollback = None
        self.with_rollback = env_options.get("with_rollback", True)
        self.with_database = env_options.get("with_database", True)
        self.with_addons_path = env_options.get("with_addons_path", False)
        self.database_must_exist = env_options.get("database_must_exist", True)
        self.database_required = self.with_database and env_options.get(
            "database_required", True
        )
        self.environment_manager = env_options.get(
            "environment_manager", OdooEnvironment
        )

        self.env_params = {
            options.config_opt,
            options.addons_path_opt if self.with_addons_path else None,
            options.db_opt if self.with_database else None,
            options.log_level_opt,
            options.logfile_opt,
            options.rollback_opt if self.with_rollback else None,
        }
        self.env_params = [p for p in self.env_params if p]
        self.params.extend(self.env_params)  # So they appear in --help

    def _parse_env_args(self, ctx):
        odoo_args = []
        # reset db_name in case we come from a previous run
        # where database has been set, in the second run the is no database
        # (mostly for tests)
        odoo.tools.config["db_name"] = None
        # Always present params
        if ctx.params.get("config"):
            odoo_args.extend(["-c", ctx.params["config"]])
        del ctx.params["config"]
        if ctx.params.get("log_level"):
            odoo_args.extend(["--log-level", ctx.params["log_level"]])
        del ctx.params["log_level"]
        if ctx.params.get("logfile"):
            odoo_args.extend(["--logfile", ctx.params["logfile"]])
        del ctx.params["logfile"]
        # Conditionally present params
        if ctx.params.get("addons_path"):
            odoo_args.extend(["--addons-path", ctx.params["addons_path"]])
        if "addons_path" in ctx.params:
            del ctx.params["addons_path"]
        if ctx.params.get("database"):
            odoo_args.extend(["-d", ctx.params["database"]])
        if "database" in ctx.params:
            del ctx.params["database"]
        if ctx.params.get("rollback"):
            self.rollback = ctx.params["rollback"]
        if "rollback" in ctx.params:
            del ctx.params["rollback"]
        return odoo_args

    def load_odoo_config(self, ctx):
        series = odoo.release.version_info[0]

        def _fix_logging(series):
            if series < 9:
                handlers = logging.getLogger().handlers
                if handlers and len(handlers) == 1:
                    handler = handlers[0]
                    if isinstance(handler, logging.StreamHandler):
                        if handler.stream is sys.stdout:
                            handler.stream = sys.stderr

        odoo_args = self._parse_env_args(ctx)
        # see https://github.com/odoo/odoo/commit/b122217f74
        odoo.tools.config["load_language"] = None
        odoo.tools.config.parse_config(odoo_args)
        self.database = odoo.tools.config["db_name"] if self.with_database else False
        if self.database_required and not self.database:
            raise click.UsageError(
                "No database provided, please provide one with the -d "
                "option or the Odoo configuration file."
            )
        if self.database and self.database_must_exist and not _db_exists(self.database):
            raise click.UsageError(
                "The provided database does not exists and this script requires"
                " an pre-existing database."
            )
        elif self.database and not _db_exists(self.database):
            self.database = False
        _fix_logging(series)
        odoo.cli.server.report_configuration()

    def invoke(self, ctx):
        self.load_odoo_config(ctx)
        try:
            if self.database:
                with self.environment_manager(self) as env:
                    ctx.params["env"] = env
                    return super(CommandWithOdooEnv, self).invoke(ctx)
            else:
                with odoo.api.Environment.manage():
                    ctx.params["env"] = None
                    return super(CommandWithOdooEnv, self).invoke(ctx)
        except Exception as e:
            _logger.error("exception", exc_info=True)
            raise click.ClickException(str(e))


@click.command(
    cls=CommandWithOdooEnv,
    env_options={"database_required": False, "with_addons_path": True},
)
@options.interactive_opt
@options.shell_interface_opt
@options.script_arg
@options.script_args_arg
def main(env, interactive, shell_interface, script, script_args):
    """Execute a python script in an initialized Odoo environment. The script
    has access to a 'ctx.env' global variable which is an odoo.api.Environment
    initialized for the given database. If no script is provided, the script is
    read from stdin or an interactive console is started if stdin appears to be
    a terminal."""
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
