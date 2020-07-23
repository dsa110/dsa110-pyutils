"""dsa_calstatus.py

Dana simard 06/2020
Module for setting and decoding the status of the real-time calibration pipeline.
"""


# error_keys = ['inv_antnum', 'inv_time', 'inv_pol', 'inv_gainamp_p1',
#               'inv_gainamp_p2', 'inv_gainphase_p1', 'inv_gainphase_p2',
#               'inv_delay_p1', 'inv_delay_p2', 'inv_calsource',
#               'inv_gaincaltime', 'inv_delaycaltime', 'inv_sim', 'infile_err',
#               'cal_missing_err', 'infile_format_err', 'fringes_err',
#               'ms_write_err', 'flagging_err', 'delay_cal_err',
#               'gain_bp_cal_err', 'gain_tbl_err', 'delay_tbl_err',
#               'calname_err','sim_err','unknown_err']
# error_codes = dict({})
# for i,k in enumerate(error_keys):
#     error_codes[k] = 2**i

INV_ANTNUM = 2**0
INV_POL = 2**1
INV_GAINAMP_P1 = 2**2
INV_GAINAMP_P2 = 2**3
INV_GAINPHASE_P1 = 2**4
INV_GAINPHASE_P2 = 2**5
INV_DELAY_P1 = 2**6
INV_DELAY_P2 = 2**7
INV_CALSOURCE = 2**8
INV_GAINCALTIME = 2**9
INV_DELAYCALTIME = 2**10
INV_SIM = 2**11
INFILE_ERR = 2**12
CAL_MISSING_ERR = 2**13
INFILE_FORMAT_ERR = 2**14
FRINGES_ERR = 2**15
MS_WRITE_ERR = 2**16
FLAGGING_ERR = 2**17
DELAY_CAL_ERR = 2**18
GAIN_BP_CAL_ERR = 2**19
GAIN_TBL_ERR = 2**20
DELAY_TBL_ERR = 2**21
CALNAME_ERR = 2**22
SIM_ERR = 2**23
UNKNOWN_ERR = 2**24

error_dict = {'inv_antnum': INV_ANTNUM,
              'inv_pol': INV_POL,
              'inv_gainamp_p1': INV_GAINAMP_P1,
              'inv_gainamp_p2': INV_GAINAMP_P2,
              'inv_gainphase_p1': INV_GAINPHASE_P1,
              'inv_gainphase_p2': INV_GAINPHASE_P2,
              'inv_delay_p1': INV_DELAY_P1,
              'inv_delay_p2': INV_DELAY_P2,
              'inv_calsource': INV_CALSOURCE,
              'inv_gaincaltime': INV_GAINCALTIME,
              'inv_delaycaltime': INV_DELAYCALTIME,
              'inv_sim': INV_SIM,
              'infile_err': INFILE_ERR,
              'cal_missing_err': CAL_MISSING_ERR,
              'infile_format_err': INFILE_FORMAT_ERR,
              'fringes_err': FRINGES_ERR,
              'ms_write_err': MS_WRITE_ERR,
              'flagging_err': FLAGGING_ERR,
              'delay_cal_err': DELAY_CAL_ERR,
              'gain_bp_cal_err': GAIN_BP_CAL_ERR,
              'gain_tbl_err': GAIN_TBL_ERR,
              'delay_tbl_err': DELAY_TBL_ERR,
              'calname_err': CALNAME_ERR,
              'sim_err': SIM_ERR,
              'unknown_err': UNKNOWN_ERR,
              }

def update(status, error):
    """Updates the status code to include a given error.

    Args:
      status: int
        the current value of the status code
      error: int
        the error code to add to the status

    Returns:
      int
        the updated status codee
    """
    if isinstance(error, int):
        status = status | error
        return status

    if isinstance(error, str):
        error = [error]
    if isinstance(error, list):
        for err in error:
            if err in error_dict.keys():
                status = status | error_dict[err]
            else:
                status = status | error_dict['unknown_err']
    return status

def decode(status):
    """Decodes the calibration status.

    Args:
      status : int
        the current value of the status code

    Returns:
      list(str)
        The errors corresponding to the current key
        If no errors, returns an empty list
    """
    errors = []
    for error, code in error_dict.items():
        if is_error(status, code):
            errors += [error]
    return errors

def is_error(status, error):
    """Determines if a given error is set.

    Args:
      status: int
        the current value of the status code
      error: int
        the error to check for

    Returns:
      boolean
        True if the given error is encoded in status
    """
    return status & error
