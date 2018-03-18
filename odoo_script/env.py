# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager
import signal

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


@contextmanager
def OdooEnvironment(config=None, database=None, log_level=None):
    odoo_args = []
    if config:
        odoo_args.extend(['-c', config])
    if database:
        odoo_args.extend(['-d', database])
    if log_level:
        odoo_args.extend(['--log-level', log_level])
    # see https://github.com/odoo/odoo/commit/b122217f74
    odoo.tools.config['load_language'] = None
    odoo.tools.config.parse_config(odoo_args)
    db_name = odoo.tools.config['db_name']
    if not db_name:
        raise click.ClickException("No database name found.")
    odoo.tools.config['workers'] = 0
    odoo.tools.config['max_cron_threads'] = 0
    odoo.tools.config['xmlrpc'] = False
    odoo.service.server.start(preload=[], stop=True)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    with Environment.manage():
        if odoo.release.version_info[0] > 9:
            registry = odoo.modules.registry.Registry(db_name)
        else:
            registry = odoo.modules.registry.RegistryManager.get(db_name)
        with registry.cursor() as cr:
            uid = odoo.SUPERUSER_ID
            ctx = Environment(cr, uid, {})['res.users'].context_get()
            env = Environment(cr, uid, ctx)
            try:
                yield env
            finally:
                cr.rollback()
