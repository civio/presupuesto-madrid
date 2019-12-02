# -*- coding: UTF-8 -*-

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

import re


class MadridPaymentsLoader(PaymentsLoader):
    # Parse an input line into fields
    def parse_item(self, budget, line):
        # The institutional structure of the City of Madrid has changed quite a lot along the
        # years, es In order to show the evolution of a given section we need to keep codes
        # consistent.
        institutional_mapping_2015 = {
            '0085': '0027',  # EQUIDAD, DERECHOS SOCIALES Y EMPLEO
            '0033': '0037',  # COORDINACIÓN TERRITORIAL Y ASOCIACIONES
            '0041': '0047',  # PORTAVOZ, COORD. JUNTA GOB. Y RELAC. CON EL PLENO
            '0025': '0057',  # ECONOMÍA Y HACIENDA
            '0032': '0067',  # SALUD, SEGURIDAD Y EMERGENCIAS
            '0071': '0077',  # PARTICIPACIÓN CIUDADANA, TRANSP. Y GOB. ABIERTO
            '0035': '0087',  # DESARROLLO URBANO SOSTENIBLE
            '0015': '0097',  # MEDIO AMBIENTE Y MOVILIDAD
            '0065': '0098',  # CULTURA Y DEPORTES
        }

        institutional_mapping_pre_2019 = {
            '0011': '0020',     # Vicealcaldía
            '0075': '007A',     # Área de Economía, Empleo y Participación Ciudadana
        }

        institutional_mapping_pre_2020 = {
            '0002': '0100',     # Presidencia del Pleno
            '0003': '0103',     # Oficina Municipal contra el Fraude y la Corrupción
            '0010': '0101',     # Alcaldía
            '0012': '0102',     # Coordinación General de la Alcaldía
            '0020': '0110',     # Vicealcaldía
            '0021': '0111',     # Área delegada de Coordinación Territorial, Transparencia y Participación Ciudadana
            '0023': '0112',     # Área delegada de Internacionalización y Cooperación
            '0027': '0180',     # Familias, Igualdad y Bienestar Social
            '0031': '0161',     # Área Delegada de Vivienda
            '0055': '0190',     # Obras y Equipamientos
            '0057': '0170',     # Hacienda y Personal
            '0060': '0140',     # Economía, Innovación y Empleo
            '0065': '0131',     # Área Delegada de Deporte
            '0066': '0132',     # Área Delegada de Turismo
            '0067': '0120',     # Portavoz, Seguridad y Emergencias
            '0075': '0141',     # Área Delegada de Emprendimiento, Empleo e Innovación
            '0087': '0160',     # Desarrollo Urbano
            '0097': '0150',     # Medio Ambiente y Movilidad
            '0098': '0130',     # Cultura, Turismo y Deporte
            '0100': '0300',     # Endeudamiento
            '0110': '0310',     # Créditos Globales y Fondo de Contingencia
            '0120': '0320',     # Tribunal Económico-Administrativo
            '0130': '013A',     # Defensor del Contribuyente
        }

        # But what we want as area is the programme description
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

        # Get institutional code. See the budget_loader for more details on this process for Madrid.
        # Note: in the most recent 2018 data leading zeros were missing in some rows,
        # so add them back using zfill.
        raw_ic_code = line[0].zfill(6)
        institution = self.get_institution_code(raw_ic_code[0:3])
        ic_code = institution + (raw_ic_code[3:6] if institution == '0' else '00')

        # Apply institutional mapping to make codes consistent across years
        if budget.year <= 2015:
            ic_code = institutional_mapping_2015.get(ic_code, ic_code)

        if budget.year < 2019:
            ic_code = institutional_mapping_pre_2019.get(ic_code, ic_code)

        if budget.year < 2020:
            ic_code = institutional_mapping_pre_2020.get(ic_code, ic_code)

        return {
            'area': policy,
            'fc_code': None,
            'ec_code': None,
            'ic_code': ic_code,
            'date': None,
            'payee': payee,
            'payee_fiscal_id': fiscal_id,
            'description': description + ' (' + str(budget.year) + ')',
            'amount': self._read_english_number(line[6]),
        }

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    def get_institution_code(self, madrid_code):
        institution_code = madrid_code if madrid_code != '001' else '000'
        return institution_code[2]
