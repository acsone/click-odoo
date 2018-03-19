# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager
import logging
import sys

import click

try:
    import odoo
    from odoo.api import Environment
except ImportError:
    # Odoo < 10
    try:
        import openerp as odoo
        from openerp.api import Environment
    except ImportError:
        raise ImportError("No module named odoo nor openerp")


def _fix_logging(series):
    if series < 9:
        handlers = logging.getLogger().handlers
        if handlers and len(handlers) == 1:
            handler = handlers[0]
            if isinstance(handler, logging.StreamHandler):
                if handler.stream is sys.stdout:
                    handler.stream = sys.stderr


@contextmanager
def OdooEnvironment(config=None, database=None, log_level=None, logfile=None):
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

    db_name = odoo.tools.config['db_name']
    if not db_name:
        raise click.ClickException("No database name found. Please provide "
                                   "one with the -d option or the odoo "
                                   "configuration file.")

    with Environment.manage():
        if series > 9:
            registry = odoo.modules.registry.Registry(db_name)
        else:
            registry = odoo.modules.registry.RegistryManager.get(db_name)
        with registry.cursor() as cr:
            uid = odoo.SUPERUSER_ID
            ctx = Environment(cr, uid, {})['res.users'].context_get()
            env = Environment(cr, uid, ctx)
            cr.commit()
            try:
                yield env
            finally:
                try:
                    cr.rollback()
                except Exception:
                    pass
