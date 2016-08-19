
# you very likely want to tweak these to match your needs

LOG_BASE = "/tmp/"
LOG_FILE = LOG_BASE+"atlas-dyndns.log"
COUNTX_FILE = LOG_BASE+"count.log"
COUNT4_FILE = LOG_BASE+"count4.log"
COUNT6_FILE = LOG_BASE+"count6.log"
TTL = '0'
NS_TTL = 6*60*60
NSSET = []
LOGLEVEL = "INFO"
DOMAIN = ".example.net"
SOA = "dyndns.example.net\troot.dyndns.example.net\t2010103101\t1800\t3600\t604800\t3600"
DATA_DIR = "/tmp"
