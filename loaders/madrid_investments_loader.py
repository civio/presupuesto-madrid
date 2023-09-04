# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import InvestmentsLoader
import csv
import re

class MadridInvestmentsLoader(InvestmentsLoader):

    # An artifact of the in2csv conversion of the original XLS files is a trailing '.0',
    # which we remove here
    def clean(self, s):
        return s.split('.')[0]

    # Make sure special district codes (many districts, and no districts) match
    # the special values the application expects.
    def map_geo_code(self, s):
        if (s=='998'):
            return 'NN'
        if (s=='999'):
            return 'NA'
        return s

    def parse_item(self, filename, line):
        # Skip empty/header/subtotal lines.
        # Careful with 2017 data, first two columns are usually empty
        if unicode(line[0], encoding='iso-8859-1').encode('utf8') in ['*', 'Fondo', 'Fondos', 'Programa de financiación']:
            return
        if line[0]=='' and line[2]=='':
            return

        # Extract metadata from filename
        year = re.search('municipio/(\d+)/', filename).group(1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # 2014 data is in a different format to previous years
        if int(year) < 2014:
            project_id = line[3]
            description = line[4]
            investment_line = self.clean(line[1])
            gc_code = self.map_geo_code(self.clean(line[0]).strip())
            amount = self._read_english_number(line[5])
        else:
            # Investment data comes in two very different formats: when the budget is
            # approved and when provided as part of an execution update.
            if len(line) > 13:
                project_id = line[7]
                description = unicode(line[8], encoding='iso-8859-1').encode('utf8')
                investment_line = line[11]
                gc_code = self.map_geo_code(line[9])
                amount = self._read_spanish_number(line[28 if is_actual else 23])

            else:
                project_id = line[0]
                description = unicode(line[1], encoding='iso-8859-1').encode('utf8')
                investment_line = line[7]
                gc_code = self.map_geo_code(line[11])
                amount = self._read_spanish_number(line[6])

        # Note we implement the investment lines as an extension of functional policies.
        # See #527 for further information.
        return {
            'is_actual': is_actual,
            'gc_code': gc_code,
            'fc_code': 'X'+investment_line.zfill(2),
            'fc_area': 'X',
            'fc_policy': 'X'+investment_line.zfill(2),
            'amount': amount,
            'project_id': project_id.strip(),
            'description': description.strip()
        }

    # Override default input delimiter
    def _get_delimiter(self):
        return ';'
