 """calstatus.py

Dana Simard 06/2020
Module for setting and decoding the status of the real-time calibration pipeline.
"""

INV_ANTNUM = 1 << 0
INV_POL = 1 << 1
INV_GAINAMP_P1 = 1 << 2
INV_GAINAMP_P2 = 1 << 3
INV_GAINPHASE_P1 = 1 << 4
INV_GAINPHASE_P2 = 1 << 5
INV_DELAY_P1 = 1 << 6
INV_DELAY_P2 = 1 << 7
INV_CALSOURCE = 1 << 8
INV_GAINCALTIME = 1 << 9
INV_DELAYCALTIME = 1 << 10
INV_SIM = 1 << 11
INFILE_ERR = 1 << 12
CAL_MISSING_ERR = 1 << 13
INFILE_FORMAT_ERR = 1 << 14
FRINGES_ERR = 1 << 15
MS_WRITE_ERR = 1 << 16
FLAGGING_ERR = 1 << 17
DELAY_CAL_ERR = 1 << 18
GAIN_BP_CAL_ERR = 1 << 19
GAIN_TBL_ERR = 1 << 20
DELAY_TBL_ERR = 1 << 21
CALNAME_ERR = 1 << 22
SIM_ERR = 1 << 23
UNKNOWN_ERR = 1 << 24

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

    Parameters
    ----------
    status : int
        The current value of the status code.
    error: int
        The error code to add to the status.

    Returns
    -------
    int
        The updated status code.
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

    Parameters
    ----------
    status : int
        The current value of the status code.

    Returns
    -------
    list
        The errors corresponding to `status`. If no errors, returns empty list.
    """
    errors = []
    for error, code in error_dict.items():
        if is_error(status, code):
            errors += [error]
    return errors


def is_error(status, error):
    """Determines if a given error is set.

    Parameters
    ----------
    status : int
        The current value of the status code.
    error : int
        The error to check for.

    Returns
    -------
    boolean
        True if the given error is encoded in status.
    """
    return status & error
