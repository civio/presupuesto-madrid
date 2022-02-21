# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import MainInvestmentsLoader
import csv
import re

class MadridMainInvestmentsLoader(MainInvestmentsLoader):
    def read_nullable_integer(self, s):
        return None if s==None or s=='' else int(s)

    # Make sure special district codes (many districts, and no districts) match
    # the special values the application expects.
    def map_geo_code(self, s):
        if (s=='998'):
            return 'NN'
        if (s=='999'):
            return 'NA'
        if (len(s)>3):  # Unexpected stuff
            return None
        return s

    def parse_item(self, filename, line):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='Centro':
            return

        investment_line = line[19]
        gc_code = self.map_geo_code(line[9])

        # Note we implement the investment lines as an extension of functional policies.
        # See #527 for further information.
        return {
            'project_id': line[4].strip(),
            'description': line[5].strip(),
            'status': line[28].strip(),
            'entity_name': line[1].strip(),
            'section_name': line[3].strip(),
            'area_name': line[10].strip(),
            'address': line[11].strip(),
            'latitude': line[17].strip(),
            'longitude': line[18].strip(),
            'start_year': self.read_nullable_integer(line[6]),
            'expected_end_year': self.read_nullable_integer(line[7].strip()),
            'actual_end_year': self.read_nullable_integer(line[8].strip()),
            'total_expected_amount': self._read_english_number(line[27].strip()),
            'already_spent_amount': self._read_english_number(line[21].strip()),
            'current_year_amount': self._read_english_number(line[22].strip()),
            'gc_code': gc_code,
            'fc_code': 'X'+investment_line.zfill(2),
            'fc_area': 'X',
            'fc_policy': 'X'+investment_line.zfill(2),
        }
