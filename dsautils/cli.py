import time
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units, table
from numpy import median
import click
from dsautils import dsa_store, coordinates
from event import lookup
import dsautils.dsa_syslog as dsl
from influxdb import DataFrameClient
from event import labels


logger = dsl.DsaSyslogger()    
logger.subsystem("software")
logger.app("mnccli")
de = dsa_store.DsaStore()
influx = DataFrameClient('influxdbservice.sas.pvt', 8086, 'root', 'root', 'dsa110')

ovro_longitude_deg = -118.2819
ovro_latitude_deg = 37.2339
MS_PER_SECOND = 1000

# etcd monitor commands

@click.group('dsatm')
def tm():
    pass


@tm.command()
@click.option('--mjd', type=float)
@click.option('--localtime', type=str)
@click.option('--utctime', type=str)
def radecel(mjd=None, localtime=None, utctime=None):
    """ Get antenna pointing (RA, Dec, Elevation) at any time.
    Time can be defined as mjd, local or UT time.
    localtime string should have timezone attached to the string. utctime must not.
    Unix date utility can get time from descriptive term, e.g.:
    "> date --date='TZ="America/Los_Angeles" 10:00 yesterday' -Iseconds"
    "2021-02-02T10:00:00-08:00"
    The local time (with time zone) can be pasted into "localtime" argument to get values at that time.
    """

    if mjd is not None and localtime is None and utctime is None:
        tu = int(MS_PER_SECOND*Time(mjd, format='mjd').unix)
        tm = Time(mjd, format='mjd')
    elif mjd is None and localtime is not None and utctime is None:
        assert localtime.count('-') == 3
        tt, _, tz = localtime.rpartition('-')
        tu = int(MS_PER_SECOND*Time(tt, format='isot').unix)
        tm = Time(tt, format='isot')
        tu += MS_PER_SECOND*int(tz.split(':')[0])*3600    # millisecond offset for time zone hours
    elif mjd is None and localtime is None and utctime is not None:
        assert utctime.count('-') == 2
        tu = int(MS_PER_SECOND*Time(utctime, format='isot').unix)
        tm = Time(utctime, format='isot').mjd
    else:
        print('Must provide either mjd or localtime')
        return

    query = f'SELECT time,ant_num,ant_el FROM "antmon" WHERE time >= {tu}ms and time < {tu+MS_PER_SECOND}ms'
    print(query)
    try:
        result = influx.query(query)
#        print(result['antmon'])
        med_ant_el = median(result['antmon']['ant_el'])
        ha = tm.sidereal_time("apparent", ovro_longitude_deg*units.deg)
        print(f'MJD, RA, Decl, Elev (deg): {mjd}, {ha.to_value(units.deg)}, {med_ant_el+ovro_latitude_deg-90}, {med_ant_el}')
    except (KeyError, TypeError):
        print('No values (or None) returned by query.')


@tm.command()
@click.option('--mjd', type=float)
@click.option('--localtime', type=str)
@click.option('--utctime', type=str)
def temperature(mjd=None, localtime=None, utctime=None):
    """ Get weather at any time.
    Time can be defined as mjd, local or UT time.
    localtime string should have timezone attached to the string. utctime must not.
    Unix date utility can get time from descriptive term, e.g.:
    "> date --date='TZ="America/Los_Angeles" 10:00 yesterday' -Iseconds"
    "2021-02-02T10:00:00-08:00"
    The local time (with time zone) can be pasted into "localtime" argument to get values at that time.
    """

    if mjd is not None and localtime is None and utctime is None:
        tu = int(MS_PER_SECOND*Time(mjd, format='mjd').unix)
        tm = Time(mjd, format='mjd')
    elif mjd is None and localtime is not None and utctime is None:
        assert localtime.count('-') == 3
        tt, _, tz = localtime.rpartition('-')
        tu = int(MS_PER_SECOND*Time(tt, format='isot').unix)
        tm = Time(tt, format='isot')
        tu += MS_PER_SECOND*int(tz.split(':')[0])*3600    # millisecond offset for time zone hours
    elif mjd is None and localtime is None and utctime is not None:
        assert utctime.count('-') == 2
        tu = int(MS_PER_SECOND*Time(utctime, format='isot').unix)
        tm = Time(utctime, format='isot').mjd
    else:
        print('Must provide either mjd or localtime')
        return

    query = f'SELECT time,airtemp FROM "wxmon" WHERE time >= {tu}ms and time < {tu+30000}ms'
    try:
        result = influx.query(query)
        temp = float(result['wxmon']['airtemp'])
        print(f'Temperature on {mjd}: {temp}C')

    except KeyError:
        print('No values returned by query.')


