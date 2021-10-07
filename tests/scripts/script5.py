# noqa
try:
    import odoo.release as release
except (AttributeError, ImportError):
    import openerp.release as release

if release.version_info < (10, 0):
    import openerp.addons.addon1  # noqa
else:
    import odoo.addons.addon1  # noqa
