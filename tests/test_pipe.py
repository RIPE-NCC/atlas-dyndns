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

import StringIO
from unittest import TestCase

from ripe.atlas.dyndns.pipe import PowerDNSPipe
from ripe.atlas.dyndns.version import __version__


class TestPowerDNSPipe(TestCase):
    def test_reply(self):
        fdin = StringIO.StringIO()
        fdout = StringIO.StringIO()
        p = PowerDNSPipe(fdin, fdout)
        p.reply_data(
            "host1.domain.tld",
            "IN", "MX",
            3600, "5",
            "relay.domain.tld"
        )
        self.assertEqual(
            fdout.getvalue(),
            "DATA\thost1.domain.tld\tIN\tMX\t3600\t5\trelay.domain.tld\n"
        )

    def test_end(self):
        fdin = StringIO.StringIO()
        fdout = StringIO.StringIO()
        PowerDNSPipe(fdin, fdout).reply_end()
        self.assertEqual(
            fdout.getvalue(),
            "END\n"
        )

    def test_fail(self):
        fdin = StringIO.StringIO()
        fdout = StringIO.StringIO()
        PowerDNSPipe(fdin, fdout).reply_fail()
        self.assertEqual(
            fdout.getvalue(),
            "FAIL\n"
        )

    def test_pipe_chat(self):
        requests = (
            "HELO\t1\n"
            "Q\thost1.domain.tld\tIN\tSOA\t-1\t127.0.0.1\n"
            "Q\thost2.domain.tld\tIN\tANY\t1\t127.0.0.1\n"
        )

        responces = (
            "OK\tPowerDNSPipe {}\n"
            "DATA\thost1.domain.tld\tIN\tSOA\t65535\t-1\t127.0.0.1\n"
            "DATA\thost2.domain.tld\tIN\tANY\t65535\t1\t127.0.0.1\n"
        ).format(__version__)

        fdin = StringIO.StringIO(requests)
        fdout = StringIO.StringIO()

        PowerDNSPipe(fdin, fdout).dispatch()
        self.assertEqual(fdout.getvalue(), responces)

    def test_pipe_chat_bad(self):
        requests = (
            "HELO\t1\n"
            "host1.domain.tld\tIN\tSOA\t-1\t127.0.0.1\n"
        )

        responces = (
            "OK\tPowerDNSPipe {}\n"
            "FAIL\n"
        ).format(__version__)

        fdin = StringIO.StringIO(requests)
        fdout = StringIO.StringIO()

        PowerDNSPipe(fdin, fdout).dispatch()
        self.assertEqual(fdout.getvalue(), responces)
