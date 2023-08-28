from django.conf.urls import url

# We can define additional URLs applicable only to the theme. These will get added
# to the project URL patterns list.
EXTRA_URLS = (
    url(r'^visita-guiada$', 'guidedvisit', name='guidedvisit'),
    url(r'^inflacion\.(?P<format>.+)$', 'inflation_stats', name='inflation_stats'),
    url(r'^poblacion\.(?P<format>.+)$', 'population_stats', name='population_stats'),

    url(r'^admin/?$', 'admin', name='admin'),

    url(r'^admin/general$', 'admin_general', name='admin_general'),
    url(r'^admin/general/retrieve$', 'admin_general_retrieve'),
    url(r'^admin/general/review$', 'admin_general_review'),
    url(r'^admin/general/load$', 'admin_general_load'),

    url(r'^admin/execution$', 'admin_execution', name='admin_execution'),
    url(r'^admin/execution/retrieve$', 'admin_execution_retrieve'),
    url(r'^admin/execution/review$', 'admin_execution_review'),
    url(r'^admin/execution/load$', 'admin_execution_load'),

    url(r'^admin/monitoring$', 'admin_monitoring', name='admin_monitoring'),
    url(r'^admin/monitoring/retrieve$', 'admin_monitoring_retrieve'),
    url(r'^admin/monitoring/load$', 'admin_monitoring_load'),

    url(r'^admin/main-investments$', 'admin_main_investments', name='admin_main_investments'),
    url(r'^admin/main-investments/retrieve$', 'admin_main_investments_retrieve'),
    url(r'^admin/main-investments/load$', 'admin_main_investments_load'),

    url(r'^admin/inflation$', 'admin_inflation', name='admin_inflation'),
    url(r'^admin/inflation/retrieve$', 'admin_inflation_retrieve'),
    url(r'^admin/inflation/save$', 'admin_inflation_save'),
    url(r'^admin/inflation/load$', 'admin_inflation_load'),

    url(r'^admin/population$', 'admin_population', name='admin_population'),
    url(r'^admin/population/retrieve$', 'admin_population_retrieve'),
    url(r'^admin/population/save$', 'admin_population_save'),
    url(r'^admin/population/load$', 'admin_population_load'),

    url(r'^admin/payments$', 'admin_payments', name='admin_payments'),
    url(r'^admin/payments/retrieve$', 'admin_payments_retrieve'),
    url(r'^admin/payments/review$', 'admin_payments_review'),
    url(r'^admin/payments/load$', 'admin_payments_load'),

    url(r'^admin/glossary$', 'admin_glossary', name='admin_glossary'),

    url(r'^admin/glossary/es$', 'admin_glossary_es', name='admin_glossary_es'),
    url(r'^admin/glossary/es/retrieve$', 'admin_glossary_es_retrieve'),
    url(r'^admin/glossary/es/save$', 'admin_glossary_es_save'),
    url(r'^admin/glossary/es/load$', 'admin_glossary_es_load'),

    url(r'^admin/glossary/en$', 'admin_glossary_en', name='admin_glossary_en'),
    url(r'^admin/glossary/en/retrieve$', 'admin_glossary_en_retrieve'),
    url(r'^admin/glossary/en/save$', 'admin_glossary_en_save'),
    url(r'^admin/glossary/en/load$', 'admin_glossary_en_load'),
)
