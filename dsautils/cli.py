import time
import click
from dsautils import dsa_store
import dsautils.dsa_syslog as dsl

logger = dsl.DsaSyslogger()    
logger.subsystem("software")
logger.app("mnccli")
de = dsa_store.DsaStore()

# etcd monitor commands

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
    print('capture_rate, drop_rate, drop_count, b0_full, b0_clear, b0_written, b0_read, last_seq:')
    for i in range(1,17):
        h = de.get_dict('/mon/corr/'+str(i))
        print(h['capture_rate'], h['drop_rate'], h['drop_count'],
              h['b0_full'], h['b0_clear'], h['b0_written'], h['b0_read'],h['last_seq'])

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
