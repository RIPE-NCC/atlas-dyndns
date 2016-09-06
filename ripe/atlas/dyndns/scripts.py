#!/usr/bin/env python
import os
import sys
import errno
import logging
import requests
import argparse
from IPy import IP
from random import shuffle
from StringIO import StringIO
from ConfigParser import ConfigParser
from .pdns_round_robin import PowerDNSRoundRobin
from .version import __version__


CONFIGS = [
    '/etc/atlas_dyndns.conf',
    '/usr/local/etc/atlas_dyndns.conf',
    os.path.expanduser('~/.atlas_dyndns.conf')
]


def get_resource(resource):
    url = "https://stat.ripe.net/data/ris-prefixes/data.json"
    r = requests.get(
        url,
        params=dict(
            resource=resource,
            list_prefixes="true"
        )
    )
    return r.json()


def get_routables(indata, af=4):
    _af = 'v' + str(af)

    prefixes = set()
    for t in ("originating", "transitting"):
        try:
            prefixes.update(indata["data"]["prefixes"][_af][t])
        except KeyError:
            continue

    addrs = set()
    for prefix in prefixes:
        try:
            p = IP(prefix)
            plen = p.prefixlen()
            if (
                af == 4 and plen < 24 or
                af == 6 and 0 < plen <= 48
            ):
                addrs.add(p[1].strCompressed())

        except (ValueError, IndexError):
            continue

    return addrs


def mkpath(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_routed_list_main():
    parser = argparse.ArgumentParser(
        description='Creates a routable list using RIPE Stat'
    )
    parser.add_argument(
        "-d", "--data-path",
        action="store", dest='data_path',
        default="data",
        help="path to directory where the data is stored"
    )
    parser.add_argument(
        "-r", "--resource",
        action="store", dest='resource',
        help="Resource: eg ASn"
    )
    parser.add_argument(
        "-n", "--host-name",
        action="store", dest='hostname',
        help="host name to associate with"
    )
    parser.add_argument(
        "-4", "--only-v4",
        action="append_const", const=4, dest='af',
        help="Get only v4 addresses"
    )
    parser.add_argument(
        "-6", "--only-v6",
        action="append_const", const=6, dest='af',
        help="Get only v6 addresses"
    )
    parser.add_argument(
        "--min-v4",
        action="store", type=int, dest='minv4',
        default=1,
        help=(
            "Create/overwrite files only if the number "
            "of v4 records is greater than this value"
        )
    )
    parser.add_argument(
        "--min-v6",
        action="store", type=int, dest='minv6',
        default=1,
        help=(
            "Create/overwrite files only if the number "
            "of v6 records is greater than this value"
        )
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ' + __version__
    )
    args = parser.parse_args()

    if None in (args.hostname, args.resource):
        print >>sys.stderr, "Host name and resource must be specified"
        return

    afs = args.af or [4, 6]

    data = get_resource(args.resource)
    for af in afs:
        rectype, minlen = ("AAAA", args.minv6) if af == 6 else ("A", args.minv4)

        addrs = list(get_routables(data, af))
        addrslen = len(addrs)

        if addrslen < minlen:
            print >>sys.stderr, (
                "Number of {} records ({}) "
                "is lower than threshold {}"
            ).format(rectype, addrslen, minlen)
            continue

        hostpath = os.path.join(args.data_path, args.hostname + str(af))
        mkpath(hostpath)

        filename = os.path.join(hostpath, "v{}.txt".format(af))
        with open(filename, "wt") as fh:
            shuffle(addrs)
            for addr in addrs:
                print >>fh, "\t".join([rectype, addr])


SAMPLE_CONFIG = """# This is a sample config file
#

[main]
# where the log files will be written
log_dir = /tmp

# main log file
log_file = %(log_dir)s/atlas-dyndns.log

# log level (DEBUG/INFO/WARN/ERROR)
loglevel=INFO

# logfiles - counters for munin
count4_file = %(log_dir)s/count4.log
count6_file = %(log_dir)s/count6.log
countx_file = %(log_dir)s/countx.log

# directory where are the host files located
data_dir=data

# TTL settings
ttl=0
soa_ttl=21600
ns_ttl=21600

# our zone
domain=dyndns.example.net

# SOA contents for our zone
soa:
    %(domain)s root.%(domain)s
    2010103101
    1800
    3600
    604800
    3600

# NS servers for our zone
ns_set:
    ns1.example.net
    ns1.example.net

# end of a sample config file
"""

SAMPLE_CONFIG_PDNS = """# This is a sample PowerDNS config file
# for atlas-dyndns services

out-of-zone-additional-processing=no
launch=pipe
pipe-timeout=5000
pipe-regex=dyndns[0-9]?.atlas.ripe.net;(A|AAAA|SOA|ANY|NS)$
pipe-command={pipe_command} --config /path/to/config
setuid=atlas
setgid=atlas
distributor-threads=1
local-ipv6=::
# end of a sample config file
"""


def get_config(config_files):
    cp = ConfigParser()
    cp.readfp(StringIO(SAMPLE_CONFIG))
    cp.read(config_files)
    config = {}
    for name, value in cp.items("main"):
        if name == "soa":
            config[name] = "\t".join(value.split())

        elif name == "ns_set":
            config[name] = value.replace(',', ' ').split()

        else:
            config[name] = value

    return config


def setup_logging(config):
    loglevel = config['loglevel'].upper()
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(loglevel))

    logger = logging.getLogger('dyndns')
    logger.setLevel(numeric_level)
    formatter = logging.Formatter(
        "%(asctime)s %(process)d %(levelname)s %(message)s"
    )
    handler = logging.handlers.WatchedFileHandler(config['log_file'])
    handler.setLevel(numeric_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    c4_handler = logging.handlers.WatchedFileHandler(config['count4_file'])
    c4_logger = logging.getLogger('count4')
    c4_logger.addHandler(c4_handler)

    c6_handler = logging.handlers.WatchedFileHandler(config['count6_file'])
    c6_logger = logging.getLogger('count6')
    c6_logger.addHandler(c6_handler)

    cx_handler = logging.handlers.WatchedFileHandler(config['countx_file'])
    cx_logger = logging.getLogger('countx')
    cx_logger.addHandler(cx_handler)


def atlas_pdns_pipe_main():
    parser = argparse.ArgumentParser(
        description='PowerDNS pipe roundrobin backend'
    )
    parser.add_argument(
        "-c", "--config",
        action="store", dest='config',
        help="config file"
    )
    parser.add_argument(
        "--dump-config",
        action="store_true", dest='dumpconfig',
        help="dump current settings"
    )
    parser.add_argument(
        "--sample-config",
        action="store_true", dest='genconfig',
        help="generate a sample config file"
    )
    parser.add_argument(
        "--sample-config-pdns",
        action="store_true", dest='genconfig_pdns',
        help="generate a sample PowerDNS config file"
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ' + __version__
    )

    args = parser.parse_args()
    if args.genconfig:
        print SAMPLE_CONFIG
        return

    if args.genconfig_pdns:
        print SAMPLE_CONFIG_PDNS.format(pipe_command=sys.argv[0])
        return

    config_files = args.config and [args.config] or CONFIGS
    if not any([os.path.isfile(cfn) for cfn in config_files]):
        print >>sys.stderr, (
            "No configs found. Using internal defaults. "
            "Use --sample-config to generate a sample config"
        )

    config = get_config(config_files)

    if args.dumpconfig:
        for name, value in config.items():
            print '{} = "{}"'.format(name, value)
        return

    setup_logging(config)

    PowerDNSRoundRobin(sys.stdin, sys.stdout, **config).dispatch()
