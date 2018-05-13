# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

long_description = []
with open(os.path.join('README.rst')) as f:
    long_description.append(f.read())
with open(os.path.join('CHANGES.rst')) as f:
    long_description.append(f.read())


setup(
    name='click-odoo',
    description='Beautiful, robust CLI for Odoo',
    long_description='\n'.join(long_description),
    use_scm_version=True,
    packages=[
        'click_odoo',
    ],
    include_package_data=True,
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'click',
    ],
    license='LGPLv3+',
    author='ACSONE SA/NV',
    author_email='info@acsone.eu',
    url='http://github.com/acsone/click-odoo',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Odoo',
    ],
    entry_points='''
        [console_scripts]
        click-odoo=click_odoo.cli:main
    ''',
)
