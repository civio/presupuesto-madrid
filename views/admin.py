# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from coffin.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME_PATH, HTTPS_PROXY, HTTP_PROXY

import base64
import csv
import collections
import glob
import json
import os
import re
import subprocess
import urllib

DATA_BASE_URL = "https://datos.madrid.es"

GENERAL_URL = {
    2020: "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=9062dd2e34a6f610VgnVCM1000001d4a900aRCRD",
    'historical': "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=14f285e4b1204410VgnVCM1000000b205a0aRCRD",
}

EXECUTION_URL = {
    2020: "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=ce40806727670710VgnVCM1000001d4a900aRCRD",
    2019: "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=93bf1b7ba1939610VgnVCM2000001f4a900aRCRD",
    'historical': "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=b404f67f5b35b410VgnVCM2000000c205a0aRCRD",
}


PAYMENTS_URL = "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=2fd903751cd56610VgnVCM2000001f4a900aRCRD"

TEMP_BASE_PATH = "/tmp/budget_app"


class AdminException(Exception):
    pass


# Main
@never_cache
def admin(request):
    return redirect("admin-execution")


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

    return render(request, "admin/general.html", context)


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

    return render(request, "admin/execution.html", context)


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
    return render(request, "admin/inflation.html", context)


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
    return render(request, "admin/population.html", context)


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

    return render(request, "admin/payments.html", context)


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
    return redirect("admin-glossary-es")


