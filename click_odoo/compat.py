import contextlib

__all__ = [
    "Environment",
    "environment_manage",
    "odoo",
    "odoo_bin",
    "odoo_version_info",
]

import odoo
from odoo.api import Environment
from odoo.release import version_info as odoo_version_info

odoo_bin = "odoo"


if odoo_version_info < (15, 0):
    environment_manage = Environment.manage
else:

    @contextlib.contextmanager
    def environment_manage():
        # Environment.manage is a no-op in Odoo 15+, but it
        # emits a noisy warning so let's avoid it.
        yield
