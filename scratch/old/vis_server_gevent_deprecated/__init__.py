# stupid flask.
from gevent import monkey

# see this issue
# https://github.com/hackoregon/team-budget/issues/128#issuecomment-294365717
monkey.patch_all(thread=False)

