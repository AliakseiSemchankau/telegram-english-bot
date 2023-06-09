import datetime

default_date = datetime.datetime(2023,5,31)
default_delta = 24 * 3600

SCRIPT = "./camb"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'
    
def today():
	return round(datetime.datetime.utcnow().timestamp() - default_date.timestamp())
    
    
