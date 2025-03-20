import six

if six.PY2:
    from guidedvisit import guidedvisit
    from csv_xls import inflation_stats, population_stats
    from admin import *
else:
    from .guidedvisit import guidedvisit
    from .csv_xls import inflation_stats, population_stats
    from .admin import *
