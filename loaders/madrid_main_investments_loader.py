# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import MainInvestmentsLoader
import csv
import re

class MadridMainInvestmentsLoader(MainInvestmentsLoader):
    def read_nullable_integer(self, s):
        return None if s==None or s=='' else int(s)

    # XXX: Image handling is still to be decided. We'll hardcode it for now
    def get_image_URL(self, project_id):
        IMAGES = {
          '14': 'https://civio.box.com/shared/static/ogll2bad0qazoapnnafgql33cs76fza0.jpg',
          '21': 'https://civio.box.com/shared/static/jsem2ks9lqgw3kovz6dtynj1q006sj23.jpg',
          '2019/000217': 'https://civio.box.com/shared/static/o606zx1wgkytvt9g6n7zve0n7c0pjw6n.jpg',
          '2016/000341': 'https://civio.box.com/shared/static/7jcyjgcrs9sb0qcy1enbotwzgivgnafc.jpg',
          '2017/000242': 'https://civio.box.com/shared/static/ywso24dp6u5mq8mgsspq3i0s2c5i0yh2.jpg',
          '2016/000833': 'https://civio.box.com/shared/static/nloyl1rye6du1qhipxqroqo2c3c3ub5s.jpg',
          '2018/001065': 'https://civio.box.com/shared/static/zzhbj0flrj33wd1qxaqnmkhqxilr3jq5.jpg',
          '2020/000717': 'https://civio.box.com/shared/static/lrp212dp8mmy0g8cav8olxt632c3rjaf.jpg',
          '2019/004342': 'https://civio.box.com/shared/static/mel5uql3z3tjosnqmz0iz69ytbnjh3f9.jpg',
          '2019/003814': 'https://civio.box.com/shared/static/wswz5gwcgcmvhwzi02dbhg4aj2rlad3f.jpg',
          '2009/000430': 'https://civio.box.com/shared/static/t6omi9wrh9b9ylo3uyhodbuqnyyscr48.jpg',
          '2019/003889': 'https://civio.box.com/shared/static/59pl0bfswsin0d8ucoy4qe6g2bmb6a6j.jpg',
          '2016/000533': 'https://civio.box.com/shared/static/4ol8oo50u9op5dqt07jw2is5dfhf427l.jpg',
          '2015/000207': 'https://civio.box.com/shared/static/eye5da8s7yqc8kg0mp7as5cq2dmataa2.jpg',
          '2017/000195': 'https://civio.box.com/shared/static/l41f97qbson47lp1y3kqyrm6fiuvt7tn.jpg',
          '2019/000730': 'https://civio.box.com/shared/static/fywwn14vvh9gynnpldbld856p8zc8qcc.jpg'
        }
        return IMAGES.get(project_id, '')


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
        investment_line = line[19]
        gc_code = self.map_geo_code(line[9])

        # Note we implement the investment lines as an extension of functional policies.
        # See #527 for further information.
        return {
            'project_id': project_id,
            'description': line[5].strip(),
            'image_URL': self.get_image_URL(project_id),
            'status': line[28].strip(),
            'entity_name': line[1].strip(),
            'section_name': line[3].strip(),
            'area_name': line[10].strip(),
            'address': line[11].strip().replace('\n', ' '),     # New lines mess up the JSON in the template
            'latitude': line[17].strip().replace('\'', ''),     # Got an odd extra quote in dirty data at least once
            'longitude': line[18].strip().replace('\'', ''),    # Just in case
            'start_year': self.read_nullable_integer(line[6]),
            'expected_end_year': self.read_nullable_integer(line[7].strip()),
            'actual_end_year': self.read_nullable_integer(line[8].strip()),
            'total_expected_amount': self._read_spanish_number(line[27].strip()),
            'already_spent_amount': self._read_spanish_number(line[21].strip()),
            'current_year_amount': self._read_spanish_number(line[22].strip()),
            'gc_code': gc_code,
            'fc_code': 'X'+investment_line.zfill(2),
            'fc_area': 'X',
            'fc_policy': 'X'+investment_line.zfill(2),
        }

    def _get_delimiter(self):
        return ';'
