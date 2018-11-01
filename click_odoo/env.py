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
def OdooEnvironment(self):
    with Environment.manage():
        registry = odoo.registry(self.database)
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
                if self.rollback:
                    cr.rollback()
                else:
                    cr.commit()
        finally:
            if odoo.release.version_info[0] < 10:
                odoo.modules.registry.RegistryManager.delete(self.database)
            else:
                odoo.modules.registry.Registry.delete(self.database)
            odoo.sql_db.close_db(self.database)
