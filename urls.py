from django.conf.urls import url

# We can't import the theme module directly because it has a hyphen in its name. This works well.
import importlib
theme_views = importlib.import_module('presupuesto-madrid.views')

# We can define additional URLs applicable only to the theme. These will get added
# to the project URL patterns list.
EXTRA_URLS = (
    url(r'^visita-guiada$', theme_views.guidedvisit, name='guidedvisit'),
    url(r'^inflacion\.(?P<format>.+)$', theme_views.inflation_stats, name='inflation_stats'),
    url(r'^poblacion\.(?P<format>.+)$', theme_views.population_stats, name='population_stats'),

    url(r'^admin/?$', theme_views.admin, name='admin'),

    url(r'^admin/general$', theme_views.admin_general, name='admin_general'),
    url(r'^admin/general/retrieve$', theme_views.admin_general_retrieve),
    url(r'^admin/general/review$', theme_views.admin_general_review),
    url(r'^admin/general/load$', theme_views.admin_general_load),

    url(r'^admin/execution$', theme_views.admin_execution, name='admin_execution'),
    url(r'^admin/execution/retrieve$', theme_views.admin_execution_retrieve),
    url(r'^admin/execution/review$', theme_views.admin_execution_review),
    url(r'^admin/execution/load$', theme_views.admin_execution_load),

    url(r'^admin/monitoring$', theme_views.admin_monitoring, name='admin_monitoring'),
    url(r'^admin/monitoring/retrieve$', theme_views.admin_monitoring_retrieve),
    url(r'^admin/monitoring/load$', theme_views.admin_monitoring_load),

    url(r'^admin/main-investments$', theme_views.admin_main_investments, name='admin_main_investments'),
    url(r'^admin/main-investments/retrieve$', theme_views.admin_main_investments_retrieve),
    url(r'^admin/main-investments/load$', theme_views.admin_main_investments_load),

    url(r'^admin/inflation$', theme_views.admin_inflation, name='admin_inflation'),
    url(r'^admin/inflation/retrieve$', theme_views.admin_inflation_retrieve),
    url(r'^admin/inflation/save$', theme_views.admin_inflation_save),
    url(r'^admin/inflation/load$', theme_views.admin_inflation_load),

    url(r'^admin/population$', theme_views.admin_population, name='admin_population'),
    url(r'^admin/population/retrieve$', theme_views.admin_population_retrieve),
    url(r'^admin/population/save$', theme_views.admin_population_save),
    url(r'^admin/population/load$', theme_views.admin_population_load),

    url(r'^admin/payments$', theme_views.admin_payments, name='admin_payments'),
    url(r'^admin/payments/retrieve$', theme_views.admin_payments_retrieve),
    url(r'^admin/payments/review$', theme_views.admin_payments_review),
    url(r'^admin/payments/load$', theme_views.admin_payments_load),

    url(r'^admin/glossary$', theme_views.admin_glossary, name='admin_glossary'),

    url(r'^admin/glossary/es$', theme_views.admin_glossary_es, name='admin_glossary_es'),
    url(r'^admin/glossary/es/retrieve$', theme_views.admin_glossary_es_retrieve),
    url(r'^admin/glossary/es/save$', theme_views.admin_glossary_es_save),
    url(r'^admin/glossary/es/load$', theme_views.admin_glossary_es_load),

    url(r'^admin/glossary/en$', theme_views.admin_glossary_en, name='admin_glossary_en'),
    url(r'^admin/glossary/en/retrieve$', theme_views.admin_glossary_en_retrieve),
    url(r'^admin/glossary/en/save$', theme_views.admin_glossary_en_save),
    url(r'^admin/glossary/en/load$', theme_views.admin_glossary_en_load),
)
