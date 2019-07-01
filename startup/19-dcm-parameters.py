#run_report(__file__)

class dcm_parameters():
    '''A simple class for maintaining calibration parameters for the
    Si(111) and Si(311) monochromators.

    BMM_dcm.dspacing_111:   d-spacing for the Si(111) mono
    BMM_offset_111:         angular offset for the Si(111) mono

    BMM_dcm.dspacing_311:   d-spacing for the Si(311) mono
    BMM_offset_311:         angular offset for the Si(311) mono

    '''
    def __init__(self):
        self.dspacing_111 = 3.1353241  # 13 June 2019
        self.dspacing_311 = 1.6376015  # 13 June 2019
        ## *add* the fit result from these numbers!
        self.offset_111 = 16.0576931 
        self.offset_311 = 15.9913698
BMM_dcm = dcm_parameters()

