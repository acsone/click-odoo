# noqa
try:
    import odoo.release as release
    import odoo.tools.parse_version as parse_version
except (AttributeError, ImportError):
    import openerp.release as release
    import openerp.tools.parse_version as parse_version

if parse_version(release.version) > parse_version("9.0c"):
    import odoo.addons.addon1  # noqa
else:
    import openerp.addons.addon1  # noqa
