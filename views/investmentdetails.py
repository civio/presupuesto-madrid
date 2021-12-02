# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from budget_app.views.helpers import *

# FIXME: Temporary data storage
data = [
    [2021, 'Arganzuela', 'El mercao', 1000, 10000],
    [2021, 'Arganzuela', 'La estación', 2000, 20000],
    [2021, 'Retiro', 'El parque', 8000, 80000],
]
districts = []
# Object used to define data as literal. See http://stackoverflow.com/a/2466207
class DataPoint(object):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

def investmentdetails(request, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-entities', title='')
    entity = get_main_entity(c)
    set_entity(c, entity)

    # Setup active_tab for menu options
    c['active_tab'] = 'investmentdetails'

    # Get the investments breakdown
    c['area_breakdown'] = BudgetBreakdown(['area', 'description'])
    # FIXME: Temporary data storage
    for item in data:
        # Current year
        data_point = DataPoint(year=item[0], area=item[1], description=item[2], expense=True, is_actual=True, amount=item[3])
        column_name = str(data_point.year)
        c['area_breakdown'].add_item(column_name, data_point)

        # All years
        data_point = DataPoint(year=item[0], area=item[1], description=item[2], expense=True, is_actual=True, amount=item[4])
        column_name = "total_"+str(data_point.year)
        c['area_breakdown'].add_item(column_name, data_point)

    # Get additional information
    populate_entity_descriptions(c, entity)

    return render_response('investmentdetails/index.html', c)
