# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from __future__ import print_function

import os
from os.path import join as opj
import subprocess

import psycopg2
import pytest


class OdooVirtualenv(object):

    def setUp(self):
        self.create_db()

    def tearDown(self):
        pass

    @property
    def odoo_series(self):
        return os.environ['ODOO_SCRIPT_TEST_SERIES']

    @property
    def odoo_bin(self):
        if self.odoo_series in ('8.0', '9.0'):
            return 'openerp-server'
        else:
            return 'odoo'

    @property
    def odoo_dir(self):
        return opj(os.environ['VIRTUAL_ENV'], 'src', self.odoo_series)

    @property
    def dbname(self):
        return 'odoo-script-test-' + self.odoo_series.replace('.', '-')

    def create_db(self):
        # createdb if it does not exist
        try:
            with psycopg2.connect(dbname=self.dbname) as conn:
                pass
        except psycopg2.OperationalError:
            subprocess.check_call(['createdb', self.dbname])
        # check if db initialized
        with psycopg2.connect(dbname=self.dbname) as conn:
            with conn.cursor() as cr:
                cr.execute("""
                    select * from information_schema.tables
                    where table_name='ir_module_module'
                """)
                if cr.rowcount:
                    return
        subprocess.check_call([
            self.odoo_bin,
            '-d', self.dbname,
            '-i', 'base',
            '--stop-after-init',
        ])


@pytest.fixture(scope="session")
def odoo_venv(request):
    venv = OdooVirtualenv()
    venv.setUp()
    try:
        yield venv
    finally:
        venv.tearDown()
