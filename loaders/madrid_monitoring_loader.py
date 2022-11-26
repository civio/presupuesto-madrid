# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import MonitoringLoader
import csv
import re

class MadridMonitoringLoader(MonitoringLoader):

    def parse_goal(self, filename, line):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='Entidad CP':
            return

        # Get institutional code, which requires some manipulation. We ignore sections in autonomous bodies.
        institution_code = '0' if line[4][0:3] != '001' else line[4][2]
        department_code = line[4][3:6] if institution_code == '0' else '00'

        return {
            'ic_code': institution_code + department_code,
            'fc_code': line[5],
            'goal_number': line[6],
            'description': line[7]
        }
