# -*- coding: UTF-8 -*-
import re

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget
from madrid_utils import MadridUtils

class MadridPaymentsLoader(PaymentsLoader):
    # Parse an input line into fields
    def parse_item(self, budget, line):
        # What we want as area is the programme description
        # Note: in the most recent 2018 data leading zeros were missing in some rows,
        # so add them back using zfill.
        fc_code = line[1].zfill(5)
        policy_id = fc_code[:2]
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        # Some descriptions are missing in early years. Per #685, we use the heading text then.
        description = line[3].strip()
        if description == "":
            heading_id = line[2][0:3]
            description = Budget.objects.get_all_descriptions(budget.entity)['expense'][heading_id]

        # Get the payee name and clean it up a bit, as some non-ASCII characters are messed up.
        payee = line[5].strip()
        payee = payee.replace('Ð', 'Ñ').replace('Ë', 'Ó').replace('\'-', 'Á')
        # And some payee names have bizarre punctuation marks:
        payee = re.sub(r'( \.)+$', '', payee)  # trailing 1-2 instances of " ."
        payee = re.sub(r'^[\. ]+', '', payee)  # leading dot or spaces

        # Madrid wants to include the fiscal id trailing the payee name.
        fiscal_id = line[4]
        payee = payee + ' (' + fiscal_id + ')'

        # The original Madrid institutional code requires some mapping.
        # Note: in the most recent 2018 data leading zeros were missing in some rows,
        # so add them back using zfill.
        ic_code = MadridUtils.map_institutional_code(line[0].zfill(6), budget.year)

        return {
            'area': policy,
            'fc_code': None,
            'ec_code': None,
            'ic_code': ic_code,
            'date': None,
            'payee': payee,
            'payee_fiscal_id': fiscal_id[:15],
            'description': description + ' (' + str(budget.year) + ')',
            'amount': self._read_english_number(line[6]),
        }

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    def get_institution_code(self, madrid_code):
        institution_code = madrid_code if madrid_code != '001' else '000'
        return institution_code[2]
