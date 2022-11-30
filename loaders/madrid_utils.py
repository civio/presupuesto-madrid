# -*- coding: UTF-8 -*-

class MadridUtils:

    # Get institutional code. We ignore sections in autonomous bodies, since they
    # get assigned to different sections in main body but that's not relevant.
    @staticmethod
    def map_institutional_code(raw_ic_code):
        institution = MadridUtils.get_institution_code(raw_ic_code[0:3])
        return institution + (raw_ic_code[3:6] if institution == '0' else '00')

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    @staticmethod
    def get_institution_code(madrid_code):
        institution_code = madrid_code if madrid_code != '001' else '000'
        return institution_code[2]
