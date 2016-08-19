#!/usr/bin/env python

import backends
import sys


if __name__ == '__main__':

    r4 = backends.round_robin(None, ".", 'test4')
    r6 = backends.round_robin(None, ".", 'test6')
    #r4 = backends.simple(None, config, 'test4')
    #r6 = backends.simple(None, config, 'test6')

    for i in range(0,10):
        print(r4.next())
        print(r6.next())
        sys.stdin.readline()
