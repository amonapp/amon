import sys, time
from daemon import Daemon
from logger import AmonRedisLog
from runner import AmonRunner

class AmonDaemon(Daemon):
	
	def run(self):
		
		runner = AmonRunner()
		logger = AmonRedisLog()

		while True:
			system_info = runner.run()
			logger.save_dict(system_info)
			time.sleep(5)

if __name__ == "__main__":

	pidfile = '/tmp/amon-daemon.pid'


	daemon = AmonDaemon(pidfile)
	
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			print "Stopping Amon .."
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			print "Restaring Amon ..."
			daemon.restart()
		elif 'status' == sys.argv[1]:
			try:
				pf = file(pidfile,'r')
				pid = int(pf.read().strip())
				pf.close()
			except IOError:
				pid = None
			except SystemExit:
				pid = None

			if pid:
				print 'Amon is running as pid %s' % pid
			else:
				print 'Amon is not running.'
		
		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)
