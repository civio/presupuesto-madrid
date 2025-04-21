# -*- coding: UTF-8 -*-

import os
import csv
import six
import sys
import re

from decimal import *


# Read number in English format (123,456.78), and return as number of cents
def read_english_number(s):
    if s.strip() == "":
        return 0

    return int(Decimal(s.replace(',', '')) * 100)


# Read number in Spanish format (123.456,78), and return as number of cents
def parse_spanish_amount(amount):
    amount = amount.replace('.', '')    # Remove thousands delimiters, if any
    return read_english_number(amount.replace(',', '.'))


def format_number_as_spanish(n):
    formatted_number = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", "%18.0f" % n)
    return formatted_number


# We expect the organization code to be one digit, but Madrid has a 3-digit code.
# We can _almost_ pick the last digit, except for one case.
def get_institution_code(madrid_code):
    institution_code = madrid_code if madrid_code != '001' else '000'
    return institution_code[2]


def get_stats(path, is_expense, is_actual):
    total_external = 0
    total_internal_transfer = 0

    filename = os.path.join(path, 'gastos.csv' if is_expense else 'ingresos.csv')

    if six.PY2:
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
    else:
        reader = csv.reader(open(filename, 'r', encoding='iso-8859-1'), delimiter=';')

    for index, line in enumerate(reader):
        if re.match("^#", line[0]):  # Ignore comments
            continue

        if re.match("^ *$", ''.join(line)):  # Ignore empty lines
            continue

        if line[0] == 'Centro':  # Ignore header
            continue

        if is_expense:
            ec_code = line[8]

            # Get institutional code. We ignore sections in autonomous bodies,
            # since they get assigned to different sections in main body but that's
            # not relevant.
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            institution = get_institution_code(line[0].zfill(3))
            ic_code = institution + (line[2].zfill(3) if institution == '0' else '00')

            # Select the amount column to use based on whether we are importing execution
            # or budget data. In the latter case, sometimes we're dealing with the
            # amended budget, sometimes with the just approved one, in which case
            # there're less columns
            budget_position = 12 if len(line) > 11 else 10
            amount = parse_spanish_amount(line[15 if is_actual else budget_position])
        else:
            ec_code = line[4]

            ic_code = get_institution_code(line[0].zfill(3)) + '00'

            # Select the column from which to read amounts. See similar comment above.
            budget_position = 8 if len(line) > 7 else 6
            amount = parse_spanish_amount(line[9 if is_actual else budget_position])

        # We've been asked to ignore data for a special department, not really an organism (#756)
        if ic_code == '200':
            continue

        if ec_code[:-2] in ['410', '710', '400', '700']:
            total_internal_transfer += amount
        else:
            total_external += amount

    return total_external, total_internal_transfer


# Get path to data files
if len(sys.argv) < 2:
    print("Por favor, indica la ruta de los ficheros a comprobar.")
    sys.exit()

path = sys.argv[1]

year = open(os.path.join(path, '.budget_year'), 'r').read()
is_actual = (open(os.path.join(path, '.budget_type'), 'r').read() == "execution")

# Open data files and get some basic stats
incoming_revenues, internal_revenues = get_stats(path, False, is_actual)  # stats for revenues
outgoing_expenses, internal_expenses = get_stats(path, True, is_actual)  # stats for expenses

print("Datos de %s (tras descontar eliminaciones)" % ("ejecución" if is_actual else "presupuesto"))
print("  Ingresos: %s euros" % format_number_as_spanish(incoming_revenues / 100.0))
print("  Gastos  : %s euros" % format_number_as_spanish(outgoing_expenses / 100.0))
print(" ")
print("Eliminaciones")
print("  Ingresos: %s euros" % format_number_as_spanish(internal_revenues / 100.0))
print("  Gastos  : %s euros" % format_number_as_spanish(internal_expenses / 100.0))
