# -*- coding: UTF-8 -*-

class MadridUtils:

    @staticmethod
    def map_institutional_code(raw_ic_code, year):
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

        # Get institutional code. We ignore sections in autonomous bodies, since they
        # get assigned to different sections in main body but that's not relevant.
        institution = MadridUtils.get_institution_code(raw_ic_code[0:3])
        ic_code = institution + (raw_ic_code[3:6] if institution == '0' else '00')

        # Apply institutional mapping to make codes consistent across years
        if year <= 2015:
            ic_code = institutional_mapping_2015.get(ic_code, ic_code)

        if year < 2019:
            ic_code = institutional_mapping_pre_2019.get(ic_code, ic_code)

        if year < 2020:
            ic_code = institutional_mapping_pre_2020.get(ic_code, ic_code)

        return ic_code


    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    @staticmethod
    def get_institution_code(madrid_code):
        institution_code = madrid_code if madrid_code != '001' else '000'
        return institution_code[2]
