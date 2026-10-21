from django.urls import re_path

# We can't import the theme module directly because it has a hyphen in its name. This works well.
import importlib
theme_views = importlib.import_module('presupuesto_madrid.views')

# We can define additional URLs applicable only to the theme. These will get added
# to the project URL patterns list.
EXTRA_URLS = (
    re_path(r'^visita-guiada$', theme_views.guidedvisit, name='guidedvisit'),
    re_path(r'^inflacion\.(?P<format>.+)$', theme_views.inflation_stats, name='inflation_stats'),
    re_path(r'^poblacion\.(?P<format>.+)$', theme_views.population_stats, name='population_stats'),

    re_path(r'^admin/?$', theme_views.admin, name='admin'),

    re_path(r'^admin/general$', theme_views.admin_general, name='admin_general'),
    re_path(r'^admin/general/retrieve$', theme_views.admin_general_retrieve),
    re_path(r'^admin/general/review$', theme_views.admin_general_review),
    re_path(r'^admin/general/load$', theme_views.admin_general_load),

    re_path(r'^admin/execution$', theme_views.admin_execution, name='admin_execution'),
    re_path(r'^admin/execution/retrieve$', theme_views.admin_execution_retrieve),
    re_path(r'^admin/execution/review$', theme_views.admin_execution_review),
    re_path(r'^admin/execution/load$', theme_views.admin_execution_load),

    re_path(r'^admin/monitoring$', theme_views.admin_monitoring, name='admin_monitoring'),
    re_path(r'^admin/monitoring/retrieve$', theme_views.admin_monitoring_retrieve),
    re_path(r'^admin/monitoring/load$', theme_views.admin_monitoring_load),

    re_path(r'^admin/main-investments$', theme_views.admin_main_investments, name='admin_main_investments'),
    re_path(r'^admin/main-investments/retrieve$', theme_views.admin_main_investments_retrieve),
    re_path(r'^admin/main-investments/load$', theme_views.admin_main_investments_load),

    re_path(r'^admin/inflation$', theme_views.admin_inflation, name='admin_inflation'),
    re_path(r'^admin/inflation/retrieve$', theme_views.admin_inflation_retrieve),
    re_path(r'^admin/inflation/save$', theme_views.admin_inflation_save),
    re_path(r'^admin/inflation/load$', theme_views.admin_inflation_load),

    re_path(r'^admin/population$', theme_views.admin_population, name='admin_population'),
    re_path(r'^admin/population/retrieve$', theme_views.admin_population_retrieve),
    re_path(r'^admin/population/save$', theme_views.admin_population_save),
    re_path(r'^admin/population/load$', theme_views.admin_population_load),

    re_path(r'^admin/payments$', theme_views.admin_payments, name='admin_payments'),
    re_path(r'^admin/payments/retrieve$', theme_views.admin_payments_retrieve),
    re_path(r'^admin/payments/review$', theme_views.admin_payments_review),
    re_path(r'^admin/payments/load$', theme_views.admin_payments_load),

    re_path(r'^admin/glossary$', theme_views.admin_glossary, name='admin_glossary'),

    re_path(r'^admin/glossary/es$', theme_views.admin_glossary_es, name='admin_glossary_es'),
    re_path(r'^admin/glossary/es/retrieve$', theme_views.admin_glossary_es_retrieve),
    re_path(r'^admin/glossary/es/save$', theme_views.admin_glossary_es_save),
    re_path(r'^admin/glossary/es/load$', theme_views.admin_glossary_es_load),

    re_path(r'^admin/glossary/en$', theme_views.admin_glossary_en, name='admin_glossary_en'),
    re_path(r'^admin/glossary/en/retrieve$', theme_views.admin_glossary_en_retrieve),
    re_path(r'^admin/glossary/en/save$', theme_views.admin_glossary_en_save),
    re_path(r'^admin/glossary/en/load$', theme_views.admin_glossary_en_load),
)
