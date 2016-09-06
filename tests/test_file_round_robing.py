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
from unittest import TestCase
from ripe.atlas.dyndns.backends.round_robin import RoundRobinFile

data_path = os.path.join(os.path.dirname(__file__), "data")


class TestRoundRobin(TestCase):
    def get_filename(self, hostname):
        af = int(hostname[-1])
        return os.path.join(
            data_path,
            hostname,
            'v{}.txt'.format(af)
        )

    def test_file_open(self):

        r = RoundRobinFile()

        filename4 = self.get_filename("host4")
        filename6 = self.get_filename("host6")

        # valid file handles must be present
        fh_a = r.get_filehandle(filename4)
        self.assertIsInstance(fh_a, file)

        fh_aaaa = r.get_filehandle(filename6)
        self.assertIsInstance(fh_aaaa, file)

        # touch file, it must force reopening
        os.utime(filename4, None)
        fh_a_new = r.get_filehandle(filename4)
        self.assertNotEqual(fh_a, fh_a_new)

        # AAAA file must be left untouched
        fh = r.get_filehandle(filename6)
        self.assertEqual(fh_aaaa, fh)

        # check negative caching
        filename = self.get_filename("missing6")
        fh = r.get_filehandle(filename)
        self.assertIsNone(r._fh_cache[filename][0])

    def test_rount_robin(self):
        r = RoundRobinFile()
        filename4 = self.get_filename("host4")
        filename6 = self.get_filename("host6")

        resp = r.get_record(filename4).split(None, 1)
        self.assertEqual(resp, ['A', '8.8.8.8'])
        resp = r.get_record(filename6).split(None, 1)
        self.assertEqual(resp, ['AAAA', '1::1'])
        resp = r.get_record(filename4).split(None, 1)
        self.assertEqual(resp, ['A', '8.8.4.4'])
        resp = r.get_record(filename6).split(None, 1)
        self.assertEqual(resp, ['AAAA', '2::2'])
        resp = r.get_record(filename4).split(None, 1)
        self.assertEqual(resp, ['A', '8.8.8.8'])
        resp = r.get_record(filename6).split(None, 1)
        self.assertEqual(resp, ['AAAA', '1::1'])
