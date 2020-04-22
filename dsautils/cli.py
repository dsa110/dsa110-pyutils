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
    
    vv = de.get_dict('/mon/ant/{0}'.format(antnum))

#    logger.info(vv)
    print(vv)

@mon.command()
@click.argument('snapnum', type=int)
def snap(snapnum):
    """ Display snap state
    """
    
    vv = de.get_dict('/mon/snap/{0}'.format(snapnum))

#    logger.info(vv)
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
