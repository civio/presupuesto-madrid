# -*- coding: UTF-8 -*-

# Some environment setup is needed for this to work.
# See https://github.com/civio/presupuesto-management/issues/1235#issuecomment-1614674582 for details.

from bs4 import BeautifulSoup
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME_PATH, HTTPS_PROXY, HTTP_PROXY
from budget_app.views.helpers import _set_meta_fields

import base64
import cgi
import csv
import collections
import glob
import json
import os
import re
import six
import subprocess
import urllib

# urllib2 has changed significantly in Python 3
if six.PY2:
    from urllib2 import Request, urlopen
else:
    from urllib.request import Request, urlopen

DATA_BASE_URL = "https://datos.madrid.es"

# XXX: All the "general" stuff should be renamed just "budget"
GENERAL_URL = {
    2025: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=09506692c611d810VgnVCM1000001d4a900aRCRD",
    2023: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=fa75acf8d2f1e710VgnVCM2000001f4a900aRCRD",
    2022: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=fa75acf8d2f1e710VgnVCM2000001f4a900aRCRD",
    2021: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=ca760ce04fcc6710VgnVCM2000001f4a900aRCRD",
    2020: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=9062dd2e34a6f610VgnVCM1000001d4a900aRCRD",
    'historical': "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=14f285e4b1204410VgnVCM1000000b205a0aRCRD"
}

EXECUTION_URL = {
    'current': "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=c58a15fef2bb6810VgnVCM2000001f4a900aRCRD",
    2022: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=09ad39ec02e3f710VgnVCM2000001f4a900aRCRD",
    2021: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=a1940380e0228710VgnVCM1000001d4a900aRCRD",
    2020: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=ce40806727670710VgnVCM1000001d4a900aRCRD",
    'historical': "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=b404f67f5b35b410VgnVCM2000000c205a0aRCRD"
}

MONITORING_URL = "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=16d65b932be71810VgnVCM2000001f4a900aRCRD"

MAIN_INVESTMENTS_URL = "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=77dee5d0fed7c710VgnVCM1000001d4a900aRCRD"

PAYMENTS_URL = "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=2fd903751cd56610VgnVCM2000001f4a900aRCRD"

TEMP_BASE_PATH = "/tmp/budget_app"

# Select the Python interpreter for external commands based on the version we're running
if six.PY2:
    PYTHON = "python2"
else:
    PYTHON = "python3"

# Add global variable to control whether we should dry run git commands, useful for development
IS_GIT_DRY_RUN = False

class AdminException(Exception):
    pass


# Main
@never_cache
def admin(request):
    return redirect("admin_execution")


# General budget
@never_cache
def admin_general(request):
    current_year = datetime.today().year
    previous_years = [year for year in range(2016, current_year)]

    context = {
        "title_prefix": _(u"Presupuesto general"),
        "active_tab": "general",
        "current_year": current_year,
        "previous_years": previous_years,
    }

    return _html_response(request, "admin/general.html", context)

@never_cache
def admin_general_retrieve(request):
    year = _get_year(request.GET)
    body, status = _retrieve_general(year)
    return _json_response(body, status)

@never_cache
def admin_general_review(request):
    body, status = _review_general()
    return _json_response(body, status)

@never_cache
def admin_general_load(request):
    body, status = _load_general()
    return _json_response(body, status)


# Execution
@never_cache
def admin_execution(request):
    current_year = datetime.today().year
    previous_years = [year for year in range(2017, current_year)]

    context = {
        "title_prefix": _(u"Ejecución mensual"),
        "active_tab": "execution",
        "current_year": current_year,
        "previous_years": previous_years,
    }

    return _html_response(request, "admin/execution.html", context)

@never_cache
def admin_execution_retrieve(request):
    month = _get_month(request.GET)
    year = _get_year(request.GET)
    body, status = _retrieve_execution(month, year)
    return _json_response(body, status)

@never_cache
def admin_execution_review(request):
    body, status = _review_execution()
    return _json_response(body, status)

@never_cache
def admin_execution_load(request):
    body, status = _load_execution()
    return _json_response(body, status)


# Inflation
@never_cache
def admin_inflation(request):
    context = {"title_prefix": _(u"Inflación"), "active_tab": "inflation"}
    return _html_response(request, "admin/inflation.html", context)

