# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from budget_app.views.helpers import *

def investmentdetails(request, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-entities', title='')

    # Setup active_tab for menu options
    c['active_tab'] = 'investmentdetails'

    return render_response('investmentdetails/index.html', c)
