import sys

env = env  # noqa


op = ""
if len(sys.argv) > 1:
    op = sys.argv[1]

ICP = env["ir.config_parameter"]
if hasattr(ICP, "set_str"):
    # Odoo >= 20
    ICP.set_str("testparam", "testvalue")
else:
    ICP.set_param("testparam", "testvalue")
if op == "commit":
    env.cr.commit()
elif op == "rollback":
    env.cr.rollback()
elif op == "raise":
    raise RuntimeError("testerror")
else:
    pass
