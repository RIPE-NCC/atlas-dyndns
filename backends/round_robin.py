import os

def round_robin(logger, data_dir, hostname):

    # check which af to use
    filename = None
    for af in ['4', '6']:
        try:
            os.stat(data_dir + '/' + hostname + '/v'+ af +'.txt')
            filename = data_dir + '/' + hostname + '/v'+ af +'.txt'
            if logger is not None:
                logger.info('Using {} for host {}'.format(filename, hostname))
        except OSError:
            pass

    # keep on yielding (None, None) if there are no input files at all
    if filename is None:
        if logger is not None:
            logger.error('Unable to load data for {}'.format(hostname))
        while True:
            yield(None)

    file_in = open(filename)
    last_mtime = os.stat(filename).st_mtime

    while True:
        try:
            # check if input was modified
            current_mtime = os.stat(filename).st_mtime
            if current_mtime != last_mtime:
                if logger is not None:
                    logger.info('Reloading data for {}'.format(hostname))
                file_in.close()
                file_in = open(filename)
                last_mtime = os.stat(filename).st_mtime

            # get next line
            line = file_in.readline().strip()
            if line == '':
                # reached the end
                if logger is not None:
                    logger.debug('Reached end of round for {}'.format(hostname))
                file_in.close()
                file_in = open(filename)
                line = file_in.readline().strip()
        except:
            # who knows what else might happen
            raise

        yield(line)
