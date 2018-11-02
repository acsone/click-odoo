# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import sys
from contextlib import closing

import click
from click.decorators import _param_memo  # XXX undocumented click internal

from .env import OdooEnvironment, odoo

_logger = logging.getLogger(__name__)


class env_options(object):
    def __init__(
        self,
        default_log_level="info",
        with_rollback=True,
        with_database=True,
        database_required=True,
        database_must_exist=True,
        with_addons_path=False,
        environment_manager=OdooEnvironment,
    ):
        self.default_log_level = default_log_level
        self.with_rollback = with_rollback
        self.with_database = with_database
        self.database_required = database_required
        self.database_must_exist = database_must_exist
        self.with_addons_path = with_addons_path
        self.environment_manager = environment_manager

    def __call__(self, f):
        # this is the decorator call which registers options in reverse order
        if self.with_rollback:
            _param_memo(
                f,
                click.Option(
                    ("--rollback",),
                    is_flag=True,
                    help="Rollback the transaction even if the script "
                    "does not raise an exception. Note that if the "
                    "script itself commits, this option has no effect. "
                    "This is why it is not named dry run. This option "
                    "is implied when an interactive console is "
                    "started.",
                ),
            )
        _param_memo(
            f,
            click.Option(
                ("--logfile",),
                type=click.Path(dir_okay=False),
                help="Specify the log file.",
            ),
        )
        _param_memo(
            f,
            click.Option(
                ("--log-level",),
                default=self.default_log_level,
                show_default=True,
                help="Specify the logging level. Accepted values depend "
                "on the Odoo version, and include debug, info, "
                "warn, error.",
            ),
        )
        if self.with_database:
            _param_memo(
                f,
                click.Option(
                    ("--database", "-d"),
                    envvar=["PGDATABASE"],
                    help="Specify the database name. If present, this "
                    "parameter takes precedence over the database "
                    "provided in the Odoo configuration file.",
                ),
            )
        if self.with_addons_path:
            _param_memo(
                f,
                click.Option(
                    ("--addons-path",),
                    envvar=["ODOO_ADDONS_PATH"],
                    help="Specify the addons path. If present, this "
                    "parameter takes precedence over the addons path "
                    "provided in the Odoo configuration file.",
                ),
            )
        _param_memo(
            f,
            click.Option(
                ("--config", "-c"),
                envvar=["ODOO_RC", "OPENERP_SERVER"],
                type=click.Path(exists=True, dir_okay=False),
                callback=self._register,
                help="Specify the Odoo configuration file. Other "
                "ways to provide it are with the ODOO_RC or "
                "OPENERP_SERVER environment variables, "
                "or ~/.odoorc (Odoo >= 10) "
                "or ~/.openerp_serverrc.",
            ),
        )
        return f

    def _register(self, ctx, param, value):
        if ctx.command.invoke != self._invoke:
            self.org_invoke = ctx.command.invoke
            ctx.command.invoke = self._invoke
        return value

    def _fix_odoo_logging(self):
        if odoo.release.version_info[0] < 9:
            handlers = logging.getLogger().handlers
            if handlers and len(handlers) == 1:
                handler = handlers[0]
                if isinstance(handler, logging.StreamHandler):
                    if handler.stream is sys.stdout:
                        handler.stream = sys.stderr

    def get_odoo_args(self, ctx):
        """Return a list of Odoo command line arguments from the Click context."""
        config = ctx.params.get("config")
        addons_path = ctx.params.get("addons_path")
        database = ctx.params.get("database")
        log_level = ctx.params.get("log_level")
        logfile = ctx.params.get("logfile")

        odoo_args = []

        if config:
            odoo_args.extend(["--config", config])
        if addons_path:
            odoo_args.extend(["--addons-path", addons_path])
        if database:
            odoo_args.extend(["--database", database])
        if log_level:
            odoo_args.extend(["--log-level", log_level])
        if logfile:
            odoo_args.extend(["--logfile", logfile])

        return odoo_args

    def _configure_odoo(self, ctx):
        odoo_args = self.get_odoo_args(ctx)
        # reset db_name in case we come from a previous run
        # where database has been set, in the second run there is no database
        # (mostly for tests)
        odoo.tools.config["db_name"] = None
        # see https://github.com/odoo/odoo/commit/b122217f74
        odoo.tools.config["load_language"] = None
        odoo.tools.config.parse_config(odoo_args)
        self._fix_odoo_logging()
        odoo.cli.server.report_configuration()

    def _db_exists(self, dbname):
        conn = odoo.sql_db.db_connect("postgres")
        with closing(conn.cursor()) as cr:
            cr._obj.execute(
                "SELECT datname FROM pg_catalog.pg_database "
                "WHERE lower(datname) = lower(%s)",
                (dbname,),
            )
            return bool(cr.fetchone())

    def _pop_params(self, ctx):
        ctx.params.pop("config", None)
        ctx.params.pop("addons_path", None)
        ctx.params.pop("database", None)
        ctx.params.pop("log_level", None)
        ctx.params.pop("logfile", None)
        ctx.params.pop("rollback", None)

    def _invoke(self, ctx):
        try:
            self._configure_odoo(ctx)
            database = ctx.params.get("database") or odoo.tools.config["db_name"]
            rollback = ctx.params.get("rollback")
            # pop env_options params so they are not passed to the command
            self._pop_params(ctx)
            if self.with_database and self.database_required and not database:
                raise click.UsageError(
                    "No database provided, please provide one with the -d "
                    "option or the Odoo configuration file."
                )
            if (
                self.with_database
                and database
                and (self.database_must_exist or self._db_exists(database))
            ):
                with self.environment_manager(
                    database=database, rollback=rollback
                ) as env:
                    ctx.params["env"] = env
                    return self.org_invoke(ctx)
            else:
                with odoo.api.Environment.manage():
                    ctx.params["env"] = None
                    return self.org_invoke(ctx)
        except click.exceptions.Exit:
            raise
        except Exception as e:
            _logger.error("exception", exc_info=True)
            raise click.ClickException(str(e))
