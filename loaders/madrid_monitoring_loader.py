# -*- coding: UTF-8 -*-
import csv
import re

from budget_app.models import *
from budget_app.loaders import MonitoringLoader
from madrid_utils import MadridUtils

class MadridMonitoringLoader(MonitoringLoader):

    def parse_goal(self, filename, line):
        # Skip empty/header/subtotal lines.
        # Note: we use second field to check for header to avoid BOM issues.
        if line[0]=='' or line[1]=='Ejercicio':
            return

        # Get key fields.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[4])
        fc_code = line[5]
        goal_number = line[6]

        return {
            'uid': self._get_goal_uid(ic_code, fc_code, goal_number),
            'ic_code': ic_code,
            'fc_code': fc_code,
            'goal_number': goal_number,
            'description': line[14].decode("utf8"),
            'report': line[15].replace("  ", "<br/><br/>")  # FIXME: Temporary solution
        }


    def parse_activity(self, filename, line):
        # Skip empty/header/subtotal lines.
        # Note: we use second field to check for header to avoid BOM issues.
        if line[0]=='' or line[1]=='Ejercicio':
            return

        # Get key fields to identify the parent goal.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[4])
        fc_code = line[9]
        goal_number = line[11]

        return {
            'goal_uid': self._get_goal_uid(ic_code, fc_code, goal_number),
            'activity_number': line[14],
            'description': line[15].decode("utf8"),
        }


    def parse_indicator(self, filename, line):
        # Skip empty/header/subtotal lines.
        # Note: we use second field to check for header to avoid BOM issues.
        if line[0]=='' or line[1]=='Ejercicio':
            return

        # Get key fields to identify the parent goal.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[4])
        fc_code = line[5]
        goal_number = line[6]

        # Calculate the indicator score, from 0 to 1
        target = int(line[12])
        actual = int(line[13])
        # Note: If goal is 0 then set score to 1 to avoid division by zero. It's very rare in any case.
        score = 1 if target==0 else min(float(actual)/float(target), 1.0)

        return {
            'goal_uid': self._get_goal_uid(ic_code, fc_code, goal_number),
            'indicator_number': line[8],
            'description': line[10].decode("utf8"),
            'unit': line[11],
            'target': target,
            'actual': actual,
            'score': score
        }


    def _get_goal_uid(self, ic_code, fc_code, goal_number):
        return "%s/%s/%s" % (ic_code, fc_code, goal_number)

    def _get_delimiter(self):
        return ';'
