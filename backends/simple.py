
def simple(logger, base_dir, hostname):

    while True:
        if hostname.endswith('4'):
            yield('127.0.0.1')
        else:
            yield('::1')
