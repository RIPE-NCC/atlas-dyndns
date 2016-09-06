import logging
from .version import __version__

logger = logging.getLogger('dyndns.pipe')


class PowerDNSPipe(object):
    def __init__(self, fdin, fdout):
        self.fdin = fdin
        self.fdout = fdout
        self.description = "PowerDNSPipe"
        self.version = __version__

    def dispatch(self):
        """
        The main loop
        """
        is_handshake_done = False
        while True:
            try:
                rawstr = self.fdin.readline()
            except AttributeError:
                logger.info("input data source must be an io stream")
                break

            if rawstr == '':
                logger.info("EOF detected. exiting")
                break


            try:
                rawstr = rawstr.rstrip()
                logger.debug("RAW  IN: %s", rawstr)
                query = rawstr.split('\t')
            except AttributeError:
                logger.info("Garbage on input <{}>".format(rawstr))
                self.reply_fail()
                continue

            if not is_handshake_done:
                # do handshake
                if query[0] == 'HELO':
                    self.reply_raw("OK\t{} {}".format(
                        self.description,
                        self.version
                    ), flush=True)
                    is_handshake_done = True
                    logger.info("Handshake OK. ABI-Version: {}".format(query[1]))
                else:
                    logger.error("Handshake error: <{}>".format(query))
                    self.reply_fail()
                continue

            # it should be a valid query here
            try:
                q, qname, qclass, qtype, qid, remote_ip = query
            except ValueError:
                logger.error(
                    "Doesn't look like a valid query <{}>".format(query)
                )
                self.reply_fail()
                continue

            self.handle_query(q, qname, qclass, qtype, qid, remote_ip)

    def reply_data(self, qname, qclass, qtype, ttl, id, content):
        data = ["DATA", qname, qclass, qtype, ttl, id, content]
        reply = "\t".join(map(str, data))
        self.reply_raw(reply) 

    def reply_end(self):
        self.reply_raw("END", flush=True)

    def reply_fail(self):
        self.reply_raw("FAIL", flush=True)

    def reply_raw(self, line, flush=False):
        logger.debug("RAW OUT: %s", line)
        if callable(self.fdout):
            self.fdout(line)
        else:
            self.fdout.write(line + "\n")
            if flush:
                self.fdout.flush()

    def handle_query(self, q, qname, qclass, qtype, qid, remote_ip):
        """
        Dummy method. must be overridden
        """
        self.reply_data(qname, qclass, qtype, 65535, qid, remote_ip)