@never_cache
def admin_inflation_retrieve(request):
    body, status = _retrieve_inflation()
    return _csv_response(body, status)

@never_cache
def admin_inflation_save(request):
    content = _get_content(request.POST)
    body, status = _save_inflation(content)
    return _json_response(body, status)

@never_cache
def admin_inflation_load(request):
    body, status = _load_stats()
    return _json_response(body, status)


# Population
@never_cache
def admin_population(request):
    context = {"title_prefix": _(u"Población"), "active_tab": "population"}
    return _html_response(request, "admin/population.html", context)

@never_cache
def admin_population_retrieve(request):
    body, status = _retrieve_population()
    return _csv_response(body, status)

@never_cache
def admin_population_save(request):
    content = _get_content(request.POST)
    body, status = _save_population(content)
    return _json_response(body, status)

@never_cache
def admin_population_load(request):
    body, status = _load_stats()
    return _json_response(body, status)


# Monitoring
@never_cache
def admin_monitoring(request):
    current_year = datetime.today().year
    previous_years = [year for year in range(2011, current_year)]

    context = {
        "title_prefix": _(u"Objetivos"),
        "active_tab": "monitoring",
        "current_year": current_year,
        "previous_years": previous_years,
    }

    return _html_response(request, "admin/monitoring.html", context)

@never_cache
def admin_monitoring_retrieve(request):
    year = _get_year(request.GET)
    is_year_completed = request.GET.get("yearCompleted", "No")==u'Sí'
    body, status = _retrieve_monitoring(year, is_year_completed)
    return _json_response(body, status)

@never_cache
def admin_monitoring_load(request):
    body, status = _load_monitoring()
    return _json_response(body, status)


# Main investments
@never_cache
def admin_main_investments(request):
    current_year = datetime.today().year
    previous_years = [year for year in range(2018, current_year)]

    context = {
        "title_prefix": _(u"Inversiones principales"),
        "active_tab": "main-investments",
        "current_year": current_year,
        "previous_years": previous_years,
    }

    return _html_response(request, "admin/main_investments.html", context)

@never_cache
def admin_main_investments_retrieve(request):
    year = _get_year(request.GET)
    body, status = _retrieve_main_investments(year)
    return _json_response(body, status)

@never_cache
def admin_main_investments_load(request):
    body, status = _load_main_investments()
    return _json_response(body, status)


# Third party payments
@never_cache
def admin_payments(request):
    last_year = datetime.today().year - 1
    previous_years = [year for year in range(2011, last_year)]

    context = {
        "title_prefix": _(u"Pagos a terceros"),
        "active_tab": "payments",
        "last_year": last_year,
        "previous_years": previous_years,
    }

    return _html_response(request, "admin/payments.html", context)

@never_cache
def admin_payments_retrieve(request):
    year = _get_year(request.GET)
    body, status = _retrieve_payments(year)
    return _json_response(body, status)

@never_cache
def admin_payments_review(request):
    body, status = _review_payments()
    return _json_response(body, status)

@never_cache
def admin_payments_load(request):
    body, status = _load_payments()
    return _json_response(body, status)


# Glossary
@never_cache
def admin_glossary(request):
    return redirect("admin_glossary_es")

