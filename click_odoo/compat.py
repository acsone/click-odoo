import contextlib

__all__ = [
    "Environment",
    "environment_manage",
    "odoo",
    "odoo_bin",
    "odoo_version_info",
]

try:
    import odoo
    from odoo.api import Environment
except ImportError as e:
    if hasattr(e, "name") and e.name != "odoo":
        raise
    # Odoo < 10
    try:
        import openerp as odoo
        from openerp.api import Environment
    except ImportError:
        if hasattr(e, "name") and e.name != "openerp":
            raise
        raise ImportError("No module named odoo nor openerp")


try:
    from odoo.release import version_info as odoo_version_info
except ImportError:
    from openerp.release import version_info as odoo_version_info


if odoo_version_info < (10, 0):
    odoo_bin = "openerp-server"
else:
    odoo_bin = "odoo"


if odoo_version_info < (15, 0):
    environment_manage = Environment.manage
else:

    @contextlib.contextmanager
    def environment_manage():
        # Environment.manage is a no-op in Odoo 15+, but it
        # emits a noisy warning so let's avoid it.
        yield
