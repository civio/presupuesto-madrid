# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from budget_app.views.helpers import *

def guidedvisit(request, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-entities', title=_(u'Visita guiada'))

    return render_response('guidedvisit/index.html', c)
