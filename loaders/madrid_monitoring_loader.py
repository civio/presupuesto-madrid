# -*- coding: UTF-8 -*-
import csv
import re

from budget_app.models import *
from budget_app.loaders import MonitoringLoader
from madrid_utils import MadridUtils

class MadridMonitoringLoader(MonitoringLoader):

    def parse_goal(self, filename, line, year):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='CeGe':
            return

        # Get key fields.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[0], int(year))
        fc_code = MadridUtils.map_functional_code(line[1], int(year))
        goal_number = line[2]

        return {
            'uid': self._get_goal_uid(year, ic_code, fc_code, goal_number),
            'ic_code': ic_code,
            'fc_code': fc_code,
            'goal_number': goal_number,
            'description': line[3].decode("utf8"),
            'report': line[4]
        }


    def parse_activity(self, filename, line, year):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='CeGe':
            return

        # Get key fields to identify the parent goal.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[0], int(year))
        fc_code = MadridUtils.map_functional_code(line[1], int(year))
        goal_number = line[2]

        return {
            'goal_uid': self._get_goal_uid(year, ic_code, fc_code, goal_number),
            'activity_number': line[3],
            'description': line[4].decode("utf8"),
        }


    def parse_indicator(self, filename, line, year):
        # Skip empty/header/subtotal lines.
        if line[0]=='' or line[0]=='CeGe' or line[3]=='':
            return

        # Get key fields to identify the parent goal.
        # The original Madrid institutional code requires some mapping.
        ic_code = MadridUtils.map_institutional_code(line[0], int(year))
        fc_code = MadridUtils.map_functional_code(line[1], int(year))
        goal_number = line[2]

        # Some other basic fields
        description = line[4].decode("utf8")
        unit = line[5]
        target = int(line[6])
        actual = int(line[7])
        _is_inverse_indicator = self._is_inverse_indicator(description, unit)

        # Calculate the indicator score, from 0 to 1
        # Note: If goal is 0 then set score to 0, there's nothing to calculate, and
        # it wouldn't be fair to give a score, it would be "free" (or "impossible" for
        # the reverse ones). It's very rare anyway.
        if _is_inverse_indicator:
            # You get 0 points for doubling the target, and better from that.
            # Note that you could be worse than that (while "normal" indicators don't
            # go below zero), so we need to cap both the minimum and the maximum.
            score = 0 if target==0 else max(min(float(2*target-actual)/float(target), 1.0), 0.0)
        else:
            # Note: we assume negative values do not exist, simpler this way.
            score = 0 if target==0 else min(float(actual)/float(target), 1.0)

        return {
            'goal_uid': self._get_goal_uid(year, ic_code, fc_code, goal_number),
            'indicator_number': line[3],
            'description': description,
            'unit': unit,
            'target': target,
            'actual': actual,
            'score': score
        }


    # Some indicators (like average waiting time for a public service) are "reversed",
    # i.e. they're better the lower the value is. The source data doesn't identify these
    # indicators, so we do our best to guess.
    # XXX: This is definitely not the final version.
    def _is_inverse_indicator(self, description, unit):
        if unit in ['SEGUNDOS', 'MINUTOS', 'DÍAS']:
            return True
        return False

    def _get_goal_uid(self, year, ic_code, fc_code, goal_number):
        return "%s-%s-%s-%s" % (year, ic_code, fc_code, goal_number)

    def _get_delimiter(self):
        return ';'