@never_cache
def admin_glossary_es(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return render(request, "admin/glossary_es.html", context)


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
    return render(request, "admin/glossary_en.html", context)


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

    return _execute(cue, *management_commands)


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
        cue = cue.replace(" para ", "para %s de " % month)

    management_commands = (
        "load_budget %s --language=es,en" % year,
        "load_investments %s --language=es,en" % year,
    )
    return _execute(cue, *management_commands)


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

    return _execute(cue, *management_commands)


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
    return _execute(u"Vamos a cargar los datos estadísticos", "load_stats")


def _retrieve_glossary_es():
    return _retrieve("data/glosario_es.csv")


def _retrieve_glossary_en():
    return _retrieve("data/glosario_en.csv")


def _save_glossary_es(content):
    return _save("data/glosario_es.csv", content, "Update spanish glossary data")


def _save_glossary_en(content):
    return _save("data/glosario_en.csv", content, "Update english glossary data")


def _load_glossary_es():
    return _execute(
        u"Vamos a cargar los datos del glosario en español",
        "load_glossary --language=es",
    )


def _load_glossary_en():
    return _execute(
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
    except AdminException:
        message = (
            "<p>Se ha producido un error descargado los datos.</p>"
            "<p>Puedes ver la página desde la que hemos intentado hacer la descarga "
            "<a href='%s' target='_blank'>aquí</a>.</p>" % url
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

        _write_temp(temp_folder_path, ".budget_month", month)
        _write_temp(temp_folder_path, ".budget_year", year)
        _write_temp(temp_folder_path, ".budget_type", "execution")

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
    except AdminException:
        message = (
            "<p>Se ha producido un error descargado los datos.</p>"
            "<p>Puedes ver la página desde la que hemos intentado hacer la descarga "
            "<a href='%s' target='_blank'>aquí</a>.</p>" % url
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
    except AdminException:
        message = (
            "<p>Se ha producido un error descargado los datos.</p>"
            "<p>Puedes ver la página desde la que hemos intentado hacer la descarga "
            "<a href='%s' target='_blank'>aquí</a>.</p>" % url
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
    cmd += "python madrid_check_datafiles.py %s" % data_files_path

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            u"<p>Se ha producido un error revisando los ficheros descargados: "
            "<pre>%s</pre></p>" % output
        )
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    message = (
        u"<p>Los ficheros descargados se han revisado correctamente: "
        "<pre>%s</pre></p>" % (output)
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
        "organismos.csv": [1, 3, 4, 6, 8, 9, 10]
    }

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
            with open(data_filename, "rb") as source:
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

                    columns_to_write = [line[c].decode("iso-8859-1").encode("utf-8") for c in columns_for[data_file]]

                    # we split the data into the amount and the other fields (which we'll use as key)
                    # and we accumulate the amounts
                    key = tuple(columns_to_write[:-1])
                    amount = _parse_spanish_number(columns_to_write[-1])

                    payments[key] = payments.get(key, 0.0) + amount

        with open(target_filename, "ab") as target:
            target.truncate(0)
            writer = csv.writer(target, delimiter=',')

            for key, amount in payments.items():
                row_data = list(key)
                row_data.append(amount)
                writer.writerow(row_data)

        with open(target_filename, "rb") as target:
            reader = csv.reader(target, delimiter=',')

            for index, line in enumerate(reader):
                number_of_payments += 1
                amount_of_payments += float(line[6])

    except Exception as e:
        error = str(e)

    output = "Hay %s pagos que suman un total de %s euros en %s" % (
        _format_number_as_spanish(number_of_payments),
        _format_number_as_spanish(amount_of_payments),
        year
    )

    if error:
        message = (
            u"<p>Se ha producido un error revisando los ficheros descargados: "
            "<pre>%s</pre></p>" % error
        )
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    message = (
        u"<p>Los ficheros descargados se han revisado correctamente: "
        "<pre>%s</pre></p>" % (output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


def _retrieve(file_path):
    try:
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
        _write(file_path, content)
        _commit(file_path, commit_message)

        body = {
            "result": "success",
            "message": "<p>Los datos se han guardado correctamente.</p>",
        }
        status = 200
    except AdminException:
        body = {
            "result": "error",
            "message": "<p>Se ha producido un error guardando los datos.</p>",
        }
        status = 500

    return (body, status)


def _execute(cue, *management_commands):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "export PYTHONIOENCODING=utf-8 "
        "&& cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset --hard origin/master "
        "&& cd %s"
    ) % (THEME_PATH, ROOT_PATH)

    for management_command in management_commands:
        cmd += "&& python manage.py %s " % management_command

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            "<p>No se han podido ejecutar los comandos <code>%s</code>:"
            "<pre>%s</pre></p>"
        ) % (" && ".join(management_commands), output)
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    # Touch project/wsgi.py so the app restarts
    _touch(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>%s.</p>"
        "<p>Ejecutado: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cue, cmd, output)
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
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            _copy(source, destination, ".budget_status")
            _copy(source, destination, "gastos.csv")
            _copy(source, destination, "gastos.csv", "ejecucion_gastos.csv")
            _copy(source, destination, "ingresos.csv")
            _copy(source, destination, "ingresos.csv", "ejecucion_ingresos.csv")
            _copy(source, destination, "inversiones.csv")
            _copy(source, destination, "inversiones.csv", "ejecucion_inversiones.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "Update %s execution data" % year)

    except AdminException as error:
        raise Exception(error)

    return (month, year)


def _arrange_payments(data_files_path):
    # Read the year of the payments data
    year = _read_temp(data_files_path, ".budget_year")

    action = "Add"

    # Copy files around
    try:
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
        page = urllib.urlopen(url).read()
    except IOError as error:
        raise AdminException("Page at '%s' couldn't be fetched: %s" % (url, str(error)))

    return page


def _download(url, temp_folder_path, filename):
    file_path = os.path.join(temp_folder_path, filename)

    try:
        urllib.urlretrieve(url, file_path)
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

    with open(file_path, "rb") as file:
        return file.read()


def _write_temp(temp_folder_path, filename, content):
    file_path = os.path.join(temp_folder_path, filename)

    with open(file_path, "w") as file:
        file.write(content)


def _touch(file_path):
    # The scripts/touch executable must be manually deployed and setuid'ed
    cmd = "cd %s && scripts/touch %s" % (THEME_PATH, file_path)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File '%s' couldn't be touched" % file_path)


def _read(file_path):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = ("cd %s " "&& scripts/git fetch " "&& scripts/git show origin/master:%s") % (
        THEME_PATH,
        file_path,
    )

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be read." % file_path)

    return output


def _write(file_path, content):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    # The scripts/cat executable must be manually deployed and setuid'ed
    cmd = (
        "export PYTHONIOENCODING=utf-8 "
        "&& cd %s "
        "&& cat <<EOF | scripts/tee %s\n"
        "%s"
        "EOF"
    ) % (THEME_PATH, file_path, content)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be written." % file_path)


def _remove(folder_path, filename):
    target = os.path.join(folder_path, filename)

    # The scripts/rm executable must be manually deployed and setuid'ed
    cmd = ("cd %s " "&& scripts/rm -f %s") % (THEME_PATH, target)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be removed." % target)


def _copy(source_path, destination_path, source_filename, destination_filename=None):
    if not destination_filename:
        destination_filename = source_filename

    source = os.path.join(source_path, source_filename)
    destination = os.path.join(destination_path, destination_filename)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # The scripts/cp executable must be manually deployed and setuid'ed
    cmd = ("cd %s " "&& scripts/cp -f %s %s") % (THEME_PATH, source, destination)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be copied." % source_filename)


def _commit(path, commit_message):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset origin/master "
        "&& scripts/git add -A %s "
        "&& git diff-index --quiet HEAD "
        "|| scripts/git commit -m \"%s\n\nChange performed on the admin console.\" "
        "&& scripts/git push"
    ) % (THEME_PATH, path, commit_message)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("Path %s couldn't be commited." % path)


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
    url = GENERAL_URL.get(year, GENERAL_URL['historical'])
    return url


def _get_execution_url(year):
    url = EXECUTION_URL.get(year, EXECUTION_URL['historical'])
    return url


def _get_payments_url(year):
    url = PAYMENTS_URL

    return url


def _get_files(page):
    doc = BeautifulSoup(page, "html.parser")
    links = doc.find_all("a", class_="ico-csv")

    return [DATA_BASE_URL + link["href"] for link in links]


def _get_files_historical(page, year):
    doc = BeautifulSoup(page, "html.parser")
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
    return_code = process.poll()

    output = output.decode("utf8", "backslashreplace")
    error = return_code != 0

    return (output, error)


def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data), content_type="application/json; charset=utf-8", status=status
    )


def _csv_response(data, status=200):
    return HttpResponse(data, content_type="text/csv; charset=utf-8", status=status)
