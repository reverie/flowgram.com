import logging, logging.handlers, sys

from flowgram.localsettings import fg_LOG_DIR
from flowgram.core.helpers import _mkdir

_mkdir(fg_LOG_DIR)

main_logger = logging.getLogger('main')
main_log = logging.FileHandler(fg_LOG_DIR + 'main.log')
main_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
main_log.setLevel(logging.DEBUG)
main_logger.addHandler(main_log)
main_logger.setLevel(logging.DEBUG)

#cache_logger = logging.getLogger('cache')
#cache_log = logging.FileHandler(fg_LOG_DIR + 'cache.log')
#cache_log.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
#cache_log.setLevel(logging.DEBUG)
#cache_logger.addHandler(cache_log)
#cache_logger.setLevel(logging.DEBUG)


def callersname():
    # callersname copied from ASPN
    return sys._getframe(2).f_code.co_name

def log_at_level(level):
    def logger(msg='', request=None):
        caller = callersname()
        if request:
            if request.user.is_authenticated():
                u = request.user.username
            else:
                u = request.META['REMOTE_ADDR']
        else:
            u = '?'
        main_logger.log(level, ("[function: %s] [user: %s] %s" % (caller, u, msg)))
    return logger


def action(message):
    debug('Action log: %s' % message)


debug    = log_at_level(logging.DEBUG)
info     = log_at_level(logging.INFO)
error    = log_at_level(logging.ERROR)
critical = log_at_level(logging.CRITICAL)
sec      = log_at_level(66)

def trace(msg=''):
    main_logger.log(logging.CRITICAL, msg, exc_info=True)

def sec_req(request, msg):
    sec(msg, request)

cache_hit = cache_miss = cache = lambda x: None

#def cache_hit(key):
    #cache_logger.log(logging.INFO, "Cache hit on %s" % key)
    
#def cache_miss(key):
    #cache_logger.log(logging.INFO, "Cache miss on %s" % key)
    
#def cache(msg):
    #cache_logger.log(logging.DEBUG, msg)