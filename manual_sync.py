from hera_corr_f import HeraCorrelator
import sys

corr = HeraCorrelator(redishost=None, config=sys.argv[1], use_redis=False)

corr.disable_output()
corr.do_for_all_f("change_period", block="sync", args=[0])
corr.resync(manual=True)
corr.enable_output()


