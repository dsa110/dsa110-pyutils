#!/usr/bin/env python3
"""Example micro-service using DsaStore. This micro-service registers a 
   callback to handle asynchronous commands while writing monitor data
   every second.  Argument parsing has be left out as well as error handling.
"""

import time
from time import sleep
import dsautils.DsaStore as ds

# define which etcd key to watch for commands. It's usually
# /cmd/<subsystem>
# or if the subsystem has identical replications as in snaps or antennas, then
# we use /0 to mean all and <number> for a specific one. For example:
# /cmd/<subsystem>/0 and
# /cmd/<subsystem>/5
# Thus the code would listen for changes to /cmd/.../0 and /cmd/.../5
# so it will handle commands sent to all(/cmd/.../0) as well as(/cmd/.../5)
EX_SERVICE_CMD_KEY = "/cmd/ex"
EX_SERVICE_MON_KEY = "/mon/ex"
MONITOR_UPDATE_IN_SECONDS = 1

# define current time is milliseconds
current_milli_time = lambda: int(round(time.time() * 1000))

def get_monitor_data():
    """ Return a dictionary representing monitor data.
        The key is the monitor point name and value is its value
    """
    md = {}
    md['time'] = current_milli_time()

    return md

def process_command(my_cmds):
    """Etcd watch callback function. Called when values of watched
       key are updated.

    :param my_cmds: Dictionary containing the key and value.
    """

    # Extract the cmd and value(ie. args if any)
    cmd = my_cmds['cmd']
    val = my_cmds['val']

    # cmd_func is a dictionary of predefined functions
    # i.e. cmd_func["move"] = process_move(el_ang_in_deg)
    #      cmd_func["halt"] = process_halt(arg=None)
    # This is one way around having a huge if-else. super clean.

    # Add check if key exists. if not, throw.
    cmd_func[cmd](val)

def start_service(args):
    """Main entry point. Will never return.

    :param args: Input arguments from argparse.
    """

    my_store = ds.DsaStore()
    my_store.add_watch(MY_SERVICE_CMD_KEY, process_command)

    # Send monitor data every second forever.
    while True:
        md = get_monitor_data()
        my_store.put_dict(MY_SERVICE_MON_KEY, md)
        sleep(MONITOR_UPDATE_IN_SECONDS)

if __name__ == '__main__':
    # parse args not shown
    start_service(the_args)
