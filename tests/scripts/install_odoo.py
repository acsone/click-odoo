#!/usr/bin/env python
import os
import subprocess
import sys

import psycopg2


odoo_series = sys.argv[1]
odoo_dir = os.path.join(os.environ['VIRTUAL_ENV'], 'src', 'odoo')
odoo_db = 'odoo-script-test-' + odoo_series.replace('.', '-')
if odoo_series in ('8.0', '9.0'):
    odoo_bin = 'openerp-server'
else:
    odoo_bin = 'odoo'


def odoo_installed():
    try:
        import odoo  # noqa
        return True
    except ImportError:
        # odoo < 10
        try:
            import openerp  # noqa
            return True
        except ImportError:
            # odoo not installed
            return False


def odoo_cloned():
    return os.path.isdir(os.path.join(odoo_dir, '.git'))


def clone_odoo():
    subprocess.check_call([
        'git', 'clone',
        '--depth=1',
        '-b', odoo_series,
        'https://github.com/odoo/odoo',
        odoo_dir,
    ])


def install_odoo():
    subprocess.check_call([
        'pip', 'install',
        '-e', odoo_dir,
    ])


def create_db():
    # createdb if it does not exist
    try:
        with psycopg2.connect(dbname=odoo_db) as conn:
            pass
    except psycopg2.OperationalError:
        subprocess.check_call(['createdb', odoo_db])
    # check if db initialized
    with psycopg2.connect(dbname=odoo_db) as conn:
        with conn.cursor() as cr:
            cr.execute("""
                select * from information_schema.tables
                where table_name='ir_module_module'
            """)
            if cr.rowcount:
                return
    subprocess.check_call([
        odoo_bin,
        '-d', odoo_db,
        '-i', 'base',
        '--stop-after-init',
    ])


def main():
    if not odoo_installed():
        if not odoo_cloned():
            clone_odoo()
        install_odoo()
    create_db()


if __name__ == '__main__':
    main()
