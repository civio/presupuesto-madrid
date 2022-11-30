# -*- coding: UTF-8 -*-
import csv
import re

from budget_app.models import *
from budget_app.loaders import MonitoringLoader
from madrid_utils import MadridUtils

class MadridMonitoringLoader(MonitoringLoader):

    def parse_goal(self, filename, line):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='Entidad CP':
            return

        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[4])

        return {
            'ic_code': ic_code,
            'fc_code': line[5],
            'goal_number': line[6],
            'description': line[7]
        }