@click.group('dsamon')
def mon():
    pass


@mon.command()
@click.argument('antnum', type=int)
def ant(antnum):
    """ Display antenna state
    """

    try:
        vv = de.get_dict('/mon/ant/{0}'.format(antnum))
        print(vv)
    except KeyDoesNotExistException:
        logger.warn("Antnum {0} not found".format(antnum))


@mon.command()
@click.argument('antnum', type=int)
def beb(antnum):
    """ Display beb monitor points
    """

    try:
        vv = de.get_dict('/mon/beb/{0}'.format(antnum))
        print(vv)
    except KeyDoesNotExistException:
        logger.warn("antnum {0} not found".format(antnum))


@mon.command()
@click.argument('snapnum', type=int)
def snap(snapnum):
    """ Display snap state
    """
    
    try:
        vv = de.get_dict('/mon/snap/{0}'.format(snapnum))
        print(vv)
    except KeyDoesNotExistException:
        logger.warn("snapnum {0} not found".format(snapnum))


@mon.command()
@click.argument('antnum', type=int)
def getcal(antnum):
    """ Display antenna calibration state
    """
    
    vv = de.get_dict('/mon/cal/{0}'.format(antnum))

    print(vv)

@mon.command()
@click.argument('subsystem', type=int)
@click.argument('antnum', type=int)
@click.option('--timeout', type=int, default=None)
def watch(subsystem, antnum, timeout):
    """ Wait for antenna commanded state to change
    """
    def my_cb(event: "Dictionary"):
        print(event)

    assert subsystem in ['ant', 'snap']

    vv = de.get_dict('/cmd/{0}/{1}'.format(subsystem, antnum))
    print("Watching antenna {0} for command. Current commanded values: {1}".format(antnum, vv))

    de.add_watch('/cmd/{0}/{1}'.format(subsystem, antnum), my_cb)
    t0 = time.time()
    if timeout is not None:
        while time.time() - t0 < timeout:
            time.sleep(1)
    else:
        while True:
            time.sleep(1)


@mon.command()
@click.argument('antnum', type=int)
@click.argument('gainamp_a', type=float)
@click.argument('gainamp_b', type=float)
@click.argument('gainphase_a', type=float)
@click.argument('gainphase_b', type=float)
@click.argument('delay_a', type=float)
@click.argument('delay_b', type=float)
@click.argument('calsource', type=str)
@click.argument('gaincaltime', type=float)
@click.argument('delaycaltime', type=float)
def putcal(antnum, time, gainamp_a, gainamp_b, gainphase_a, gainphase_b, delay_a, delay_b,
           status, calsource, gaincaltime_offset, delaycaltime_offset, sim=False):
    """ Set calibration gain amplitude and delay.
    Requires amplitude, phase, delay per antnum and pol (a/b).
    time is transit of source (in mjd).
    gain and delay values are output of calibration pipeline for A/B pols.
    calsource is name of calibration source.
    time offset arguments are relative to time (in seconds; later is positive).
    status is integer code that defines quality of value (0 = "good").
    sim is optional arg to define whether values are simulated or real.
    """

    dd = {'ant_num': antnum, 'time': time, 'pol': ['A','B'],
          'gainamp': [gainamp_a, gainamp_b],
          'gainphase': [gainphase_a, gainphase_b],
          'delay': [delay_a, delay_b],
          'status': status, 'calsource': calsource,
          'gaincaltime_offset': gaincaltime_offset,
          'delaycaltime_offset': delaycaltime_offset, 'sim': sim}
    de.put_dict('/mon/cal/{0}'.format(antnum), dd)

    
@mon.command()
def corr():
    now = Time.now().mjd
    print('capture_rate, drop_rate, drop_count, b0_full, b0_clear, b0_written, b0_read, last_seq:')
    ages = []  # hold mp age in seconds
    for i in range(1,17):
        h = de.get_dict('/mon/corr/'+str(i))
        ages.append(24*3600*(now-float(h['time'])))
        print(h['capture_rate'], h['drop_rate'], h['drop_count'],
              h['b0_full'], h['b0_clear'], h['b0_written'], h['b0_read'],h['last_seq'])

    print('\ncorr monitor point ages (s):', ages)

