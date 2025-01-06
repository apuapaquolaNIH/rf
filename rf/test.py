#!/usr/bin/env python
""" rf - A minimalist framework for reproducible computation

    Copyright (C) 2025 Apuã Paquola <apua.paquola@nih.gov>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import tempfile
import os
import base64
import subprocess
from argparse import Namespace
import rflib


__author__ = 'Apuã Paquola'


class UnitTests(unittest.TestCase):

    @staticmethod
    def write_dummy_tree_and_init_git():
        """Creates dummy analysis tree and inits the git repo. It cds to 'dummy' """
        with open("dummy.tar.gz", "wb") as f:
            f.write(base64.b64decode(
                b'''H4sIAAAAAAAAA+2dzW7TQBSFs66EeAIkI/bJnf94USRKK5UNKgt2SJWTWDQSSUp+pLLjSXkANrwC9pg2ZuKocWqPk/p8quR24mimnZxz51573Kvo7jKORvG8N1pNJj86dUBERqmgYyzrI90jZcC4EUpw0smJxAwn2QnuahmNw2qxjObJUG6j76vZtygabjnv44fLL+ezSTSeBp8X8Xzhvp79JsHD8Uhg/eDreHTKhKa+ChmTJ0nLKm3pS8F1yEicND1GUB9W9b16+7jX/8/k+8mvF3/S46dXL3/TGkf/mkvWCVS9w8pouf6z+b96iALT2Sh+V3Efj/k/Ix4waYQhoY3mAXHiAv7vhV38X1AwWY4n8SkzQrNQKUPdUCgtQ8UNosNRk+nfqr62KLCT/+f1n6z/jIb/+6DI/y8q7qOU/xtt/V8q+L8P9vL/Pu+K5EWuRcjg/0fN2v8vDsP/U/0nnzMy8H8fFPn/WcV9lPB/Q6Ss/3Os/72wn/+HXUb9UFMYojp03Kz9/+wQ/D/Tf7L+11j/eyE//+socL3tr7AXj/m/rf8L0kZpJZj1f80M/N8HqP+3m7z+r4f1hICd/D+vf2a0kvB/HxT7f/rz+8r6KLX+TxabxBlXHP7vg33W/8mpXcZIhTx5D6LDUZPXv1V9DSGg1Prf6p8Eg/97Ybv/n1fWRzn/N9b/NfzfC3v5P1PdvtIh54Jw/fe4cf3/vHH/N9b/OfzfC5vzX30VqHz9h2lF8H8foP7Tbjb1X30VqHT9h5MhBf/3QeH8r0PAfDV9eh87+b+9/5eS9C/N/3jiPfB/H8D/202h/itR/ZpH/d8oR/9Mptf/qMpBbKPl+n/zujcYT3uLm5N4eDMLRix4GyxYd3m3/NfA0waeaxBpg7ANTQ8ePJnN+u9h5H8S1/+9gPjfbjb1fyD5H+p/Xiic/wbzP273/3EpUf/zAvy/3RTqv8H8L9M/k1wh//OBk/8N3fxv6OZ/Q+R/zwnn/s+KI39GmfjPDLP6J+R/XkD8bzeO/iuO/Bll4n+mfxJGIv77wIn/Azf+D9z4P0D8f07k938f0v4vjuu/XkD8bzd5/R/U/i88/8ELzvyvQ8Aovq2qj53zP26SD4FI8z9hBPzfB/D/duPoP1F99TFgJ///T/8kBcH/fbDV/xuq/wkms/u/GPzfB/D/duPov/H6X6Z/EunzP1H/qx+n/he79b/Yrf/FqP89JwrWf5VvAy+f/3GJ5//5AfG/3RTov9qHP3T2yf+k/f8PvNvtZV+5/SlVDiyl5frPP//9kK7/MA3/9wH8v93k9X9Q138E6n8+cOa/8fpf+iwoe/8f7v/3Avy/3Tj6b7z+l+mfhMb9/15w6n+RW/+L3PpfhPofAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABN8ReUqGPUAKAAAA==
'''))
        subprocess.check_call(['tar', 'xfz', 'dummy.tar.gz'])
        os.chdir('dummy')
        #subprocess.check_call(['git', 'init'])
        #subprocess.check_call(['git', 'annex', 'init'])

    def skel_test_run(self):
        """Create dummy analysis tree, run driver scripts and check output"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            try:
                print('NAME', __name__)
                cur_dir = os.getcwd()
                os.chdir(tmpdirname)

                self.write_dummy_tree_and_init_git()

                rflib.run(Namespace(node='.', recursive=True, verbose=True, dry_run=False))

                command = '''export LC_ALL=C; find . -name '*.txt' | sort | md5sum'''
                o = subprocess.check_output(command, shell=True).decode()
                self.assertTrue(o.startswith('873a9c2d4a56e62c7afd955057e54ac1'))

                command = '''export LC_ALL=C; cat `find . -name '*.txt'` | sort | md5sum'''
                o = subprocess.check_output(command, shell=True).decode()
                self.assertTrue(o.startswith('43682754c874d40b3667b2c7c7dc0e65'))

            finally:
                os.chdir(cur_dir)

    def test_run_native(self):
        """Runs a test tree natively"""
        self.skel_test_run()

