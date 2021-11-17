# ENVIRONMENT-SPECIFIC SETTINGS
#
ENV = {
  'THEME': 'presupuesto-mollet',
  'DEBUG': True,
  'TEMPLATE_DEBUG': True,
  # Database
  'DATABASE_NAME': 'dvmi_mollet_dev',
  'DATABASE_USER': '',
  'DATABASE_PASSWORD': '',
  # 'SEARCH_CONFIG': 'unaccent_spa',
  # Caching
  'CACHES': {
      'default': {
          'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
  }
}