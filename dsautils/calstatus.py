"""dsa_calstatus.py 

Dana simard 06/2020
Module for setting and decoding the status of the real-time calibration pipeline.
"""

#def __init__():
error_keys = ['inv_antnum','inv_time','inv_pol','inv_gainamp_p1','inv_gainamp_p2',
                            'inv_gainphase_p1','inv_gainphase_p2','inv_delay_p1','inv_delay_p2',
                            'inv_calsource','inv_gaincaltime','inv_delaycaltime','inv_sim',
                            'infile_err','cal_missing_err','infile_format_err','fringes_err',
                            'ms_write_err','flagging_err','delay_cal_err','gain_bp_cal_err',
                            'gain_tbl_err','delay_tbl_err','calname_err','sim_err','other_err']
error_codes = dict({})
for i,k in enumerate(error_keys):
    error_codes[k] = 2**i
        

def update(status,error):
    """Update the status code to include a given error
    
    Args:
      status: int 
        the current value of the status code
      error: str (one of the values in error_keys) of list(str)
        the error(s) to add to the status

    Returns:
      status: int
        the updated status codee
    """
    if type(error) is str:
        status = status | error_codes[error]
    else:
        for e in error:
            status = status | error_codes[e]
    return status
    

def decode(status,key=None):
    """Decode the calibration status.
    
    Args:
      status : int
        the current value of the status code 
    
    Returns:
      errors: list(str)
        The errors corresponding to the current key
        If no errors, returns an empty list
    """
    errors = []
    for k in error_keys:
        if status & error_codes[k]:
            errors += [k]
    return errors
                                                                                                            
