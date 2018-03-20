Changes
~~~~~~~

.. Future (?)
.. ----------
.. -

1.0.0b1 (2018-03-20)
--------------------
- clear cache when starting environment (mostly useful for tests)
- simplify and test transaction and exception handling
- when leaving the env, log the exception to be sure it is visible
  when using ``--logfile``

1.0.0a2 (2018-03-19)
--------------------
- improve transaction management: avoid some rare deadlock
- avoid masking original exception in case of error during rollback
- make sure scripts launched by click-odoo have ``__name__ == '__main__'``
- add ``--logfile option``


1.0.0a1 (2018-03-19)
--------------------
- first alpha
