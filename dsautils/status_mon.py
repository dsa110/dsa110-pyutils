import numpy as np 
import time

from astropy.time import Time

from dsautils import dsa_store
import dsautils.dsa_syslog as dsl
from influxdb import DataFrameClient
import dsacalib.constants as ct

logger = dsl.DsaSyslogger()    
logger.subsystem("software")
logger.app("mnccli")
de = dsa_store.DsaStore()
influx = DataFrameClient('influxdbservice.sas.pvt', 8086, 'root', 'root', 'dsa110')

ovro_longitude_deg = np.degrees(ct.OVRO_LAT) #-118.2819
ovro_latitude_deg = np.degrees(ct.OVRO_LAT)  #37.2339

class Monitor:
    """ Class to test the status of observing on DSA-110.
    """
    def __init__(self):
        self.el_bool = None
        self.dm_bool = None 
        self.block_bool = None 
        self.corrmon_bool = None 
        self.T2_bool = None 
        self.system_status = None 
        self.ant_el_rms = None 
        self._mjd = None
        self.status_arr = np.zeros([3], dtype=bool)

    def query_all(self, mjd=None, localtime=None, utctime=None):
        """ Get antenna pointing (RA, Dec, Elevation) at any time.
        Time can be defined as mjd, local or UT time.
        localtime string should have timezone attached to the string. utctime must not.
        Unix date utility can get time from descriptive term, e.g.:
        "> date --date='TZ="America/Los_Angeles" 10:00 yesterday' -Iseconds"
        "2021-02-02T10:00:00-08:00"
        The local time (with time zone) can be pasted into "localtime" argument to get values at that time.
        """
        self._mjd = mjd
        print("Querying MJD %.6f" % mjd)

        if mjd is not None and localtime is None and utctime is None:
            tu = int(1000*Time(mjd, format='mjd').unix)
            tm = Time(mjd, format='mjd')
        elif mjd is None and localtime is not None and utctime is None:
            assert localtime.count('-') == 3
            tt, _, tz = localtime.rpartition('-')
            tu = int(1000*Time(tt, format='isot').unix)
            tm = Time(tt, format='isot')
            tu += 1000*int(tz.split(':')[0])*3600    # millisecond offset for time zone hours
        elif mjd is None and localtime is None and utctime is not None:
            assert utctime.count('-') == 2
            tu = int(1000*Time(utctime, format='isot').unix)
            tm = Time(utctime, format='isot').mjd
        else:
            print('Must provide either mjd or localtime')
            return

        query0 = f'SELECT time,ant_num,ant_el FROM "antmon" WHERE time >= {tu-160000}ms and time < {tu}ms'
        query1 = f'SELECT corr_num,b0_clear FROM "corrmon" WHERE time >= {tu-160000}ms and time < {tu}ms AND corr_num != \'17\' AND corr_num != \'18\' AND corr_num != \'19\' AND corr_num != \'20\''
        query2 = f'SELECT corr_num,full_blockct FROM "corrmon" WHERE time >= {tu-160000}ms and time < {tu}ms AND corr_num = \'17\' OR corr_num = \'18\' OR corr_num = \'19\' OR corr_num = \'20\''
        query3 = f'SELECT t1_num, DM_space_searched FROM "t1mon" WHERE time >= {tu-160000}ms and time < {tu}ms'        
        query4  = f'SELECT t2_num, gulp_status FROM "t2mon" WHERE time >= {tu-160000}ms and time < {tu}ms'        
        result0 = influx.query(query0) # ant el 
        result1 = influx.query(query1) # corrmon 
        result2 = influx.query(query2) # full block count 
        result3 = influx.query(query3) # DM space searched 
        result4 = influx.query(query4) # T2 status 

        try:
            return result0, result1, result2, result3, result4
        except:
            print("Query failed")

    def calc_el_stats(self,ant_el,ant_num):
        """ Calculate the core antenna elevation RMS
        and the fraction of core antennas that are 
        more than 6 and 30 arcminutes from the median,
        respectively 
        """
        ant_el = ant_el.values[ant_num<64]
        med_ant_el = np.median(ant_el)
        ant_absdev = np.abs(ant_el-med_ant_el)

        # Calculate fraction of antennas off by >6 arcmin
        f6arcmin = len(np.where(ant_absdev>6/60.)[0]) / float(len(ant_el))
        # Calculate fraction of antennas off by >30 arcmin
        f30arcmin = len(np.where(ant_absdev>30/60.)[0]) / float(len(ant_el))
        el_RMS = np.std(ant_absdev)
        self.ant_el_rms = el_RMS

        return el_RMS, f6arcmin, f30arcmin

    def ant_el_decision_crit(self, el_RMS, f6arcmin, f30arcmin):
        """ If elevation RMS is more than 0.5 degrees,
        consider the system not observing 
        """
        if el_RMS>0.5:
            return False
        else:
            return True

        #if f6arcmin>0.5 or f30arcmin>0.25:
        #    return False 
        #elif f6arcmin>0.1 and f30arcmin>0.05:
        #    return False 
        #else:
        #    return True

    def ant_el_decision(self, query_el):
        """ Set elevation decision boolean value 
        based on decision criteria
        """
        ant_el = query_el['antmon']['ant_el']
        ant_num = query_el['antmon']['ant_num'].values.astype(int)
        if ant_el is None:
            return
        el_RMS, f6arcmin, f30arcmin = self.calc_el_stats(ant_el, ant_num)
        decision_bool = self.ant_el_decision_crit(el_RMS, 
                                                  f6arcmin, 
                                                  f30arcmin)
        self.el_bool = decision_bool

    def b0_decision_crit(self):
        pass

    def b0_decision(self, query_b0):
        pass

    def dm_search_decision(self, query_dm, dm_max=1101.05):
        """ Set DM search observing status to False 
        if the mean maximum DM searched per block is less than 
        half of the maximum value (dm_max)
        """
        dm_max_arr = query_dm['t1mon']['DM_space_searched'].values
        if np.mean(dm_max_arr)<dm_max/2.:
            self.dm_bool = False 
        else:
            self.dm_bool = True

    def full_blockct_decision_crit(self):
        pass 

    def full_blockct_decision(self, query_b0):
        pass 

    def T2_status_decision(self, query_T2):
        """ 0 means good, non-zero means some kind of failure for a gulp.
            1 means not all clients are gulping
            2 means different gulps received, so restarting clients
            3 means overflow error during parsing of table.
            t2_num is the process number running T2. Only one for now.
        """
        if query_T2['t2mon']['gulp_status'].values.sum()!=0:
            self.T2_bool = False
        else:
            self.T2_bool = True

    def check_status(self):
        """ Test status of three (for now) observing criteria: 
        elevation RMS, max DM, and T2 status 
        """
        self.status_arr = np.array([self.el_bool, self.dm_bool, self.T2_bool])
        if all(self.status_arr):
            self.system_status = True
        else:
            self.system_status = False
            if self.el_bool is not True:
                print('Failed on elevation')
                self.status_arr[0] = False
            if self.dm_bool is not True:
                print('Failed on DM_space_searched')
                self.status_arr[1] = False
            if self.T2_bool is not True: 
                print('Failed on T2')
                self.status_arr[2] = False


