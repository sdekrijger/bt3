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
import time

class Observable(object):
  """Observable - An observable data type.

     When pickling this the callback functions are not pickled
     to prevent unpickleable objects to be pulled along with
     it. After unpickling all callbacks need to be re-attached.
  """
  def __init__(self, initialValue=None):
    """Instantiate an observable variable with initialValue."""
    self.data = initialValue
    self.callbacks = {}

  def __getstate__(self):
    return {'data': self.data, 'callbacks': {}}

  def __setstate__(self, d):
    self.__dict__ = d

  def addCallback(self, func):
    """Add a callback to the variable."""
    self.callbacks[func] = 1

  def delCallback(self, func):
    """Remove callback from variable."""
    if func in self.callbacks:
      del self.callbacks[func]

  def _docallbacks(self):
    for func in self.callbacks:
      func(self.data)

  def set(self, data):
    """Set variable to new value."""
    self.data = data
    self._docallbacks()

  def get(self):
    """Get variable value."""
    return self.data

  def unset(self):
    """Set variable to None."""
    self.data = None


class EntryHistory(object):

  def __init__(self):
    self.history = ['']
    self.index = 0

  def add(self, entry):
    self.history.append(entry)
    self.index = len(self.history)

  def previous(self):
    if (self.index > 0):
      self.index -= 1
    return self.history[self.index]

  def next(self):
    if self.index < (len(self.history) - 1):
      self.index += 1
    return self.history[self.index]

  def last(self):
    if self.index > 0:
      return self.history[-1]
    else:
      return ''



def achr(n):
  # return chr(n) if displayable ascii, '.' otherwise.
  if 32 < n < 126:
    c = chr(n)
  else:
    c = '.'
  return c


def hex_dump(bytes_val):
  # return \n separated lines hexdump (index word + 16 data bytes + ascii column) of bytes
  hex_val = [bytes_val[i:i+16] for i in range(0, len(bytes_val), 16)]

  cnt = 0
  dump = []
  for row in hex_val:
    dump.append('%04X  %s%s\n' % (cnt, ''.join(['%02X '% x for x in row]).strip().ljust(56), ''.join([achr(c) for c in row])))
    cnt = cnt + 16

  return ''.join(dump)


def sum_mod(bytes_val):
  # return 2's complement (modulo) checksum of bytes
  d = (255 - (sum(bytes_val) % 256)) + 1
  if (d > 255):
      d = 0
  return d


def sum_xor(bytes_val):
  # return xor sum of bytes
  x = 0
  for b in bytes_val:
    x = x ^ b
  return x


def get_timecode():
  t = time.gmtime()
  return '%04d%02d%02dT%02d%02d%02dZ' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


