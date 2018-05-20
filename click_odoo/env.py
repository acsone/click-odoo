# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager
import logging
import sys

import click

try:
    import odoo
    from odoo.api import Environment
    Registry = odoo.modules.registry.Registry
    odoo_bin = 'odoo'
except ImportError:
    # Odoo < 10
    try:
        import openerp as odoo
        from openerp.api import Environment
        Registry = odoo.modules.registry.RegistryManager
        odoo_bin = 'openerp-server'
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


def parse_config(config=None, database=None, log_level=None, logfile=None):
    series = odoo.release.version_info[0]

    odoo_args = []
    if config:
        odoo_args.extend(['-c', config])
    if database:
        odoo_args.extend(['-d', database])
    if log_level:
        odoo_args.extend(['--log-level', log_level])
    if logfile:
        odoo_args.extend(['--logfile', logfile])
    # see https://github.com/odoo/odoo/commit/b122217f74
    odoo.tools.config['load_language'] = None
    odoo.tools.config.parse_config(odoo_args)
    _fix_logging(series)
    odoo.cli.server.report_configuration()


@contextmanager
def OdooEnvironment(config=None, database=None, log_level=None, logfile=None,
                    rollback=False):
    parse_config(config, database, log_level, logfile)

    db_name = odoo.tools.config['db_name']
    if not db_name:
        raise click.ClickException("No database name found. Please provide "
                                   "one with the -d option or the odoo "
                                   "configuration file.")

    with Environment.manage():
        registry = odoo.registry(db_name)
        try:
            with registry.cursor() as cr:
                uid = odoo.SUPERUSER_ID
                try:
                    ctx = Environment(cr, uid, {})['res.users'].context_get()
                except Exception as e:
                    ctx = {'lang': 'en_US'}
                    # this happens, for instance, when there are new
                    # fields declared on res_partner which are not yet
                    # in the database (before -u)
                    _logger.warn(
                        "Could not obtain a user context, continuing "
                        "anyway with a default context. Error was: %s",
                        e
                    )
                env = Environment(cr, uid, ctx)
                cr.rollback()
                try:
                    yield env
                    if rollback:
                        cr.rollback()
                    else:
                        cr.commit()
                except:  # noqa
                    _logger.exception("Exception in OdooEnvironment")
                    raise
        finally:
            Registry.delete(db_name)
            odoo.sql_db.close_db(db_name)
