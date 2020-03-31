import time
import click
from dsautils import dsa_store
import dsautils.dsa_syslog as dsl

logger = dsl.DsaSyslogger()    
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
@click.argument('antnum', type=int)
@click.option('--timeout', type=int, default=None)
def watchant(antnum, timeout):
    """ Wait for antenna state to change
    """
    def my_cb(event: "Dictionary"):
        print(event)

    vv = de.get_dict('/mon/ant/{0}'.format(antnum))
    print("Watching antenna {0} for changes from {1}".format(antnum, vv))

    de.add_watch('/mon/ant/{0}'.format(antnum), my_cb)
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
@click.argument('subsystem', type=str)
def listkeys(subsystem):
    """
    Name of subsystem to list keys
    """
    
    assert subsystem in ['ant']
    vv = de.get_dict('/mon/{0}/1'.format(subsystem))

#    logger.info(list(vv.keys()))
    print(list(vv.keys()))
