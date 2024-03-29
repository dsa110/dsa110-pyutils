"""Update the current pointing declination"""
import time
from functools import wraps
import traceback
import numpy as np
import astropy.units as u
import dsautils.dsa_store as ds
import dsautils.dsa_syslog as dsl
from dsautils.coordinates import get_declination, get_elevation, get_pointing
from dsautils.status_mon import get_dm, get_rm
from dsautils.dsa_functions36 import current_mjd

LOGGER = dsl.DsaSyslogger()
LOGGER.subsystem("software")
LOGGER.app("dsacalib")
LOGGER.function("declination_service")

ETCD = ds.DsaStore()

def get_config() -> dict:
    """Return configuration."""
    return {
        'wait_time_s': 10,
        'tol_deg': 0.5}

def declination_service(wait_time_s: int, tol_deg: float) -> None:
    """Monitor the array declination and update as needed."""
    while True:
        start = time.time()

        update_declination(tol_deg)
        radec = update_pointing()
        update_galactic_dm(radec)
        update_galactic_rm(radec)

        wait = wait_time_s - (time.time() - start)
        if wait > 0:
            time.sleep(wait_time_s)

def persistent(target: "Callable") -> "Callable":
    """Ensure any errant exceptions are logged but don't cause the service to stop."""
    @wraps(target)
    def wrapper(*args, **kwargs):
        try:
            output = target(*args, **kwargs)
        except Exception as exc:
            exception_logger(target.__name__, exc, throw=False)
            output = None
        return output
    return wrapper

@persistent
def update_declination(tol_deg: float) -> None:
    """Get the current array declination and update value in etcd if needed.

    etcd value is only updated if the current and stored array declinations differ by more
    than TOL_DEG
    """
    declination = get_declination(get_elevation()).to_value(u.deg)
    stored_declination = ETCD.get_dict('/mon/array/dec')
    if stored_declination:
        stored_declination = stored_declination['dec_deg']

    if np.isnan(declination):
        message = ('No updated declination from antmc. '
                   f'Using current stored value of {stored_declination} deg')
        info_logger(message)

    else:
        if not stored_declination or np.abs(declination - stored_declination) > tol_deg:
            ETCD.put_dict(
                '/mon/array/dec',
                {
                    'time': current_mjd(),
                    'dec_deg': declination})

            message = (f'Updated array declination to {declination:.1f} deg')
            info_logger(message)

@persistent
def update_pointing() -> tuple:
    """Update the current pointing (J2000 ra and dec) in etcd.

    Returns ra,dec in degrees.
    """
    ra, dec = get_pointing()
    ra = ra.to_value(u.deg)
    dec = dec.to_value(u.deg)

    ETCD.put_dict(
        '/mon/array/pointing_J2000',
        {
            'time': current_mjd(),
            'ra_deg': ra,
            'dec_deg': dec})
    message = (f'Updated array pointing to J2000 {ra:.1f} deg '
               f'{dec:.1f} deg')
    info_logger(message)
    return ra, dec

@persistent
def update_galactic_dm(radec: tuple) -> None:
    """Update the galactic DM in the pointing direction."""
    gal_dm = get_dm(radec=radec)
    ETCD.put_dict(
        '/mon/array/gal_dm',
        {
            'time': current_mjd(),
            'gal_dm': gal_dm
        })
    info_logger(f'Updated galactic DM to {gal_dm:.1f}')

@persistent
def update_galactic_rm(radec: tuple) -> None:
    """Update the galactic RM in the pointing direction."""
    gal_rm = get_rm(radec=radec)
    ETCD.put_dict(
        '/mon/array/gal_rm',
        {
            'time': current_mjd(),
            'gal_rm': gal_rm[0],
            'gal_rm_std': gal_rm[1]
        })

    info_logger(f'Updated galactic RM to {gal_rm[0]:.1f} +/- {gal_rm[1]:.1f}')
    print(gal_rm)

def info_logger(message: str):
    if LOGGER:
        LOGGER.info(message)

    print(message)

def exception_logger(
        task: str, exception: "Exception", throw: bool) -> None:
    """Logs exception traceback to syslog using the dsa_syslog module.

    Parameters
    ----------
    logger : dsa_syslog.DsaSyslogger() instance
        The logger used for within the reduction pipeline.
    task : str
        A short description of where in the pipeline the error occured.
    exception : Exception
        The exception that occured.
    throw : boolean
        If set to True, the exception is raised after the traceback is written
        to syslogs.
    """
    error_string = 'During {0}, {1} occurred:\n{2}'.format(
        task, type(exception).__name__, ''.join(
            traceback.format_tb(exception.__traceback__)
        )
    )
    if LOGGER is not None:
        LOGGER.error(error_string)

    print(error_string)
    if throw:
        raise exception

if __name__ == '__main__':
    CONFIG = get_config()
    declination_service(CONFIG['wait_time_s'], CONFIG['tol_deg'])