def check_obs(mjd):
    Mon = Monitor()

    # Ant el, Corrmon, Full block count, DM space searched, T2 status
    r0,r1,r2,r3,r4 = Mon.query_all(mjd=mjd)

    nempty=0
    if len(r0):
        Mon.ant_el_decision(r0)
    else:
        print("    Ant mon query empty")
        nempty += 1
    #Mon.corrmon_decision(r1)
    if len(r2):
        Mon.full_blockct_decision(r2)
    else:
        print("    Full block query empty")
        nempty += 1

    if len(r3):
        Mon.dm_search_decision(r3)
    else:
        print("    DM query empty")
        nempty += 1
    if len(r4):
        Mon.T2_status_decision(r4)
    else:
        print("    T2 query empty")
        nempty += 1

    Mon.check_status()
    return Mon.system_status, Mon.status_arr


def get_fraction_day(mjd_start,nsec_block=160.):
    """ Obtain the fraction of nsec_blocks in a day 
    during which the system was observing. This 
    function will also return a status array (status_arr_day)
    that has value 1 when the criterion was passed and 0 if not
    """
    nsec_day = 86400.
    nblock_per_day = int(nsec_day // nsec_block)
    bool_arr = np.zeros([nblock_per_day], dtype=np.bool)
    status_arr_day = np.zeros([nblock_per_day, 3])

    for ii in range(nblock_per_day):
        mjd_ii = mjd_start + ii*nsec_block/nsec_day
        bool_arr[ii], status_arr = check_obs(mjd_ii)
        status_arr_day[ii] = status_arr.astype(int)

    fraction_on = np.sum(bool_arr) / float(nblock_per_day)
    return fraction_on, status_arr_day


def run_day_loop():
    while True:
        nsec_day = 86400.
        nsec_block = 160.

        mjd_start = Time.now().mjd - 1.0

        fraction_on, status_arr_day = get_fraction_day(mjd_start, nsec_block)

        time_until_tomorrow = nsec_day - nsec_day*(Time.now().mjd - mjd_start - 1)
        print("Obs time fraction: %f" % fraction_on)
        print("Finished %0.6f. Sleeping until tomorrow." % mjd_start)
        ff = open('%0.6f.txt'%mjd_start, 'w')
        ff.write(fraction_on)
        ff.close()
        time.sleep(time_until_tomorrow)


def push_status(status, arr):
    """ Set etcd key with status values.
    Sets "status" to overall status good/bad = 1/0.
    Also sets "status0", ... to each value in arr.
    """

    version = 1
    status_num = 1
    dd = {'status_num': status_num, 'time': Time.now().mjd,
          'version': version, 'status': int(status)}
    for i in range(len(arr)):
        dd[f'status{i}'] = int(arr[i])
    de.put_dict(f'/mon/status/{status_num}', dd)
