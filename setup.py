#  Copyright (c) 2016 DeKrijger Engineering
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.

#
#  setup.py      Setup script for py2exe.
#

from distutils.core import setup
import py2exe

my_files = [('.', ['ascii.png', 'cr.png', 'echo.png', 'hex.png',
                   'lf.png', 'mod.png', 'open.png', 'xor.png'])]

setup(
    options = {'py2exe': {'bundle_files': 2, 'compressed': True,
                          'dll_excludes': ['MSVCP90.dll', 'libiomp5md.dll',
                                           'libifcoremd.dll', 'libmmd.dll',
                                           'svml_dispmd.dll', 'libifportMD.dll']}},

    windows = ['bt3.py'],
    zipfile = None,
    data_files = my_files,
    )

