import os
import logging

logger = logging.getLogger('dyndns.roundrobin_file')


class RoundRobinFile(object):
    def __init__(self):
        self._fh_cache = dict()

    def get_record(self, filename):
        fh = self.get_filehandle(filename)

        if fh is None:
            return None

        # read the line in round-robin fashion
        try:
            line = fh.next()
        except StopIteration:
            logger.debug('Reached end of round for {}'.format(fh.name))
            fh.seek(0)
            try:
                line = fh.next()
            except StopIteration:
                return None

        return line.strip()

    def open_file(self, filename):
        """
        Open and cache the file
        """
        try:
            fh = open(filename, "rt")
        except (TypeError, IOError):
            # cache even if the file cannot be open
            logger.error('Unable to open {}'.format(filename))
            self._fh_cache[filename] = (None, ())
            return None

        stat = os.stat(filename)
        self._fh_cache[filename] = (fh, (stat.st_mtime, stat.st_ino))
        return fh

    def get_filehandle(self, filename):
        try:
            fh, stat_cached = self._fh_cache[filename]
        except KeyError:
            # no file in the cache. try to open and cache it
            return self.open_file(filename)

        if fh is None:
            # negative caching is in progress
            return None

        try:
            stat = os.stat(filename)
        except (TypeError, OSError):
            # file is missing - switch to negative caching
            self._fh_cache[filename] = (None, ())
            return None

        if stat_cached != (stat.st_mtime, stat.st_ino):
            # file is updated - reopen and cache it
            logger.info('Reloading data from {}'.format(filename))
            fh.close()
            return self.open_file(filename)

        return fh
