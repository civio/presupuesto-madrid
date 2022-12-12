# -*- coding: UTF-8 -*-
import csv
import os
import re

from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
from madrid_utils import MadridUtils

class MadridBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Skip first line
        if line[0] == 'Centro':
            return

        # The format of numbers in data files have changed along the years:
        # Up to 2016 (included) we converted Excel files using in2csv: English format
        # From 2017 we use the original CSVs from the open data portal: Spanish format
        year = re.search(r'municipio/(\d+)/', filename).group(1)
        if int(year) < 2017:
            parse_amount = self._read_english_number
        else:
            parse_amount = self.parse_spanish_amount

        is_expense = (filename.find('gastos.csv') != -1)
        is_actual = (filename.find('/ejecucion_') != -1)
        if is_expense:
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            fc_code = MadridUtils.map_functional_code(line[4].zfill(5), int(year))
            ec_code = line[8]

            # Select the amount column to use based on whether we are importing execution
            # or budget data. In the latter case, sometimes we're dealing with the
            # amended budget, sometimes with the just approved one, in which case
            # there're less columns
            budget_position = 12 if len(line) > 11 else 10
            amount = parse_amount(line[15 if is_actual else budget_position])

            # The original Madrid institutional code requires some mapping
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            ic_code = MadridUtils.map_institutional_code(line[0].zfill(3)+line[2].zfill(3), int(year))

            # We've been asked to ignore data for a special department, not really an organism (#756)
            if ic_code == '200':
                print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                return

            # Ignore transfers to dependent organisations
            if ec_code[:-2] in ['410', '710', '400', '700']:
                print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                return

            # We have to manually modify the 2022 budget data due to some weird amendments. Ouch.
            # This is further explained in civio/presupuesto-management#1157
            if year=='2022':
                if ic_code == '300' and ec_code == '22502': # AGENCIA PARA EL EMPLEO (503)
                    print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                    return
                if ic_code == '800' and ec_code == '22502': # MADRID SALUD (508)
                    print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                    return

            # The input files are encoded in ISO-8859-1, since we want to work with the files
            # as they're published in the original open data portal. All the text fields are
            # ignored, as we use the codes instead, but the description one.
            description = self._spanish_titlecase(line[9].decode("iso-8859-1").encode("utf-8"))

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

        else:
            ec_code = line[4]
            ic_code = MadridUtils.get_institution_code(line[0].zfill(3)) + '00'

            # Select the column from which to read amounts. See similar comment above.
            budget_position = 8 if len(line) > 7 else 6
            amount = parse_amount(line[9 if is_actual else budget_position])

            # We've been asked to ignore data for a special department, not really an organism (#756)
            if ic_code == '200':
                return

            # Ignore transfers from parent organisation.
            if ec_code[:-2] in ['410', '710', '400', '700']:
                print "Eliminando ingreso (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                amount = 0

            # See note above
            description = self._spanish_titlecase(line[5].decode("iso-8859-1").encode("utf-8"))

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

    # We have to manually modify the 2022 budget data due to some weird amendments. Ouch.
    # This is further explained in civio/presupuesto-management#1157
    def load_budget(self, path, entity, year, status, items):
        if year=='2022':
            items.append(self.parse_item("municipio/2022/ingresos.csv", "001;AYUNTAMIENTO DE MADRID;1;IMPUESTOS DIRECTOS;11500;IMPUESTO SOBRE VEHÍCULOS DE TRACCIÓN MECÁNICA;-1000".split(';')))
            items.append(self.parse_item("municipio/2022/ingresos.csv", "001;AYUNTAMIENTO DE MADRID;3;TASAS, PRECIOS PÚBLICOS Y OTROS INGRESOS;33100;ENTRADA DE VEHÍCULOS;-3000".split(';')))

        super(MadridBudgetLoader, self).load_budget(path, entity, year, status, items)

    def parse_spanish_amount(self, amount):
        amount = amount.replace('.', '')    # Remove thousands delimiters, if any
        return self._read_english_number(amount.replace(',', '.'))

    def _get_delimiter(self):
        return ';'
