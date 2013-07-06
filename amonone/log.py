import logging
from amonone.core import settings

logging.basicConfig(level=logging.ERROR, filename=settings.LOGFILE,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')

