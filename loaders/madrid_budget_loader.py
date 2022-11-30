# -*- coding: UTF-8 -*-
import csv
import os
import re

from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
from madrid_utils import MadridUtils

class MadridBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Programme codes have changed in 2015, due to new laws. Since the application expects a code-programme
        # mapping to be constant over time, we are forced to amend budget data prior to 2015.
        programme_mapping_pre_2015 = {
            # old programme: new programme
            '13304': '13402',   # Planificación de la movilidad
            '13305': '13403',   # Instalaciones de gestión del tráfico
            '13401': '13510',   # SAMUR
            '13501': '13610',   # Bomberos
            '15201': '15210',   # Vivienda
            '15501': '15321',   # Vías públicas
            '15502': '15322',   # Otras actuaciones en vías públicas
            '15504': '15340',   # Infraestructuras públicas
            '16101': '16001',   # Ingeniería del agua
            '16201': '16210',   # Gestión ambiental
            '16202': '16230',   # Valdemingómez
            '17203': '17211',   # Sostenibilidad
            '17201': '17212',   # Control ambiental
            '23000': '23100',   # Gestión de familia
            '23202': '23101',   # Igualdad de oportunidades
            '23301': '23103',   # Mayores
            '24000': '24100',   # Dirección de empleo
            '31000': '31100',   # Dirección Madrid Salud
            '31320': '31101',   # Salubridad pública
            '31321': '31102',   # Adicciones
            '31401': '49300',   # Consumo
            '32101': '32301',   # Centros docentes
            '32401': '32601',   # Servicios de educación
            '33201': '33210',   # Bibliotecas
            '33404': '92402',   # Participación empresarial
            '33403': '33601',   # Patrimonio cultural
            '43110': '43301',   # Promoción económica
            '44101': '44110',   # Promoción del transporte
            '91100': '91230',   # Secretaría del pleno
            '91101': '91240',   # Grupos municipales
            '92701': '92202',   # Medios de comunicación
            '92301': '92310',   # Estadística
        }
        programme_mapping_2011 = {
            '13303': '13302',   # Aparcamientos
            '17102': '16601',   # Mobiliario urbano
            '23103': '23106',   # Servicios sociales
            '23104': '23106',   # Servicios sociales
            '23105': '23107',   # Inmigración
            '23201': '23202',   # Igualdad de oportunidades
            '23101': '23290',   # Cooperación internacional
            '91203': '91204',   # Área de portavoz
            '91204': '91203',   # Área de coordinación territorial
            '91205': '91204',   # Área de portavoz
            '92202': '92208',   # Relaciones con distritos
        }
        programme_mapping_2012 = {
            # old programme: new programme
            '33404': '33403',   # Patrimonio cultural y paisaje urbano
            '91203': '91204',   # Área de portavoz
            '91204': '91203',   # Área de coordinación territorial
            '91205': '91204',   # Área de portavoz
            '92202': '92208',   # Relaciones con distritos
        }
        programme_mapping_2013 = {
            # old programme: new programme
            '33404': '33403',   # Patrimonio cultural y paisaje urbano
            '91203': '91204',   # Área de portavoz
            '91205': '91204',   # Área de portavoz
            '91207': '91205',   # Área de participación ciudadana
        }
        programme_mapping_2015 = {
            # old programme: new programme
            '15341': '15340',   # Infraestructuras urbanas
            '23104': '23200',   # Planes de barrio
            '33404': '92402',   # Participación empresarial
        }
        programme_mapping_pre_2019 = {
            # old programme: new programme
            '49102': '4910A',  # Innovación y tecnología
            '91210': '9121A',  # Área de gobierno de Economía, Empleo y Participación Ciudadana
            '91211': '9121B',  # Área de gobierno de Seguridad
            '91214': '9121C',  # Área de gobierno de Obras y Espacios Públicos
            '91215': '9121D',  # Área delegada de licencias de actividades
            '91217': '9121E',  # Área de Comunicación
            '91219': '9121F',  # Área delegada de Deportes
            '92010': '9201A',  # Oficina de la Presidencia del Pleno
        }

        # The institutional structure of the City of Madrid has changed quite a lot along the
        # years, es In order to show the evolution of a given section we need to keep codes
        # consistent.
        institutional_mapping_2015 = {
            '0085': '0027',     # EQUIDAD, DERECHOS SOCIALES Y EMPLEO
            '0033': '0037',     # COORDINACIÓN TERRITORIAL Y ASOCIACIONES
            '0041': '0047',     # PORTAVOZ, COORD. JUNTA GOB. Y RELAC. CON EL PLENO
            '0025': '0057',     # ECONOMÍA Y HACIENDA
            '0032': '0067',     # SALUD, SEGURIDAD Y EMERGENCIAS
            '0071': '0077',     # PARTICIPACIÓN CIUDADANA, TRANSP. Y GOB. ABIERTO
            '0035': '0087',     # DESARROLLO URBANO SOSTENIBLE
            '0015': '0097',     # MEDIO AMBIENTE Y MOVILIDAD
            '0065': '0098',     # CULTURA Y DEPORTES
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

        # Skip first line
        if line[0] == 'Centro':
            return

        # The format of numbers in data files have changed along the years:
        # Up to 2016 (included) we converted Excel files using in2csv: English format
        # From 2017 we use the original CSVs from the open data portal: Spanish format
        year = re.search(r'municipio/(\d+)/', filename).group(1)
        if int(year) < 2017:
            parse_amount = self._read_english_number
        else:
            parse_amount = self.parse_spanish_amount

        is_expense = (filename.find('gastos.csv') != -1)
        is_actual = (filename.find('/ejecucion_') != -1)
        if is_expense:
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            fc_code = line[4].zfill(5)
            ec_code = line[8]

            # Select the amount column to use based on whether we are importing execution
            # or budget data. In the latter case, sometimes we're dealing with the
            # amended budget, sometimes with the just approved one, in which case
            # there're less columns
            budget_position = 12 if len(line) > 11 else 10
            amount = parse_amount(line[15 if is_actual else budget_position])

            # The original Madrid institutional code requires some mapping
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            ic_code = MadridUtils.map_institutional_code(line[0].zfill(3)+line[2].zfill(3))

            # We've been asked to ignore data for a special department, not really an organism (#756)
            if ic_code == '200':
                print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                return

            # Ignore transfers to dependent organisations
            if ec_code[:-2] in ['410', '710', '400', '700']:
                print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                return

            # We have to manually modify the 2022 budget data due to some weird amendments. Ouch.
            # This is further explained in civio/presupuesto-management#1157
            if year=='2022':
                if ic_code == '300' and ec_code == '22502': # AGENCIA PARA EL EMPLEO (503)
                    print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                    return
                if ic_code == '800' and ec_code == '22502': # MADRID SALUD (508)
                    print "Eliminando gasto (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                    return

            # Apply institutional mapping to make codes consistent across years
            if int(year) <= 2015:
                ic_code = institutional_mapping_2015.get(ic_code, ic_code)

            if int(year) < 2019:
                ic_code = institutional_mapping_pre_2019.get(ic_code, ic_code)

            if int(year) < 2020:
                ic_code = institutional_mapping_pre_2020.get(ic_code, ic_code)

            # Some years require some amendments
            if year == '2011':
                fc_code = programme_mapping_2011.get(fc_code, fc_code)
            if year == '2012':
                fc_code = programme_mapping_2012.get(fc_code, fc_code)
            if year == '2013':
                fc_code = programme_mapping_2013.get(fc_code, fc_code)
            if year == '2015':
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

            # For years before 2015 we check whether we need to amend the programme code
            if int(year) < 2015:
                fc_code = programme_mapping_pre_2015.get(fc_code, fc_code)

            # For years before 2019 we check whether we need to amend the programme code
            if int(year) < 2019:
                fc_code = programme_mapping_pre_2019.get(fc_code, fc_code)

            # The input files are encoded in ISO-8859-1, since we want to work with the files
            # as they're published in the original open data portal. All the text fields are
            # ignored, as we use the codes instead, but the description one.
            description = self._spanish_titlecase(line[9].decode("iso-8859-1").encode("utf-8"))

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

        else:
            ec_code = line[4]
            ic_code = MadridUtils.get_institution_code(line[0].zfill(3)) + '00'

            # Select the column from which to read amounts. See similar comment above.
            budget_position = 8 if len(line) > 7 else 6
            amount = parse_amount(line[9 if is_actual else budget_position])

            # We've been asked to ignore data for a special department, not really an organism (#756)
            if ic_code == '200':
                return

            # Ignore transfers from parent organisation.
            if ec_code[:-2] in ['410', '710', '400', '700']:
                print "Eliminando ingreso (organismo %s, artículo %s): %12.2f €" % (line[0], ec_code, amount/100)
                amount = 0

            # See note above
            description = self._spanish_titlecase(line[5].decode("iso-8859-1").encode("utf-8"))

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

    # We have to manually modify the 2022 budget data due to some weird amendments. Ouch.
    # This is further explained in civio/presupuesto-management#1157
    def load_budget(self, path, entity, year, status, items):
        if year=='2022':
            items.append(self.parse_item("municipio/2022/ingresos.csv", "001;AYUNTAMIENTO DE MADRID;1;IMPUESTOS DIRECTOS;11500;IMPUESTO SOBRE VEHÍCULOS DE TRACCIÓN MECÁNICA;-1000".split(';')))
            items.append(self.parse_item("municipio/2022/ingresos.csv", "001;AYUNTAMIENTO DE MADRID;3;TASAS, PRECIOS PÚBLICOS Y OTROS INGRESOS;33100;ENTRADA DE VEHÍCULOS;-3000".split(';')))

        super(MadridBudgetLoader, self).load_budget(path, entity, year, status, items)

    def parse_spanish_amount(self, amount):
        amount = amount.replace('.', '')    # Remove thousands delimiters, if any
        return self._read_english_number(amount.replace(',', '.'))

    def _get_delimiter(self):
        return ';'
