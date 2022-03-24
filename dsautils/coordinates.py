"""Functions to get pointing information for the DSA.
"""

import datetime
import numpy as np
from influxdb import DataFrameClient
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord, FK5, ICRS
from astropy.wcs import WCS
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

def create_WCS(coords: SkyCoord, beam_sep: u.Quantity, npix: int) -> "wcs":
    """Creates astropy wcs object for beams

    Parameters
    ----------
    c : astropy SkyCoord object
        Center coordinates
    cdelt_deg: float
        Separation between beams in degrees
    Returns
    -------
    astropy wcs object
        wcs corresponding to image of beams.
    """
    cdelt_deg = beam_sep.to_value(u.deg)
    w = WCS(naxis=2)
    w.wcs.crpix = [npix//2, npix//2]
    w.wcs.cdelt = np.array([cdelt_deg, cdelt_deg])
    w.wcs.crval = [coords.ra.deg, coords.dec.deg]
    w.wcs.ctype = ["RA---SIN", "DEC--SIN"]
    return w

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
    npix = 1000
    beam_sep = 1.*u.arcmin

    if obstime is None:
        obstime = Time(datetime.datetime.utcnow())
        dec = DS.get_dict('/mon/array/dec')
        if dec:
            dec = dec['dec_deg']*u.deg
        else:
            dec = get_declination(get_elevation())
    else:
        elevation = get_elevation(obstime)
        dec = get_declination(elevation)

    if not usecasa:
        ra = obstime.sidereal_time('apparent', longitude=ct.OVRO_LON*u.rad)
        pointing = SkyCoord(ra=ra, dec=dec, frame=FK5, equinox=obstime)
        pointing = pointing.transform_to(ICRS)

    else:
        pointing = direction(
            'HADEC', 0., dec.to_value(u.rad), obstime=obstime.mjd)
        pointing = SkyCoord(*pointing.J2000(), unit='rad', frame=ICRS)

    print(f'Primary beam pointing: {pointing}')
    wcs_sky = create_WCS(pointing, beam_sep, npix)
    beam_pointing = wcs_sky.pixel_to_world(npix//2+(127-ibeam), npix//2)

    return beam_pointing.ra, beam_pointing.dec

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
