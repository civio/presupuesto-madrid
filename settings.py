# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, url

MAIN_ENTITY_LEVEL = 'municipio'
MAIN_ENTITY_NAME = 'Madrid'

BUDGET_LOADER = 'MadridBudgetLoader'
PAYMENTS_LOADER = 'MadridPaymentsLoader'
INVESTMENTS_LOADER = 'MadridInvestmentsLoader'
MAIN_INVESTMENTS_LOADER = 'MadridMainInvestmentsLoader'

FEATURED_PROGRAMMES = ['13610', '13510', '16301', '15321', '15210', '23103', '23102', '33401', '33210']


# Use new Sankey visualization or the old one. Default: False
# OVERVIEW_USE_NEW_VIS = True

OVERVIEW_INCOME_NODES = [
                          {
                            'nodes': [['11', '113']],
                            'label.es': 'Impuesto sobre bienes inmuebles de naturaleza urbana',
                            'label.en': 'Tax on urban real estate',
                            'link_id': '11'
                          },
                          '42',
                          {
                            'nodes': [['11', '116']],
                            'label.es': 'Impuesto sobre incremento del valor de terrenos',
                            'label.en': 'Tax on land value increases',
                            'link_id': '11'
                          },
                          {
                            'nodes': ['33'],
                            'label.es': 'Tasas por la utilización del dominio público',
                            'label.en': 'Fees for the use of the public domain',
                            'link_id': '33'
                          },
                          {
                            'nodes': [['30', '303']],
                            'label.es': 'Servicio de tratamiento de residuos',
                            'label.en': 'Waste treatment service',
                            'link_id': '30'
                          },
                        ]
OVERVIEW_EXPENSE_NODES = ['13', '16', '15', '23', '92', '17', '33', '34', '01']

# How aggresive should the Sankey diagram reorder the nodes. Default: 0.79 (Optional)
# Note: 0.5 usually leaves nodes ordered as defined. 0.95 sorts by size (decreasing).
OVERVIEW_RELAX_FACTOR = 0.5

# Treemaps minimum height or width to show labels. Default: 70 (Optional)
TREEMAP_LABELS_MIN_SIZE = 16

# Treemap minimum font size. Default: 11 (Optional)
TREEMAP_LABELS_FONT_SIZE_MIN = 5

# Show Payments section in menu & home options. Default: False.
SHOW_PAYMENTS           = True

# Define if payments year slider is a range (True) or a single year (False). Default: True
PAYMENTS_YEAR_RANGE = False

# Show Investments section in menu & home options. Default: False.
SHOW_INVESTMENTS = True

# Show Main Investments section in menu & home options. Default: False.
SHOW_MAIN_INVESTMENTS = True

# Show Tax Receipt section in menu & home options. Default: False.
# SHOW_TAX_RECEIPT        = True

# Show Counties & Towns links in Policies section in menu & home options. Default: False.
# SHOW_COUNTIES_AND_TOWNS = False

# Show an extra tab with institutional breakdown. Default: True.
# SHOW_INSTITUTIONAL_TAB  = False

# Show an extra treemap in the Policy page, showing institutional breakdown. Default: False.
# Important: insitutional codes must be consistent along the years, see CONSISTENT_INSTITUTIONAL_CODES.
SHOW_GLOBAL_INSTITUTIONAL_TREEMAP  = True

# How many levels to show in the global institutional treemap? Default: 1.
INSTITUTIONAL_MAX_LEVELS = 2

# Show section pages. Still under development, see #347. Default: False.
SHOW_SECTION_PAGES = True

# Are institutional codes consistent along the years. Default: False.
# Important: We need this to be True for the institutional treemap to work properly.
CONSISTENT_INSTITUTIONAL_CODES = True

# Show an extra tab with funding breakdown (only applicable to some budgets). Default: False.
# SHOW_FUNDING_TAB = False

# Show Subtotals panel in Overview. Default: False
SHOW_OVERVIEW_SUBTOTALS = True

# Calculate budget indicators (True), or show/hide the ones hardcoded in HTML (False). Default: True.
# CALCULATE_BUDGET_INDICATORS = False

# Show an extra column with actual revenues/expenses. Default: True.
# Warning: the execution data still gets shown in the summary chart and in downloads.
#SHOW_ACTUAL = True

# Should we group elements at the economic subheading level, or list all of them,
# grouping by uid?. Default: True. (i.e. group by uid, show all elements)
BREAKDOWN_BY_UID = False

# Include financial income/expenditures in overview and global policy breakdowns. Default: True.
INCLUDE_FINANCIAL_CHAPTERS_IN_BREAKDOWNS = True

# Search in entity names. Default: True.
SEARCH_ENTITIES = False


# Number of items per terms page. Default: 10
TERMS_PAGE_LENGTH = 50


# Supported languages. Default: ('es', 'Castellano')
LANGUAGES = (
  ('es', 'Castellano'),
  ('en', 'English'),
)