# etcd control commands

@click.group('dsacon')
def con():
    pass


@con.command()
@click.argument('antnum', type=str)
@click.argument('elev', type=float)
def move(antnum, elev):
    """ Set an antenna elevation
    """

    logger.info("Commanding ant {0} to move to {1}".format(antnum, elev))
    de.put_dict('/cmd/ant/{0}'.format(antnum),  {"cmd": "move", "val": elev})


@con.command()
@click.argument('antnum', type=str)
def halt(antnum):
    """ Halt motion of antenna
    """

    logger.info("Commanding ant {0} to halt".format(antnum))
    de.put_dict('/cmd/ant/{0}'.format(antnum),  {"cmd": "halt"}) # test this


@con.command()
@click.argument('antnum', type=str)
@click.argument('ab', type=str)
@click.argument('value', type=bool)
def noise(antnum, ab, value):
    """ Set a the state of noise diode True=on, False=off.
    """

    assert ab in ['a', 'b']
    logger.info("Commanding ant {0} noise {1} to {2}".format(antnum, ab, value))
    de.put_dict('/cmd/ant/{0}'.format(antnum),  {"cmd": "noise_{0}_on".format(ab), "val": value})


@con.command()
@click.argument('snapnum', type=str)
@click.argument('prop', type=str)
@click.argument('val', type=str)
def snap(snapnum, prop, val):
    """ Set a snap property to new value
    """

    pass


@con.command()
@click.argument('command', type=str)
def corr(command):
    """ Start/stop beamformer and search processes on corr nodes
    command can be "start", "stop", "set".
    """
    assert command.lower() in ['start', 'stop', 'set']

    if command.lower() == 'start':
        print("Starting search processes")
        for i in range(17,21):
            de.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':0})
        time.sleep(5)
        print("Starting beamformer processes")
        for i in range(1,17):
            de.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':0})
    elif command.lower() == 'stop':
        print("Stopping all nodes")
        de.put_dict('/cmd/corr/0', {'cmd':'stop', 'val':0})
    elif command.lower() == 'set':
        corr_dict = de.get_dict('/mon/corr/1')
        if 'last_seq' in corr_dict:
            print("Setting counter for beamformer processes")
            counter = corr_dict['last_seq'] + 500000
            de.put_dict('/cmd/corr/0', {'cmd':'utc_start', 'val':str(int(counter))})
        else:
            print("Could not find counter")

@con.command()
@click.option('--name', type=str, default='test')
def trigger(name):
    """ Send trigger to save buffer in corr node RAM
    Can set delay for trigger in the future (in spectra)
    """

    h = de.get_dict('/mon/corr/1')
    bindex = h['b5_read']  # TODO: check that this is right key

    print(f'buffer index list {bindex}')
    itime = int(bindex)*2048 + 20480*2 + 290*2048 - 350000

    print(f'Triggering for itime {itime}')
    de.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': str(itime)+'-'+name+'-'})

    print('Trigger sent with name '+name)

    # If we need to trigger writing json with info, use this syntax:
#    output_dict = {itime: {}}
#    output_dict[itime]['mjds'] = ...
#    ... maybe fill with info to signify forced trigger?
#    de.put_dict('/mon/corr/1/trigger', output_dict)


@con.command()
@click.argument('candname', type=str)
@click.option('--label', type=str, default=None)
def label(candname, label):
    """ Add or list labels associated with trigger json file for a candidate.
    candname is used to find file to read or edit.
    label can be "astrophysical", "rfi", "instrumental", "unsure/noise", "archive".
    archive label is required to preserve candidates when clearing disks.
    if no label given, then this function prints current labels.

    TODO: get full path to filename either from etcd key or from glob.
    """

    filename = f'{candname}.json'
    if label is not None:
        labels.set_label(candname, label, filename=filename)
    else:
        labels.list_cands_labels(filename)


@click.group('dsacand')
def cand():
    pass


def get_coord(mjd, ibeam):
    """ Given (mjd, ibeam), return SkyCoord
    TODO: include arbitrary elevation
    """

    return SkyCoord(*coordinates.get_pointing(ibeam=ibeam, obstime=Time(mjd, format='mjd')), unit='rad')


@cand.command()
@click.argument('mjd', type=float)
@click.argument('ibeam', type=int)
def get_radec(mjd, ibeam):
    """ Calculate SkyCoord from mjd/ibeam and print in nice form.
    """

    print(get_coord(mjd, ibeam).to_string('hmsdms'))


