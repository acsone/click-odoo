# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
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


@contextmanager
def OdooEnvironment(database, rollback=False):
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
