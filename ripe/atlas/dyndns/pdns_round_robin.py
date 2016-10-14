import os
import re
import logging
import logging.handlers

from backends.round_robin import RoundRobinFile
from .pipe import PowerDNSPipe
from .version import __version__

logger = logging.getLogger('dyndns.pdns_roundrobin')
c4_logger = logging.getLogger('count4')
c6_logger = logging.getLogger('count6')
cx_logger = logging.getLogger('countx')


class PowerDNSRoundRobin(PowerDNSPipe, RoundRobinFile):
    description = "atlas-dyndns"
    version = __version__

    def __init__(self, fdin, fdout, **config):
        for name, value in config.items():
            setattr(self, name, value)

        self.check_re = None
        if "regexp_check" in config:
            self.check_re = re.compile(config["regexp_check"])

        PowerDNSPipe.__init__(self, fdin, fdout)
        RoundRobinFile.__init__(self)

    def handle_query(self, q, qname, qclass, qtype, qid, remote_ip):
        logger.debug([q, qname, qclass, qtype, qid, remote_ip])

        if q != 'Q':
            self.reply_end()
            return

        if self.check_re is not None and not self.check_re.match(qname):
            self.reply_end()
            return

        _qname = qname.lower()
        if _qname[-1] == '.':
            _qname = _qname[:-1]

        # qname is always fdqn in our case. if not do not reply.
        if not _qname.endswith(self.domain):
            self.reply_end()
            return

        # get hostname part
        hostname = _qname.replace(self.domain, '')
        if hostname and hostname[-1] == '.':
            hostname = hostname[:-1]

        # SOA
        if qtype == 'SOA':
            # if query is SOA return myzone SOA
            self.reply_data(
                self.domain, qclass, qtype, self.soa_ttl, qid, self.soa
            )
            self.reply_end()
            return

        # does PowerDNS really send 'A', 'AAAA'?
        elif qtype in ('ANY', 'A', 'AAAA'):
            if hostname == '':
                # most likely it is a NS query
                # if it is wrong the server will pass it out
                for ns in self.ns_set:
                    self.reply_data(
                        self.domain, qclass, 'NS', self.ns_ttl, qid, ns
                    )

                cx_logger.error('')

            elif hostname[-1] in ('4', '6'):
                # it is definitely an A/AAAA request
                record = self.get_roundrobin(hostname)
                if record is not None:
                    qtype, content = record.split(None, 1)
                    self.reply_data(
                        qname, qclass, qtype, self.ttl, qid, content
                    )

                    if hostname[-1] == '4':
                        c4_logger.error('')
                    elif hostname[-1] == '6':
                        c6_logger.error('')
            else:
                cx_logger.error('')

            self.reply_end()

        else:
            logger.error('FAIL for {} {}'.format(qname, qtype))
            self.reply_fail()

    host_re = re.compile(r'[^a-z0-9-]', re.IGNORECASE)

    def get_roundrobin(self, hostname):
        if self.host_re.search(hostname):
            return None

        try:
            af = int(hostname[-1])
            if af not in (4, 6):
                raise ValueError()
        except (ValueError, TypeError):
            return None

        filename = os.path.join(
            self.data_dir,
            hostname,
            'v{}.txt'.format(af)
        )

        return self.get_record(filename)