@cand.command()
@click.argument('mjd', type=float)
@click.argument('ibeam', type=int)
def get_DM(mjd, ibeam):
    """ Use ne2001 model to calculate max Galactic DM toward given position.
    """

    try:
        from ne2001 import density, ne_io
    except ImportError:
        print('ne2001 library not available')
        return
    
    ne = density.ElectronDensity(**ne_io.Params())
    co = get_coord(mjd, ibeam)

    print(ne.DM(co.galactic.l, co.galactic.b, 20))


@cand.command()
@click.argument('mjd', type=float)
@click.argument('ibeam', type=int)
@click.option('--radius', type=float, default=60)
def check_nvss(mjd, ibeam, radius):
    """ Search NVSS catalog for (RA, Dec) within radius in arcseconds.
    TODO: use local file instead of astroquery.
    """

    from astroquery import ned
    ne = ned.Ned()

    co = get_coord(mjd, ibeam)
    tab = ne.query_region(co, radius=radius*units.arcsec)
    print(tab[['NVSS' in row['Object Name'] for row in tab]])


@cand.command()
@click.argument('mjd', type=float)
@click.argument('ibeam', type=int)
@click.option('--radius', type=float, default=60)
def check_pulsars(mjd, ibeam, radius):
    """ Search pulsar catalog for (RA, Dec) within radius in arcseconds.
    """

    co = get_coord(mjd, ibeam)
    result = lookup.find_associations(co.ra.value, co.dec.value, atnf_radius=3.3*3600, mode='pulsar')
#    ind_near = psrtools.match_pulsar(co.ra, co.dec, thresh_deg=radius/3600)

    print("\n\nMJD: %0.5f" % mjd)
    print("RA and Dec: %0.2f %0.2f" % (co.ra.value, co.dec.value))
    print(result)
#    for ii in ind_near:
#        print('    %s with DM=%0.1f pc cm**-3' % (psrtools.query['PSRB'][ii], psrtools.query['DM'][ii]))


# TODO: fix path and include catalog
#@cand.command()
#@click.argument('mjd', type=float)
#@click.argument('ibeam', type=int)
#@click.option('--radius', type=float, default=60)
#@click.option('--clupath', type=str, default='/home/user/claw/CLU_20190708.hdf5')
def check_CLU(mjd, ibeam, radius, clupath):
    """ Look for CLU catalog sources in given beam.
    Radius is defined in arcsec.
    """

    import numpy as np

    try:
        from psquery import clutools
    except ImportError:
        print('psquery library not available')
        return
    
    tabclu = clutools.compile_CLU_catalog(clupath)
    tabclu = table.Table.from_pandas(tabclu)
    cat = clutools.table2cat(tabclu)
    co_clu = SkyCoord(cat.ra, cat.dec, unit='deg')
    print(f'{len(co_clu)} CLU sources read')

    co = get_coord(mjd, ibeam)
    idx, d2, _ = co.match_to_catalog_sky(co_clu)
    matches = co_clu[idx]
    sep = d2.to_value('arcsec')[0]
    if sep < radius:
        print(tabclu[idx])
    else:
        print(f'No CLU association found within {radius} arcsec')


@cand.command()
@click.argument('mjd', type=float)
@click.argument('ibeam', type=int)
@click.option('--radius', type=float, default=10)
def check_ps1(mjd, ibeam, radius, ):
    """ Look for PS1 catalog counterparts with psquery.
    Radius is defined in arcsec.
    """

    import numpy as np

    try:
        from psquery import psquery
    except ImportError:
        print('psquery library not available')
        return
    
    co = get_coord(mjd, ibeam)
    result = psquery.query_radec(co.ra.value, co.dec.value, radius=radius/3600)
    if result is not None:
        bands = ['g', 'r', 'i', 'z', 'y']
        nmatch, dist, datastr = result
        ss = datastr.split(',')
        ra, dec = float(ss[1]), float(ss[2])
        mags = ss[-5:]
        brightmag = 999
        for i, mag in enumerate(mags):
            mag = float(mag)
            if mag < brightmag and mag > -999:
                brightmag = mag
                band = bands[i]
        print(f'Found {nmatch} PS1 associations. Nearest at ({ra}, {dec}) with {band}={brightmag} mag.')
    else:
        print(f'No PS1 association found within {radius} arcsec')

