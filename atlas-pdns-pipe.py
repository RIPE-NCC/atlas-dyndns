#!/usr/bin/env python

"""
    See https://docs.powerdns.com/md/authoritative/backend-pipe/
    for the powerdns pipe protocol description
"""

import re
import sys
import logging
import logging.handlers
import traceback
import backends


DESCR = "atlas-dyndns"
VERSION = "0.2.2"
DATA_TEMPLATE = "DATA\t{}\t{}\t{}\t{}\t{}\t{}\n"
hosts = {}
protocol_version = None

from settings import *
try:
    from settings_local import *
except:
    pass


def handle_query(qname, qclass, qtype, qid, remote_ip):
    global zone_re

    hostname = qname.lower()

    if hostname[-1] == '.':
        hostname = hostname[:-1]

    # SOA
    if qtype == 'SOA':
        response = DATA_TEMPLATE.format(qname, qclass, 'SOA', TTL, qid, SOA)
        sys.stdout.write(response)
        sys.stdout.write('END\n')

    # A or AAAA or ANY matching the domain
    elif (qtype == 'A' or qtype == 'AAAA' or qtype == 'ANY') and hostname.endswith(DOMAIN):
        hostname = re.sub(zone_re,'',hostname)

        if hostname == 'dyndns.atlas.ripe.net':
            # original query was actually an NS
            for ns in NSSET:
                response = DATA_TEMPLATE.format(qname, qclass, 'NS', NS_TTL, qid, ns)
                sys.stdout.write(response)
                logger.info("IP: {} Q: '{} {}' A: 'NS {}'".format(remote_ip, qtype, hostname, ns))

        else:

            # check if we already have a handler
            if hostname not in hosts:
                logger.debug("Installing handler for {}".format(hostname))
                hosts[hostname] = backends.round_robin(logger, DATA_DIR, hostname)

            next = hosts[hostname].next()
            try:
                (type, answer) = next.split('\t')
            except (ValueError, AttributeError):
                logger.error("Syntax error in datafile for {}: {}".format(hostname, next))
                type = None

            # type is None if there's no backend data
            if type is not None:
                qtype = type
                logger.info("IP: {} Q: '{} {}' A: '{} {}'".format(remote_ip, qtype, hostname, type, answer))
                response = DATA_TEMPLATE.format(qname, qclass, qtype, TTL, qid, answer)
                sys.stdout.write(response)
            else:
                # there's no point in keeping a non-functioning backend installed
                # besides, this way it may be reinstalled with actual data later
                del hosts[hostname]

        sys.stdout.write('END\n')

        if hostname.endswith('4'):
            c4_logger.error('')
        elif hostname.endswith('6'):
            c6_logger.error('')
        else:
            cx_logger.error('')

    else:
        logger.error('FAIL for {} {}'.format(qname, qtype))
        sys.stdout.write('FAIL\n')

    sys.stdout.flush()


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('main')
    logger.setLevel(LOGLEVEL)

    formatter = logging.Formatter("%(asctime)s %(process)d %(levelname)s %(message)s")
    handler = logging.handlers.WatchedFileHandler(LOG_FILE)
    handler.setLevel(LOGLEVEL)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    c4_handler = logging.handlers.WatchedFileHandler(COUNT4_FILE)
    c4_logger = logging.getLogger('count4')
    c4_logger.addHandler(c4_handler)
    c6_handler = logging.handlers.WatchedFileHandler(COUNT6_FILE)
    c6_logger = logging.getLogger('count6')
    c6_logger.addHandler(c6_handler)
    cx_handler = logging.handlers.WatchedFileHandler(COUNTX_FILE)
    cx_logger = logging.getLogger('countx')
    cx_logger.addHandler(cx_handler)

    global zone_re
    zone_re = re.compile('.dyndns\d?'+DOMAIN)

    # begin protocol
    line = sys.stdin.readline()
    (helo, protocol_version) = line.split('\t')
    if helo != 'HELO':
        logger.info("Protocol error: '{}'".format(line))
        exit
    protocol_version = int(protocol_version)
    logger.info("New backend thread with protocol version {}".format(protocol_version))
    sys.stdout.write('OK\t{} {}\n'.format(DESCR, VERSION))
    sys.stdout.flush()

    # normally the script should not terminate
    while True:
        query = sys.stdin.readline().strip()
        logger.debug("Query: '{}'".format(query))

        q, qname, qclass, qtype, qid, remote_ip = query.split('\t')

        try:
            handle_query(qname, qclass, qtype, qid, remote_ip)
        except:
            logger.error(traceback.format_exc())

    # never get here
    logger.info("Exiting")