@never_cache
def admin_glossary_es(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return _html_response(request, "admin/glossary_es.html", context)

@never_cache
def admin_glossary_es_retrieve(request):
    body, status = _retrieve_glossary_es()
    return _csv_response(body, status)

@never_cache
def admin_glossary_es_save(request):
    content = _get_content(request.POST)
    body, status = _save_glossary_es(content)
    return _json_response(body, status)

@never_cache
def admin_glossary_es_load(request):
    body, status = _load_glossary_es()
    return _json_response(body, status)

@never_cache
def admin_glossary_en(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return _html_response(request, "admin/glossary_en.html", context)

@never_cache
def admin_glossary_en_retrieve(request):
    body, status = _retrieve_glossary_en()
    return _csv_response(body, status)

@never_cache
def admin_glossary_en_save(request):
    content = _get_content(request.POST)
    body, status = _save_glossary_en(content)
    return _json_response(body, status)

@never_cache
def admin_glossary_en_load(request):
    body, status = _load_glossary_en()
    return _json_response(body, status)


# Actions
def _retrieve_general(year):
    data_url = _get_general_url(year)
    return _scrape_general(data_url, year)


def _review_general():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()
    return _review(data_files_path)


def _load_general():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()
    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    year = _arrange_general(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (
        data_files_path,
        year,
    )

    management_commands = (
        "load_budget %s --language=es,en" % year,
        "load_investments %s --language=es,en" % year,
    )

    return _execute_loading_task(cue, *management_commands)


def _retrieve_execution(month, year):
    data_url = _get_execution_url(year)
    return _scrape_execution(data_url, month, year)


def _review_execution():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()
    return _review(data_files_path)


def _load_execution():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()

    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    month, year = _arrange_execution(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (
        data_files_path,
        year,
    )
    if month:
        # Append the month to the end of cue
        cue += " (mes %s)" % month

    management_commands = (
        "load_budget %s --language=es,en" % year,
        "load_investments %s --language=es,en" % year,
        "load_main_investments %s --language=es,en" % year,
        "load_monitoring %s --language=es,en" % year,
    )
    return _execute_loading_task(cue, *management_commands)


def _retrieve_monitoring(year, is_year_completed):
    data_url = _get_monitoring_url(year)
    return _scrape_monitoring(data_url, year, is_year_completed)


def _load_monitoring():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()

    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    year = _arrange_monitoring(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (
        data_files_path,
        year,
    )

    management_commands = (
        "load_monitoring %s --language=es,en" % year,
    )

    return _execute_loading_task(cue, *management_commands)


def _retrieve_main_investments(year):
    data_url = _get_main_investments_url(year)
    return _scrape_main_investments(data_url, year)


def _load_main_investments():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()

    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    year = _arrange_main_investments(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (
        data_files_path,
        year,
    )

    management_commands = (
        "load_main_investments %s --language=es,en" % year,
    )

    return _execute_loading_task(cue, *management_commands)


def _retrieve_payments(year):
    data_url = _get_payments_url(year)
    return _scrape_payments(data_url, year)


def _review_payments():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()
    return _review_payments_data(data_files_path)


def _load_payments():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()

    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    year = _arrange_payments(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (
        data_files_path,
        year,
    )

    management_commands = (
        "load_payments %s --language=es,en" % year,
    )

    return _execute_loading_task(cue, *management_commands)


def _retrieve_inflation():
    return _retrieve("data/inflacion.csv")


def _retrieve_population():
    content, status = _retrieve("data/poblacion.csv")

    content = content.split("\n")

    # We assume a constant file format, newline terminated
    headers = ",".join(content[0].split(",")[2:])
    rows = content[1:-1]

    data = [headers]
    data.extend(
        [
            ",".join(row.split(",")[2:])
            for row in rows
            if row.lstrip('"').startswith("1")
        ]
    )
    data.extend(content[-1:])

    data = "\n".join(data)

    return data, status


def _save_inflation(content):
    return _save("data/inflacion.csv", content, "Update inflation data")


def _save_population(content):
    content = content.split("\n")

    # We assume a constant file format, newline terminated
    headers = '"#Id","#Entidad",%s' % content[0]
    rows = content[1:-1]

    data = [headers]
    data.extend(['"1","Madrid",%s' % row for row in rows])
    data.extend(['"2","Madrid",%s' % row for row in rows])
    data.extend(content[-1:])

    data = "\n".join(data)

    return _save("data/poblacion.csv", data, "Update population data")


def _load_stats():
    return _execute_loading_task(
        u"Vamos a cargar los datos estadísticos",
        "load_stats"
    )


def _retrieve_glossary_es():
    return _retrieve("data/glosario_es.csv")


def _retrieve_glossary_en():
    return _retrieve("data/glosario_en.csv")


def _save_glossary_es(content):
    return _save("data/glosario_es.csv", content, "Update spanish glossary data")


def _save_glossary_en(content):
    return _save("data/glosario_en.csv", content, "Update english glossary data")


def _load_glossary_es():
    return _execute_loading_task(
        u"Vamos a cargar los datos del glosario en español",
        "load_glossary --language=es",
    )


def _load_glossary_en():
    return _execute_loading_task(
        u"Vamos a cargar los datos del glosario en inglés",
        "load_glossary --language=en",
    )


# Action helpers
def _scrape_general(url, year):
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        is_historical = (url == GENERAL_URL['historical'])
        files = _get_files_historical(page, year) if is_historical else _get_files(page)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout: ingresos, gastos, inversiones
        _download(files[0], temp_folder_path, "ingresos.csv")
        _download(files[1], temp_folder_path, "gastos.csv")
        _download(files[2], temp_folder_path, "inversiones.csv")

        _write_temp(temp_folder_path, ".budget_year", year)
        _write_temp(temp_folder_path, ".budget_type", "general")

        # State that no execution data is present
        status = "0M"  # 0M means the year has no execution data

        _write_temp(temp_folder_path, ".budget_status", status)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>"
            % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException as error:
        message = (
            "<p>Se ha producido un error descargando los datos."
            "<pre>%s</pre></p>" % cgi.escape(str(error))
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _scrape_execution(url, month, year):
    month = str(month)
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        is_historical = (url == EXECUTION_URL['historical'])
        files = _get_files_historical(page, year) if is_historical else _get_files(page)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout: ingresos, gastos, inversiones
        _download(files[0], temp_folder_path, "ingresos.csv")
        _download(files[1], temp_folder_path, "gastos.csv")
        _download(files[2], temp_folder_path, "inversiones.csv")
        _download(files[3], temp_folder_path, "ingresos_eliminaciones_bruto.csv")
        _download(files[4], temp_folder_path, "gastos_eliminaciones_bruto.csv")

        _write_temp(temp_folder_path, ".budget_month", month)
        _write_temp(temp_folder_path, ".budget_year", year)
        _write_temp(temp_folder_path, ".budget_type", "execution")

        # Based on the original 'eliminaciones' files, keep only the columns we need.
        # The output files are ISO-8859-1 encoded for historical reasons.
        _csv_cut_columns(temp_folder_path,
            "ingresos_eliminaciones_bruto.csv",
            "ingresos_eliminaciones.csv",
            [0, 1, 6, 6, 7, 8, 9, 10, 11, 13, 14],
            'iso-8859-1')
        _csv_cut_columns(temp_folder_path,
            "gastos_eliminaciones_bruto.csv",
            "gastos_eliminaciones.csv",
            [0, 1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10, 11, 13, 14, 15],
            'iso-8859-1')

        # Keep track of the month of the data
        status = (
            month + "M" if month != "12" else ""
        )  # 12M means the year is fully executed

        _write_temp(temp_folder_path, ".budget_status", status)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>"
            % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException as error:
        message = (
            "<p>Se ha producido un error descargando los datos."
            "<pre>%s</pre></p>" % cgi.escape(str(error))
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _scrape_monitoring(url, year, is_year_completed):
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        files = _get_files_historical(page, year)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout
        _download(files[0], temp_folder_path, "objetivos_e_indicadores.csv")
        _download(files[1], temp_folder_path, "objetivos_y_actividades.csv")

        # Based on the two denormalized source files, create three nicer normalized final ones
        _csv_cut_columns(temp_folder_path,
            "objetivos_e_indicadores.csv",
            "objetivos.csv",
            [4, 5, 6, 14, 15])
        _csv_cut_columns(temp_folder_path,
            "objetivos_y_actividades.csv",
            "actividades.csv",
            [4, 9, 11, 14, 15])

        if is_year_completed:
            _csv_cut_columns(temp_folder_path,
                "objetivos_e_indicadores.csv",
                "indicadores.csv",
                [4, 5, 6, 8, 10, 11, 12, 13])
        else:
            _csv_cut_columns(temp_folder_path,
                "objetivos_e_indicadores.csv",
                "indicadores.csv",
                [4, 5, 6, 8, 10, 11, 12])

        _write_temp(temp_folder_path, ".budget_year", year)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>"
            % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException as error:
        message = (
            "<p>Se ha producido un error descargando los datos."
            "<pre>%s</pre></p>" % cgi.escape(str(error))
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _scrape_main_investments(url, year):
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        files = _get_files_historical(page, year)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout
        _download(files[0], temp_folder_path, "inversiones_principales.csv")

        _write_temp(temp_folder_path, ".budget_year", year)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>"
            % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException as error:
        message = (
            "<p>Se ha producido un error descargando los datos."
            "<pre>%s</pre></p>" % cgi.escape(str(error))
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _scrape_payments(url, year):
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        files = _get_files(page)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout: areas y distritos, organismos autónomos
        _download(files[0], temp_folder_path, "areas_y_distritos.csv")
        _download(files[1], temp_folder_path, "organismos.csv")

        _write_temp(temp_folder_path, ".budget_year", year)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>"
            % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException as error:
        message = (
            "<p>Se ha producido un error descargando los datos."
            "<pre>%s</pre></p>" % cgi.escape(str(error))
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _review(data_files_path):
    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que revisar.</p>"}
        status = 400
        return (body, status)

    # Execute a helper script to check the data files
    script_path = os.path.join(THEME_PATH, "loaders")

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && " % script_path
    cmd += "%s madrid_check_datafiles.py %s" % (PYTHON, data_files_path)

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            u"<p>Se ha producido un error revisando los ficheros descargados: "
            "<pre>%s</pre></p>" % cgi.escape(output)
        )
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    message = (
        u"<p>Los ficheros descargados se han revisado correctamente: "
        "<pre>%s</pre></p>" % cgi.escape(output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


def _review_payments_data(data_files_path):
    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay ficheros que revisar.</p>"}
        status = 400
        return (body, status)

    columns_for = {
        "areas_y_distritos.csv": [1, 3, 4, 7, 9, 10, 11],
        "organismos.csv": [1, 3, 4, 7, 9, 10, 11]
    }

    # Determine file mode based on Python version
    read_mode = "rb" if six.PY2 else "r"
    write_mode = "wb" if six.PY2 else "w"

    # For Python 3, we need to specify newline='' to avoid extra blank lines
    if six.PY2:
        read_params = write_params = {}
    else:
        read_params = write_params = {'newline': '', 'encoding': 'utf-8'}

    error = None

    try:
        # Read the year of the payments data to process
        year = _read_temp(data_files_path, ".budget_year")

        number_of_payments = 0
        amount_of_payments = 0

        target_filename = os.path.join(data_files_path, "pagos.csv")

        payments = collections.OrderedDict()

        for data_file in ["areas_y_distritos.csv", "organismos.csv"]:
            data_filename = os.path.join(data_files_path, data_file)
            with open(data_filename, read_mode, **read_params) as source:
                reader = csv.reader(source, delimiter=';')

                for index, line in enumerate(reader):
                    if re.match("^#", line[0]):  # Ignore comments
                        continue

                    if re.match("^ *$", ''.join(line)):  # Ignore empty lines
                        continue

                    if line[0] == 'Centro':  # Ignore header
                        continue

                    if line[0] != year:  # Ignore not target year
                        continue

                    columns_to_write = [line[c] for c in columns_for[data_file]]

                    # we split the data into the amount and the other fields (which we'll use as key)
                    # and we accumulate the amounts
                    key = tuple(columns_to_write[:-1])
                    amount = _parse_spanish_number(columns_to_write[-1])

                    payments[key] = payments.get(key, 0.0) + amount

        with open(target_filename, write_mode, **write_params) as target:
            writer = csv.writer(target, delimiter=',')

            for key, amount in payments.items():
                row_data = list(key)
                row_data.append(amount)
                writer.writerow(row_data)

        with open(target_filename, read_mode, **read_params) as target:
            reader = csv.reader(target, delimiter=',')

            for index, line in enumerate(reader):
                number_of_payments += 1
                amount_of_payments += float(line[6])

    except Exception as error:
        error = str(error)

    output = "Hay %s pagos que suman un total de %s euros en %s" % (
        _format_number_as_spanish(number_of_payments),
        _format_number_as_spanish(amount_of_payments),
        year
    )

    if error:
        message = (
            u"<p>Se ha producido un error revisando los ficheros descargados: "
            "<pre>%s</pre></p>" % cgi.escape(error)
        )
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    message = (
        u"<p>Los ficheros descargados se han revisado correctamente: "
        "<pre>%s</pre></p>" % cgi.escape(output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


def _retrieve(file_path):
    try:
        _reset_git_status()
        body = _read(file_path)
        status = 200
        return (body, status)
    except AdminException as error:
        raise Exception(error)


def _save(file_path, content, commit_message):
    if not content:
        body = {"result": "error", "message": "<p>Nada que guardar.</p>"}
        status = 400
        return (body, status)

    try:
        _reset_git_status()
        _write(file_path, content)
        _commit(file_path, commit_message)

        body = {
            "result": "success",
            "message": "<p>Los datos se han guardado correctamente.</p>",
        }
        status = 200
    except AdminException as error:
        body = {
            "result": "error",
            "message": "<p>Se ha producido un error guardando los datos: <pre>%s</pre>.</p>" % cgi.escape(str(error)),
        }
        status = 500

    return (body, status)


def _execute_loading_task(cue, *management_commands):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    cmd = (
        "export PYTHONIOENCODING=utf-8 "
        "&& cd %s "
        "&& source env/bin/activate "
    )% (ROOT_PATH, )

    for management_command in management_commands:
        cmd += "&& %s manage.py %s " % (PYTHON, management_command)

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            "<p>No se han podido ejecutar los comandos <code>%s</code>:"
            "<pre>%s</pre></p>"
        ) % (" && ".join(management_commands), cgi.escape(output))
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    # Touch project/wsgi.py so the app restarts
    _touch(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>%s.</p>"
        "<p>Ejecutado: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cue, cmd, cgi.escape(output))
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


# Orchestration helpers
def _arrange_general(data_files_path):
    # Read the year of the budget data
    year = _read_temp(data_files_path, ".budget_year")

    # Copy files around
    try:
        _reset_git_status()
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            _copy(source, destination, ".budget_status")
            _copy(source, destination, "gastos.csv")
            _copy(source, destination, "ingresos.csv")
            _copy(source, destination, "inversiones.csv")

            _remove(destination, "ejecucion_gastos.csv")
            _remove(destination, "ejecucion_ingresos.csv")
            _remove(destination, "ejecucion_inversiones.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "Add %s budget data" % year)

    except AdminException as error:
        raise Exception(error)

    return year


def _arrange_execution(data_files_path):
    # Read the year and month of the budget data
    month = _read_temp(data_files_path, ".budget_month")
    year = _read_temp(data_files_path, ".budget_year")

    # Copy files around
    try:
        _reset_git_status()
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            _copy(source, destination, ".budget_status")
            _copy(source, destination, "gastos.csv")
            _copy(source, destination, "gastos_eliminaciones.csv")
            _copy(source, destination, "gastos.csv", "ejecucion_gastos.csv")
            _copy(source, destination, "gastos_eliminaciones.csv", "ejecucion_gastos_eliminaciones.csv")
            _copy(source, destination, "ingresos.csv")
            _copy(source, destination, "ingresos_eliminaciones.csv")
            _copy(source, destination, "ingresos.csv", "ejecucion_ingresos.csv")
            _copy(source, destination, "ingresos_eliminaciones.csv", "ejecucion_ingresos_eliminaciones.csv")
            _copy(source, destination, "inversiones.csv")
            _copy(source, destination, "inversiones.csv", "ejecucion_inversiones.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "Update %s execution data" % year)

    except AdminException as error:
        raise Exception(error)

    return (month, year)


def _arrange_monitoring(data_files_path):
    year = _read_temp(data_files_path, ".budget_year")

    action = "Add"

    # Copy files around
    try:
        _reset_git_status()
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            action = "Update" if _exists_temp(destination, "objetivos.csv") else action

            _copy(source, destination, "objetivos.csv")
            _copy(source, destination, "actividades.csv")
            _copy(source, destination, "indicadores.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "%s %s monitoring data" % (action, year))

    except AdminException as error:
        raise Exception(error)

    return year


def _arrange_main_investments(data_files_path):
    year = _read_temp(data_files_path, ".budget_year")

    action = "Add"

    # Copy files around
    try:
        _reset_git_status()
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            action = "Update" if _exists_temp(destination, "inversiones_principales.csv") else action

            _copy(source, destination, "inversiones_principales.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "%s %s main investments data" % (action, year))

    except AdminException as error:
        raise Exception(error)

    return year


def _arrange_payments(data_files_path):
    # Read the year of the payments data
    year = _read_temp(data_files_path, ".budget_year")

    action = "Add"

    # Copy files around
    try:
        _reset_git_status()
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            action = "Update" if _exists_temp(destination, "pagos.csv") else action

            _copy(source, destination, "pagos.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "%s %s payments data" % (action, year))

    except AdminException as error:
        raise Exception(error)

    return year


# Network helpers
def _fetch(url):
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla'})
        response = urlopen(request)

        # Convert to string based on Python version
        if six.PY2:
            page = response.read()
        else:
            page = response.read().decode('utf-8', errors='replace')

    except IOError as error:
        raise AdminException("Page at '%s' couldn't be fetched: %s" % (url, cgi.escape(str(error))))

    return page


def _download(url, temp_folder_path, filename):
    try:
        response = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))

        # In the old Python 2 code we used the same method to create a temporary file
        # with some minor content (text) and to save a downloaded file. Not anymore.
        if six.PY2:
            _write_temp(temp_folder_path, filename, response.read(), 'iso-8859-1')
        else:
            with open(os.path.join(temp_folder_path, filename), "wb") as f:
                f.write(response.read())

    except IOError as error:
        raise AdminException(
            "File at '%s' couldn't be downloaded: %s" % (url, str(error))
        )


# Filesystem helpers
def _create_temp_folder():
    base_path = TEMP_BASE_PATH
    temp_folder_path = os.path.join(base_path, str(datetime.now().isoformat()))

    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)

    return temp_folder_path


def _exists_temp(temp_folder_path, filename):
    file_path = os.path.join(temp_folder_path, filename)

    return os.path.exists(file_path)


def _read_temp(temp_folder_path, filename):
    file_path = os.path.join(temp_folder_path, filename)

    if six.PY2:
        with open(file_path, "rb") as file:
            return file.read()
    else:
        with open(file_path, "r") as file:
            return file.read()


def _write_temp(temp_folder_path, filename, content, encoding='utf-8'):
    file_path = os.path.join(temp_folder_path, filename)

    if six.PY2:
        with open(file_path, "w") as file:
            file.write(content)
    else:
        with open(file_path, "w", encoding=encoding) as file:
            file.write(content)


def _touch(file_path):
    # The scripts/touch executable must be manually deployed and setuid'ed
    cmd = "cd %s && scripts/touch %s" % (THEME_PATH, file_path)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File '%s' couldn't be touched: %s\n\n%s" % (file_path, error, output))


def _write(file_path, content):
    # The scripts/cat executable must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& cat <<EOF | scripts/tee %s\n"
        "%s"
        "EOF"
    ) % (THEME_PATH, file_path, content)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be written: %s\n\n%s" % (file_path, error, output))


def _remove(folder_path, filename):
    target = os.path.join(folder_path, filename)

    # The scripts/rm executable must be manually deployed and setuid'ed
    cmd = ("cd %s " "&& scripts/rm -f %s") % (THEME_PATH, target)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be removed: %s\n\n%s" % (target, error, output))


def _copy(source_path, destination_path, source_filename, destination_filename=None):
    if not destination_filename:
        destination_filename = source_filename

    source = os.path.join(source_path, source_filename)
    destination = os.path.join(destination_path, destination_filename)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # The scripts/cp executable must be manually deployed and setuid'ed
    cmd = ("cd %s " "&& scripts/cp -f %s %s") % (THEME_PATH, source, destination)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be copied: %s\n\n%s" % (source_filename, error, output))


# Git helpers
# The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
def _reset_git_status():
    # Do nothing if dry run is enabled
    if IS_GIT_DRY_RUN:
        return "Dry run enabled: skipping git reset..."

    cmd = (
        "cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset --hard origin/master "
     ) % (THEME_PATH, )

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("Couldn't reset git status: %s\n\n%s" % (error, output))

    return output


def _read(file_path):
    cmd = (
        "cd %s "
        "&& scripts/git show origin/master:%s"
    ) % (THEME_PATH, file_path)
    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be read: %s\n\n%s" % (file_path, error, output))

    return output


def _commit(path, commit_message):
    # Do nothing if dry run is enabled
    if IS_GIT_DRY_RUN:
        return "Dry run enabled: skipping git commit..."

    # Why `diff-index`? See https://stackoverflow.com/a/8123841
    cmd = (
        "cd %s"
        "&& scripts/git add -A %s "
        "&& scripts/git diff-index --quiet HEAD "
        "|| scripts/git commit -m \"%s\n\nChange performed on the admin console.\" "
        "&& scripts/git push"
    ) % (THEME_PATH, path, commit_message)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("Path %s couldn't be commited: %s\nExecuting: %s\n\n%s" % (path, str(error), cmd, output))


# Utility helpers
def _format_number_as_spanish(number):
    formatted_number = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", "%18.0f" % number)
    return formatted_number.strip()


def _parse_spanish_number(number):
    # Read number in Spanish format (123.456,78), and return it as English format
    return float(number.strip().replace('.', '').replace(',', '.'))


def _get_content(params):
    content = params.get("content", "")
    return base64.b64decode(content)


def _get_month(params):
    return int(params.get("month", "0"))


def _get_year(params):
    current_year = datetime.today().year
    return int(params.get("year", current_year))


def _get_general_url(year):
    return GENERAL_URL.get(year, GENERAL_URL['historical'])

def _get_execution_url(year):
    if year<2020:
        return EXECUTION_URL['historical']
    else:
        return EXECUTION_URL.get(year, EXECUTION_URL['current'])

def _get_monitoring_url(year):
    return MONITORING_URL

def _get_main_investments_url(year):
    return MAIN_INVESTMENTS_URL

def _get_payments_url(year):
    return PAYMENTS_URL


def _parse_HTML_file(page):
    # There's a weird line that's breaking BeautifulSoup in the PRE/PROD environment,
    # but not in development. Is it the Python version? See civio/presupuesto-management#1234
    # Deleting it is a hacky way of getting rid of the issue, but the best I could find.
    page = re.sub("!function\(t,e\).*", "", page)
    page = re.sub("window.NREUM.*", "", page)
    return BeautifulSoup(page, "html.parser")

def _get_files(page):
    doc = _parse_HTML_file(page)
    links = doc.find_all("a", class_="ico-csv")

    return [DATA_BASE_URL + link["href"] for link in links]

def _get_files_historical(page, year):
    doc = _parse_HTML_file(page)
    year_block = doc.find("p", class_="info-title", text=re.compile(year)).parent.findNext("ul")
    links = year_block.find_all("a", class_="ico-csv")

    return [DATA_BASE_URL + link["href"] for link in links]


def _get_most_recent_temp_folder():
    temp_folder = None

    temp_folders = sorted(glob.glob("%s/*.*" % TEMP_BASE_PATH))

    if temp_folders:
        temp_folder = temp_folders[-1]

    return temp_folder


def _execute_cmd(cmd):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    env = os.environ.copy()

    if HTTP_PROXY:
        env["http_proxy"] = HTTP_PROXY

    if HTTPS_PROXY:
        env["https_proxy"] = HTTPS_PROXY

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        env=env,
        universal_newlines=True,
    )

    output, _ = process.communicate()
    if six.PY2:
        output = output.decode("utf8", "backslashreplace")

    return_code = process.poll()
    error = return_code != 0

    return (output, error)


def _html_response(request, template_name, c):
    _set_meta_fields(c)
    return render(request, template_name, c)

def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data), content_type="application/json; charset=utf-8", status=status
    )

def _csv_response(data, status=200):
    return HttpResponse(data, content_type="text/csv; charset=utf-8", status=status)


# A poor man's version of `csvcut`, it can create a target file using
# a subset of columns from the given source file.
# Note that it also removes duplicates! It was useful for goals data,
# it could be made optional or removed if we use this somewhere else.
def _csv_cut_columns(path, source_filename, target_filename, columns, output_encoding='utf-8'):
    # Determine file mode based on Python version
    read_mode = "rb" if six.PY2 else "r"
    write_mode = "wb" if six.PY2 else "w"

    # For Python 3, we need to specify newline='' to avoid extra blank lines
    if six.PY2:
        read_params = write_params = {}
    else:
        read_params = {'newline': '', 'encoding': 'iso-8859-1'}
        write_params = {'newline': '', 'encoding': output_encoding}

    last_line = []
    with open(os.path.join(path, target_filename), write_mode, **write_params) as target:
        writer = csv.writer(target, delimiter=';')
        with open(os.path.join(path, source_filename), read_mode, **read_params) as source:
            reader = csv.reader(source, delimiter=';')
            for index, line in enumerate(reader):
                columns_to_write = [line[c] for c in columns]
                if columns_to_write == last_line:
                    continue
                writer.writerow(columns_to_write)
                last_line = columns_to_write
