# Copyright (c) 2015 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import StringIO
from unittest import TestCase

from ripe.atlas.dyndns.pdns_round_robin import PowerDNSRoundRobin
from ripe.atlas.dyndns.scripts import get_config

data_dir = os.path.join(os.path.dirname(__file__), "data")
config_file = os.path.join(os.path.dirname(__file__), "dyndns.conf")


class TestPowerDNSPipe(TestCase):
    def setUp(self):
        self.fdin = StringIO.StringIO()
        self.fdout = StringIO.StringIO()
        config = get_config(config_file)
        self.pdns = PowerDNSRoundRobin(self.fdin, self.fdout, **config)
        self.pdns.data_dir = data_dir

    def get_response(self):
        return self.fdout.getvalue().strip().split('\n')

    def test_handle_soa(self):
        ar = ['Q', 'host4.dyndns.example.net', 'IN', 'SOA', '-1', '127.0.0.1']
        self.pdns.handle_query(*ar)
        self.assertListEqual(
            self.get_response(),
            [
                "DATA\tdyndns.example.net\tIN\tSOA\t{}\t-1\t{}".format(
                    self.pdns.soa_ttl,
                    self.pdns.soa
                ),
                'END'
            ]
        )

    def test_handle_ns(self):
        ar = ['Q', 'dyndns.example.net', 'IN', 'ANY', '-1', '127.0.0.1']
        self.pdns.handle_query(*ar)
        self.assertListEqual(
            self.get_response(),
            [
                'DATA\tdyndns.example.net\tIN\tNS\t21600\t-1\tns1.example.net',
                'DATA\tdyndns.example.net\tIN\tNS\t21600\t-1\tns2.example.net',
                'END'
            ]
        )

    def test_handle_a(self):
        ar = ['Q', 'host4.dyndns.example.net', 'IN', 'ANY', '-1', '127.0.0.1']
        self.pdns.handle_query(*ar)
        self.assertListEqual(
            self.get_response(),
            ['DATA\thost4.dyndns.example.net\tIN\tA\t0\t-1\t8.8.8.8', 'END']
        )

    def test_handle_aaaa(self):
        ar = ['Q', 'host6.dyndns.example.net', 'IN', 'ANY', '-1', '127.0.0.1']
        self.pdns.handle_query(*ar)
        self.assertListEqual(
            self.get_response(),
            [
                'DATA\thost6.dyndns.example.net\tIN\tAAAA\t0\t-1\t1::1',
                'END'
            ]
        )
