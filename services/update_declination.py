"""Update the current pointing declination"""
import time
from functools import wraps
import traceback
import numpy as np
import astropy.units as u
import dsautils.dsa_store as ds
# import dsautils.dsa_syslog as dsl
from dsautils.coordinates import get_declination, get_elevation, get_pointing
from dsautils.status_mon import get_dm, get_rm

# DsaSyslogger not working on h23
# LOGGER = dsl.DsaSyslogger()
# LOGGER.subsystem("software")
# LOGGER.app("dsacalib")
# LOGGER.function("declination_service")
LOGGER = None

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
        print(f'Ra Dec: {radec}')
        update_galactic_dm(radec)
        # update_galactic_rm(radec)

        wait = wait_time_s - (time.time() - start)
        if wait > 0:
            time.sleep(wait_time_s)

def persistent(target: "Callable") -> "Callable":
    """Ensure any errant exceptions are logged but don't cause the service to stop."""
    @wraps(target)
    def wrapper(*args, **kwargs):
        try:
            target(*args, **kwargs)
        except Exception as exc:
            exception_logger(LOGGER, target.__name__, exc, throw=False)
    return wrapper

@persistent
def update_declination(tol_deg: float) -> None:
    """Get the current array declination and update value in etcd if needed.

    etcd value is only updated if the current and stored array declinations differ by more
    than TOL_DEG
    """
    declination = get_declination(get_elevation()).to_value(u.deg)
    stored_declination = ETCD.get_dict('/mon/array/dec')['dec_deg']

    if np.isnan(declination):
        LOGGER.info('No updated declination from antmc. '
                    f'Using current stored value of {stored_declination} deg')

    else:
        if not stored_declination or np.abs(declination - stored_declination) > tol_deg:
            ETCD.put_dict(
                '/mon/array/dec',
                {'dec_deg': declination})
            LOGGER.info(f'Updated array declination to {declination:.1f} deg')

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
            'ra_deg': ra,
            'dec_deg': dec})
    LOGGER.info(f'Updated array pointing to J2000 {ra:.1f} deg '
                f'{dec:.1f} deg')
    return ra, dec

@persistent
def update_galactic_dm(radec: tuple) -> None:
    """Update the galactic DM in the pointing direction."""
    gal_dm = get_dm(radec=radec)
    ETCD.put_dict(
        '/mon/array/gal_dm',
        {
            'gal_dm': gal_dm
        })
    LOGGER.info(f'Updated galactic DM to {gal_dm:.1f}')

@persistent
def update_galactic_rm(radec: tuple) -> None:
    """Update the galactic RM in the pointing direction."""
    gal_rm = get_rm(radec=radec)
    ETCD.put_dict(
        '/mon/array/gal_rm',
        {
            'gal_rm': gal_rm
        })
    LOGGER.info(f'Updated galactic RM to {gal_rm:.1f}')

def exception_logger(
        logger: "DsaSyslogger", task: str, exception: "Exception", throw: bool) -> None:
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
    if logger is not None:
        logger.error(error_string)
    else:
        print(error_string)
    if throw:
        raise exception

if __name__ == '__main__':
    CONFIG = get_config()
    declination_service(CONFIG['wait_time_s'], CONFIG['tol_deg'])
