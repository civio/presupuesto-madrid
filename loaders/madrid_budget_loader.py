# -*- coding: UTF-8 -*-
import re
import six

from budget_app.loaders import SimpleBudgetLoader

if six.PY2:
    from madrid_utils import MadridUtils
else:
    from .madrid_utils import MadridUtils

class MadridBudgetLoader(SimpleBudgetLoader):

    # Add elimination files to the loading process. See #1348.
    # We need them in Madrid because the eliminatins have stopped following
    # a consistente pattern.
    def _get_input_filenames(self):
        return [
            'ingresos.csv',
            'ingresos_eliminaciones.csv',
            'gastos.csv',
            'gastos_eliminaciones.csv',
            'ejecucion_ingresos.csv',
            'ejecucion_ingresos_eliminaciones.csv',
            'ejecucion_gastos.csv',
            'ejecucion_gastos_eliminaciones.csv',
        ]

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

        is_expense = (filename.find('gastos') != -1)
        is_actual = (filename.find('/ejecucion_') != -1)
        is_elimination = (filename.find('eliminaciones') != -1)
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

            # Eliminations before 2023 followed a consistent pattern
            if int(year) < 2023:
                # We've been asked to ignore data for a special department, not really an organism (#756)
                if ic_code == '200':
                    print("Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100))
                    return

                # Ignore transfers to dependent organisations
                if ec_code[:-2] in ['410', '710', '400', '700']:
                    print("Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100))
                    return

            # From 2023, eliminations come in separate files, but amounts need to be reversed.
            if is_elimination:
                amount = -amount

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

            # Eliminations before 2023 followed a consistent pattern
            if int(year) < 2023:
                # We've been asked to ignore data for a special department, not really an organism (#756)
                if ic_code == '200':
                    return

                # Ignore transfers from parent organisation.
                if ec_code[:-2] in ['410', '710', '400', '700']:
                    print("Eliminando ingreso (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100))
                    amount = 0

            # From 2023, eliminations come in separate files, but amounts need to be reversed.
            if is_elimination:
                amount = -amount

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

    def parse_spanish_amount(self, amount):
        amount = amount.replace('.', '')    # Remove thousands delimiters, if any
        return self._read_english_number(amount.replace(',', '.'))

    def _get_delimiter(self):
        return ';'
