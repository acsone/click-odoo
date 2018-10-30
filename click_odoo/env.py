# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager
import logging
import sys

try:
    import odoo
    from odoo.api import Environment
    odoo_bin = 'odoo'
except ImportError:
    # Odoo < 10
    try:
        import openerp as odoo
        from openerp.api import Environment
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


def _get_config_args(**kwargs):
    """ This method can be patched for custom downstream config API """
    odoo_args = []
    if kwargs.get('config'):
        odoo_args.extend(['-c', kwargs.get('config')])
    if kwargs.get('database'):
        odoo_args.extend(['-d', kwargs.get('database')])
    if kwargs.get('log_level'):
        odoo_args.extend(['--log-level', kwargs.get('log_level')])
    if kwargs.get('logfile'):
        odoo_args.extend(['--logfile', kwargs.get('logfile')])
    if kwargs.get('addons_path'):
        odoo_args.extend(['--addons-path', kwargs.get('addons_path')])
    return odoo_args


def parse_config(config=None, database=None, log_level=None, logfile=None,
                 addons_path=None, additional_odoo_args=None):
    series = odoo.release.version_info[0]

    # reset db_name in case we come from a previous run
    # where database has been set, in the second run the is no database
    # (mostly for tests)
    odoo.tools.config['db_name'] = None
    odoo_args = _get_config_args(
        config=config, database=database, log_level=log_level,
        logfile=logfile, addons_path=addons_path)
    if additional_odoo_args:
        odoo_args.append(additional_odoo_args)
    # see https://github.com/odoo/odoo/commit/b122217f74
    odoo.tools.config['load_language'] = None
    odoo.tools.config.parse_config(odoo_args)
    _fix_logging(series)
    odoo.cli.server.report_configuration()


@contextmanager
def OdooEnvironment(database, rollback=False):
    with Environment.manage():
        registry = odoo.registry(database)
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
                    _logger.warning(
                        "Could not obtain a user context, continuing "
                        "anyway with a default context. Error was: %s",
                        e
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