# Facebook Aplication ID used in social_sharing temaplate. Default: ''
# In order to get the ID create an app in https://developers.facebook.com/
FACEBOOK_ID             = '979582332174600'

# Setup Data Source Budget link
DATA_SOURCE_BUDGET      = 'http://datos.madrid.es/portal/site/egob/menuitem.754985278d15ab64b2c3b244a8a409a0/?vgnextoid=20d612b9ace9f310VgnVCM100000171f5a0aRCRD&text=presupuestos+municipales&buscarEnTitulo=true&btn1=buscar'

# Setup Data Source Population link
DATA_SOURCE_POPULATION  = 'http://www.ine.es/jaxiT3/Tabla.htm?t=2881&L=0'

# Setup Data Source Inflation link
DATA_SOURCE_INFLATION   = 'http://www.ine.es/jaxiT3/Tabla.htm?t=22350&L=0'

# Setup Main Entity Web Url
MAIN_ENTITY_WEB_URL     = 'http://www.madrid.es/'

# Setup Main Entity Legal Url (if empty we hide the link)
MAIN_ENTITY_LEGAL_URL   = 'http://www.madrid.es/portales/munimadrid/avisoLegal.html'

# Setup Main Entity Legal Url (if empty we hide the link)
MAIN_ENTITY_PRIVACY_URL = 'http://www.madrid.es/portales/munimadrid/proteccionDatos.html'

# External URL for Cookies Policy (if empty we use out template page/cookies.html)
COOKIES_URL             = 'http://www.madrid.es/portales/munimadrid/cookies.html'

# Allow overriding of default treemap color scheme
# COLOR_SCALE = [ '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#e7969c', '#bcbd22', '#17becf' ]


# We can define additional URLs applicable only to the theme. These will get added
# to the project URL patterns list.
EXTRA_URLS = (
    url(r"^visita-guiada$", "guidedvisit", name="guidedvisit"),
    url(r"^inflacion\.(?P<format>.+)$", "inflation_stats"),
    url(r"^poblacion\.(?P<format>.+)$", "population_stats"),
    url(r"^admin$", "admin", name="admin"),
    url(r"^admin/general$", "admin_general", name="admin-general"),
    url(r"^admin/general/retrieve$", "admin_general_retrieve", name="admin-general-retrieve"),
    url(r"^admin/general/review$", "admin_general_review", name="admin-general-review"),
    url(r"^admin/general/load$", "admin_general_load", name="admin-general-load"),
    url(r"^admin/execution$", "admin_execution", name="admin-execution"),
    url(r"^admin/execution/retrieve$", "admin_execution_retrieve", name="admin-execution-retrieve"),
    url(r"^admin/execution/review$", "admin_execution_review", name="admin-execution-review"),
    url(r"^admin/execution/load$", "admin_execution_load", name="admin-execution-load"),
    url(r"^admin/inflation$", "admin_inflation", name="admin-inflation"),
    url(r"^admin/inflation/retrieve$", "admin_inflation_retrieve", name="admin-inflation-retrieve"),
    url(r"^admin/inflation/save$", "admin_inflation_save", name="admin-inflation-save"),
    url(r"^admin/inflation/load$", "admin_inflation_load", name="admin-inflation-load"),
    url(r"^admin/population$", "admin_population", name="admin-population"),
    url(r"^admin/population/retrieve$", "admin_population_retrieve", name="admin-population-retrieve"),
    url(r"^admin/population/save$", "admin_population_save", name="admin-population-save"),
    url(r"^admin/population/load$", "admin_population_load", name="admin-population-load"),
    url(r"^admin/payments$", "admin_payments", name="admin-payments"),
    url(r"^admin/payments/retrieve$", "admin_payments_retrieve", name="admin-payments-retrieve"),
    url(r"^admin/payments/review$", "admin_payments_review", name="admin-payments-review"),
    url(r"^admin/payments/load$", "admin_payments_load", name="admin-payments-load"),
    url(r"^admin/glossary$", "admin_glossary", name="admin-glossary"),
    url(r"^admin/glossary/es$", "admin_glossary_es", name="admin-glossary-es"),
    url(r"^admin/glossary/es/retrieve$", "admin_glossary_es_retrieve", name="admin-glossary-es-retrieve"),
    url(r"^admin/glossary/es/save$", "admin_glossary_es_save", name="admin-glossary-es-save"),
    url(r"^admin/glossary/es/load$", "admin_glossary_es_load", name="admin-glossary-esload"),
    url(r"^admin/glossary/en$", "admin_glossary_en", name="admin-glossary-en"),
    url(r"^admin/glossary/en/retrieve$", "admin_glossary_en_retrieve", name="admin-glossary-en-retrieve"),
    url(r"^admin/glossary/en/save$", "admin_glossary_en_save", name="admin-glossary-en-save"),
    url(r"^admin/glossary/en/load$", "admin_glossary_en_load", name="admin-glossary-en-load")
)
