#!/usr/bin/env python

from IPy import IP
import json
import sys


def process_prefix(prefix, a_or_aaaa):
    try:
        p = IP(prefix)
        if (a_or_aaaa == 'A' and p.prefixlen() <= 24) or \
                (a_or_aaaa == 'AAAA' and p.prefixlen() <= 48 and p.prefixlen() > 0 ):
            print("{}\t{}".format(a_or_aaaa, p[1]))
    except ValueError:
        pass
    except IndexError:
        pass

def process_prefixes(node, a_or_aaaa):
    for prefix in node:
        process_prefix(prefix, a_or_aaaa)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: create-routed-list.py <v4|v6>\n")
        sys.exit(1)

    af = sys.argv[1]
    a_or_aaaa = 'A'
    if af == 'v6':
        a_or_aaaa = 'AAAA'

    indata = json.load(sys.stdin)

    process_prefixes(indata["data"]["prefixes"][af]["originating"], a_or_aaaa)
    process_prefixes(indata["data"]["prefixes"][af]["transitting"], a_or_aaaa)
