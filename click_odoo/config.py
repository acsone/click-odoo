# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .env import odoo, fix_logging


class OdooConfig(object):
    """ Construct class for odoo command line args """

    def __init__(self, config=None, database=None,
                 log_level=None, logfile=None, addons_path=None,
                 *args, **kwargs):
        self.config = config
        self.database = database
        self.log_level = log_level
        self.logfile = logfile
        self.addons_path = addons_path
        self.args = args
        self.kwargs = kwargs

    def _parse(self):
        odoo_args = []
        if self.config:
            odoo_args.extend(['-c', self.config])
        if self.database:
            odoo_args.extend(['-d', self.database])
        if self.log_level:
            odoo_args.extend(['--log-level', self.log_level])
        if self.logfile:
            odoo_args.extend(['--logfile', self.logfile])
        if self.addons_path:
            odoo_args.extend(["--addons-path", self.addons_path])
        return odoo_args

    def seed(self):
        """ Seed the odoo config object """

        # reset db_name in case we come from a previous run
        # where database has been set, in the second run the is no database
        # (mostly for tests)
        odoo.tools.config['db_name'] = None
        # see https://github.com/odoo/odoo/commit/b122217f74
        odoo.tools.config['load_language'] = None
        odoo.tools.config.parse_config(self._parse())
        fix_logging()
        odoo.cli.server.report_configuration()
