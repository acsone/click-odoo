# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import sys
from contextlib import contextmanager

try:
    import odoo
    from odoo.api import Environment

    odoo_bin = "odoo"
except ImportError:
    # Odoo < 10
    try:
        import openerp as odoo
        from openerp.api import Environment

        odoo_bin = "openerp-server"
    except ImportError:
        raise ImportError("No module named odoo nor openerp")

_logger = logging.getLogger(__name__)


def _fix_logging(series):
    if series < 9:
        handlers = logging.getLogger().handlers
        if handlers and len(handlers) == 1:
            handler = handlers[0]
            if isinstance(handler, logging.StreamHandler):
                if handler.stream is sys.stdout:
                    handler.stream = sys.stderr


def parse_config(
    config=None, database=None, log_level=None, logfile=None, addons_path=None
):
    series = odoo.release.version_info[0]

    odoo_args = []
    # reset db_name in case we come from a previous run
    # where database has been set, in the second run the is no database
    # (mostly for tests)
    odoo.tools.config["db_name"] = None
    if config:
        odoo_args.extend(["-c", config])
    if database:
        odoo_args.extend(["-d", database])
    if log_level:
        odoo_args.extend(["--log-level", log_level])
    if logfile:
        odoo_args.extend(["--logfile", logfile])
    if addons_path:
        odoo_args.extend(["--addons-path", addons_path])
    # see https://github.com/odoo/odoo/commit/b122217f74
    odoo.tools.config["load_language"] = None
    odoo.tools.config.parse_config(odoo_args)
    _fix_logging(series)
    odoo.cli.server.report_configuration()


@contextmanager
def OdooEnvironment(database, rollback=False, *args, **kwargs):
    with Environment.manage():
        registry = odoo.registry(database)
        try:
            with registry.cursor() as cr:
                uid = odoo.SUPERUSER_ID
                try:
                    ctx = Environment(cr, uid, {})["res.users"].context_get()
                except Exception as e:
                    ctx = {"lang": "en_US"}
                    # this happens, for instance, when there are new
                    # fields declared on res_partner which are not yet
                    # in the database (before -u)
                    _logger.warning(
                        "Could not obtain a user context, continuing "
                        "anyway with a default context. Error was: %s",
                        e,
                    )
                env = Environment(cr, uid, ctx)
                cr.rollback()
                yield env
                if rollback:
                    cr.rollback()
                else:
                    cr.commit()
        finally:
            if odoo.release.version_info[0] < 10:
                odoo.modules.registry.RegistryManager.delete(database)
            else:
                odoo.modules.registry.Registry.delete(database)
            odoo.sql_db.close_db(database)
