# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import MainInvestmentsLoader
import csv
import re

class MadridMainInvestmentsLoader(MainInvestmentsLoader):
    def read_nullable_integer(self, s):
        return None if s==None or s=='' else int(s)

    def get_image_URL(self, raw_url):
        if raw_url=='':
            return ''
        else:
            return 'https://images.weserv.nl/?url='+raw_url;

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
        # Sometimes there's a hidden U+FEFF at the beginning of the file, so don't test for exact match.
        if line[0]=='' or 'Centro' in line[0]:
            return

        project_id = line[4].strip()
        investment_line = line[17]
        gc_code = self.map_geo_code(line[9])

        # Note we implement the investment lines as an extension of functional policies.
        # See #527 for further information.
        return {
            'project_id': project_id,
            'description': line[5].strip(),
            'image_URL': self.get_image_URL(line[28]),
            'status': line[26].strip(),
            'entity_name': line[1].strip(),
            'section_name': line[3].strip() if line[3]!='' else line[1],
            'area_name': line[10].strip(),
            'address': line[11].strip().replace('\r', ' ').replace('\n', ' '),     # New lines mess up the JSON in the template
            'latitude': line[15].strip().replace('\'', ''),     # Got an odd extra quote in dirty data at least once
            'longitude': line[16].strip().replace('\'', ''),    # Just in case
            'start_year': self.read_nullable_integer(line[6]),
            'expected_end_year': self.read_nullable_integer(line[7].strip()),
            'actual_end_year': self.read_nullable_integer(line[8].strip()),
            'total_expected_amount': self._read_spanish_number(line[25].strip()),
            'already_spent_amount': self._read_spanish_number(line[19].strip()),
            'current_year_amount': self._read_spanish_number(line[20].strip()),
            'gc_code': gc_code,
            'fc_code': 'X'+investment_line.zfill(2),
            'fc_area': 'X',
            'fc_policy': 'X'+investment_line.zfill(2),
        }

    def _get_delimiter(self):
        return ';'
