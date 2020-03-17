import click
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.captureWarnings(True)
logger = logging.getLogger(__name__)

from dsautils import dsa_etcd
de = dsa_etcd.DsaEtcd()

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

    logger.info(vv)


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

    logger.info(list(vv.keys()))
