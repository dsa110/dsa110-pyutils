"""Functions to get pointing information for the DSA.
"""

import datetime
import warnings
import numpy as np
from influxdb import DataFrameClient
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord, FK5, ICRS
import dsacalib.constants as ct
from dsacalib.utils import direction
import dsautils.cnf as cnf
from dsautils import dsa_store

DS = dsa_store.DsaStore()
CORR_CNF = cnf.Conf().get('corr')
INFLUX = DataFrameClient(
    'influxdbservice.sas.pvt',
    8086,
    'root',
    'root',
    'dsa110'
)

def get_elevation(tobs: Time = None, tol: float = 0.25) -> u.Quantity:
    """Get the pointing elevation now or at a time in the past.

    :param tobs: The time at which to get the elevation. If None, gets current elevation.
    :type tobs: astropy Time
    :param tol: Tolerance for difference between commanded and current elevation, in degrees.
    :type tol: float

    :return: Elevation, current one from etcd if tobs is None, otherwise past elevation from influx.
    """
    if tobs is not None:
        time_ms = int(tobs.unix*1000)
        query = ('SELECT ant_num, ant_el, ant_cmd_el, ant_el_err FROM "antmon" WHERE '
                 'time >= {0}ms and time < {1}ms'.format(time_ms-500, time_ms+500))
        el_df = INFLUX.query(query)
        if 'antmon' in el_df:
            # Defaults to current value if no value in etcd
            el_df = el_df['antmon']
            el = np.median(el_df[np.abs(el_df['ant_el_err']) < 1.]['ant_cmd_el'])*u.deg
            return el
    commanded_els = np.zeros(len(CORR_CNF['antenna_order']))
    for idx, ant in CORR_CNF['antenna_order'].items():
        try:
            antmc = DS.get_dict('/mon/ant/{0}'.format(ant))
            a1 = np.abs(antmc['ant_el'] - antmc['ant_cmd_el'])
        except:
            a1 = 2.*tol
        if a1 < tol:
            commanded_els[idx] = antmc['ant_cmd_el']
        else:
            commanded_els[idx] = np.nan
    return np.nanmedian(commanded_els)*u.deg

def get_declination(elevation: u.Quantity, latitude: u.Quantity = ct.OVRO_LAT*u.rad) -> u.Quantity:
    """Calculates the declination from the elevation.

    :param elevation: The pointing elevation.
    :type elevation: astropy Quantity
    :param latitude: The latitude of the telescope.
    :type latitude: astropy Quantity

    :return: The declination, in degrees or equivalent.
    :rtype: astropy Quantity
    """
    return (elevation+latitude-90*u.deg).to(u.deg)

def get_beam_ha(ibeam: int, beam_sep: u.Quantity = 1*u.arcmin) -> u.Quantity:
    """Get hourangle of beam.

    :param ibeam: The beam number
    :type ibeam: int
    :param beam_sep: The separation of the beams
    :type beam_sep: astropy Quantity

    :return: The HA of the beam.
    :rtype: astropy Quantity
    """
    if ibeam != 127:
        warnings.warn('Beam direction not implemented. Defaulting to beam 127.')
        ibeam = 127
    # TODO: Update using WCS projection to account for different
    # coordinate systems of beams and LST
    return beam_sep*(127-ibeam)

def get_pointing(ibeam: int = 127, obstime: Time = None, usecasa: bool = False) -> tuple:
    """Get pointing of the primary beam or a synthesized beam.

    :param ibeam: The beam number. Defaults to beam 127, at the centre of the primary beam.
    :type ibeam: int
    :param obstime: The time of the observation.  Defaults to now.
    :type obstime: astropy Time
    :param usecasa: If true, uses CASA to calculate coordinates.  Otherwise, uses astropy. Defaults to astropy (faster, less precise).
    :type usecasa: bool

    :return: (ra, dec) as astropy Quantities for the centre of the synthesized or primary beam.
    :rtype: tuple
    """
    if obstime is None:
        obstime = Time(datetime.datetime.utcnow())
        elevation = get_elevation()
    else:
        elevation = get_elevation(obstime)
    dec_now = get_declination(elevation)

    if not usecasa:
        ra_now = obstime.sidereal_time(
            'apparent',
            longitude=ct.OVRO_LON*u.rad
        )+get_beam_ha(ibeam)
        pointing = SkyCoord(ra=ra_now, dec=dec_now, frame=FK5, equinox=obstime)
        pointing_J2000 = pointing.transform_to(ICRS)
        return pointing_J2000.ra, pointing_J2000.dec

    pointing = direction(
        'HADEC',
        get_beam_ha(ibeam),
        dec_now.to_value(u.rad),
        obstime=obstime
    )
    ra, dec = pointing.J2000()
    return (ra*u.rad).to(u.deg), (dec*u.rad).to(u.deg)

def get_galcoord(ra: float, dec: float) -> tuple:
    """Converts RA and dec to galactic coordinates.

    :param ra: RA in degrees.
    :type ra: float
    :param dec: dec in degrees
    :type dec: float

    :return: Galactic (l, b) in degrees
    :rtype: tuple
    """
    coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
    galcoord = coord.galactic
    return galcoord.l.deg, galcoord.b.deg
