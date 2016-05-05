#!python3

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


#  bt3.py      Application module.
#
#  Typical use-case of Bt3 is debugging embedded projects by connecting to a
#  UART port and chatting directly in HEX by inputting escaped strings like
#  "\x00\x01" and viewing output in a typical hexdump format.
#
#  The ASCII mode shows lines of raw ASCII only, there is no terminal emulation.
#
#  Bt3 can append an 8-bit modulo or xor sum to each frame.
#  Bt3 can append CR+LF or one of both to each frame.

import time
import threading
import queue
import tkinter as tk
import serial
import serial.tools.list_ports

from termview import TermView
from support import *


class Terminal(object):
  def __init__(self):
    self._serial = serial.Serial()

    self.options = {'device': [],
                    'speed': self._serial.BAUDRATES,
                    'databits': self._serial.BYTESIZES,
                    'parity': self._serial.PARITIES,
                    'stopbits': self._serial.STOPBITS,
                    'flow': ['hardware', 'software', 'None']}

    self.settings = {'device': '',
                     'speed': 38400,
                     'databits': 8,
                     'parity': 'N',
                     'stopbits': 1,
                     'flow': 'None'}

    devices = [item for item in serial.tools.list_ports.comports()]
    if (devices):
      self.options['device'] = list([item[0] for item in devices])
      self.settings['device'] = self.options['device'][0]

    self.sum_type = 'mod'      # checksum type
    self.echo_enable = True    # enable local echo
    self.lf_enable = False     # add line feed
    self.cr_enable = False     # add carriage return
    self.status = Observable() # observe status msg
    self.echo = Observable()   # observe local echo
    self.connected = False     # status
    self.rxQ = queue.Queue()   # receive queue


  def listener(self):
    # listening thread
    self._serial.timeout = None
    while self.connected and self._serial.isOpen():
      cnt = self._serial.inWaiting()
      if cnt:
        self.rxQ.put(self._serial.read(cnt))
      time.sleep(0.01)

    self.connected = False


  def connect(self):
    self._serial.port =     self.settings['device']
    self._serial.baudrate = self.settings['speed']
    self._serial.bytesize = self.settings['databits']
    self._serial.parity =   self.settings['parity']
    self._serial.stopbits = self.settings['stopbits']
    # TODO flow control

    try:
      self._serial.open()
    except (serial.SerialException, ValueError) as ex:
      self.status.set('Error while connecting to %s:\n%s' % (self.settings['device'], str(ex)))
    else:
      if (self._serial.isOpen()):
        self.status.set('Connected to %s (%d/%d/%s/%d).' % (self.settings['device'],
                                                             self.settings['speed'],
                                                             self.settings['databits'],
                                                             self.settings['parity'],
                                                             self.settings['stopbits']))
        # start the listener
        self.rx_thd = threading.Thread(target=self.listener)
        self.rx_thd.setDaemon(True)
        self.connected = True
        self.rx_thd.start()
      else:
        self.status.set('Unable to open %s.' % self.settings['device'])

    return self.connected


  def disconnect(self):
    self.connected = False
    self.rx_thd.join()
    self._serial.close()
    self.status.set('Serial device closed.')


  def talk(self, line):
    if self.connected:
      b = [ord(i) for i in line]

      if self.cr_enable:
        b.append(0x0D)
      if self.lf_enable:
        b.append(0x0A)

      if self.sum_type == 'mod':
        b.append(sum_mod(b))
      elif self.sum_type == 'xor':
        b.append(sum_xor(b))

      if self.echo_enable:
        self.echo.set(bytes(b))

      self._serial.write(bytes(b))
    else:
      self.status.set('Not connected.')



class TermPresenter(object):
  def __init__(self, term, view, interactor):
    self.term = term
    self.view = view
    self.history = EntryHistory()

    # set the initial view state
    view.view_var.set('va_hex')

    view.toggle_echo.set(self.term.echo_enable)
    view.toggle_lf.set(self.term.lf_enable)
    view.toggle_cr.set(self.term.cr_enable)

    if self.term.sum_type == 'mod':
      view.toggle_mod.set(True)
    elif self.term.sum_type == 'xor':
      view.toggle_xor.set(True)

    view.cfg['port'].config(values=term.options['device'])
    view.port_set.set(term.settings['device'])

    view.cfg['baud'].config(values=term.options['speed'])
    view.baud_set.set(term.settings['speed'])

    view.cfg['bits'].config(values=term.options['databits'])
    view.bits_set.set(term.settings['databits'])

    view.cfg['pary'].config(values=term.options['parity'])
    view.pary_set.set(term.settings['parity'])

    view.cfg['stop'].config(values=term.options['stopbits'])
    view.stop_set.set(term.settings['stopbits'])

    # attach to model
    term.status.addCallback(self.on_status)
    term.echo.addCallback(self.on_echo)

    interactor.install(self, view)
    self.active= False


  def run(self, title=''):
    self.view.title(title)
    self.active = True
    self.view.mainloop()


  def set_cfg_enabled(self, enabled):
    for wgt in self.view.cfg:
      self.view.cfg[wgt].configure(state = 'normal' if enabled else 'disabled')


  def on_status(self, status):
    self.view.put_line('\n#STATUS: %s\n' % status, 'foreground_grn')


  def put_line(self, bytes_val, tag):
    if self.view.view_var.get() == 'va_hex':
      self.view.put_line(hex_dump(bytes_val), tag)
    else:
      try:
        self.view.put_line(bytes_val.decode('ascii'), tag)
      except UnicodeDecodeError as E:
        self.on_status(str(E))


  def on_update(self):
    try:
      bytes_val = self.term.rxQ.get_nowait()
    except queue.Empty:
      pass
    else:
      self.put_line(bytes_val, 'foreground_blk')


  def on_echo(self, bytes_val):
    self.put_line(bytes_val, 'foreground_red')


  def on_entry(self, entry):
    self.history.add(entry)
    try:
      self.term.talk(bytes(entry, 'ascii').decode('unicode_escape'))
    except UnicodeDecodeError as E:
      self.on_status(str(E))

  def on_entry_up(self):
    self.view.entry.delete(0, tk.END)
    self.view.entry.insert(0, self.history.previous())


  def on_entry_down(self):
    self.view.entry.delete(0, tk.END)
    self.view.entry.insert(0, self.history.next())


  def on_view(self, view_type):
    pass


  def on_lf(self, enabled):
    self.term.lf_enable = enabled


  def on_cr(self, enabled):
    self.term.cr_enable = enabled


  def on_echo_enable(self, enabled):
    self.term.echo_enable = enabled


  def on_connect(self, enabled):
    if self.active:
      self.active = False
      if enabled:
        self.term.settings['device'] = self.view.port_set.get()
        self.term.settings['speed'] = self.view.baud_set.get()
        self.term.settings['databits'] = self.view.bits_set.get()
        self.term.settings['parity'] = self.view.pary_set.get()
        self.term.settings['stopbits'] = self.view.stop_set.get()

        if not self.term.connect():
          self.view.toggle_open.set(False)
        else:
          self.set_cfg_enabled(False)
      else:
        self.term.disconnect()
        self.set_cfg_enabled(True)

      self.active = True


  def on_mod(self, enable):
    if self.active:
      if enable:
        self.active = False
        self.view.toggle_xor.set(False)
        self.active = True
        self.term.sum_type = 'mod'
      else:
        self.term.sum_type = None


  def on_xor(self, enable):
    if self.active:
      if enable:
        self.active = False
        self.view.toggle_mod.set(False)
        self.active = True
        self.term.sum_type = 'xor'
      else:
        self.term.sum_type = None



class TermInteractor(object):
  def __init__(self):
    pass

  def install(self, presenter, view):
    self.presenter = presenter
    self.view = view

    # key bindings
    view.entry.bind('<Key-Return>', self.on_enter)
    view.entry.bind('<Key-Up>', self.on_up)
    view.entry.bind('<Key-Down>', self.on_down)

    # variable bindings
    view.view_var.trace('w', self.on_view)
    view.toggle_lf.trace('w', self.on_lf)
    view.toggle_cr.trace('w', self.on_cr)
    view.toggle_echo.trace('w', self.on_echo)
    view.toggle_open.trace('w', self.on_open)
    view.toggle_mod.trace('w', self.on_mod)
    view.toggle_xor.trace('w', self.on_xor)

    # start update loop
    self.on_update()


  def on_update(self):
    self.presenter.on_update()
    self.view.after(1, self.on_update)

  def on_enter(self, *args):
    self.presenter.on_entry(self.view.entry.get())
    self.view.entry.delete(0, tk.END)

  def on_up(self, *args):
    self.presenter.on_entry_up()

  def on_down(self, *args):
    self.presenter.on_entry_down()

  def on_view(self, *args):
    self.presenter.on_view(self.view.view_var.get())

  def on_lf(self, *args):
    self.presenter.on_lf(self.view.toggle_lf.get())

  def on_cr(self, *args):
    self.presenter.on_cr(self.view.toggle_cr.get())

  def on_echo(self, *args):
    self.presenter.on_echo_enable(self.view.toggle_echo.get())

  def on_open(self, *args):
    self.presenter.on_connect(self.view.toggle_open.get())

  def on_mod(self, *args):
    self.presenter.on_mod(self.view.toggle_mod.get())

  def on_xor(self, *args):
    self.presenter.on_xor(self.view.toggle_xor.get())


def main():
  TermPresenter(Terminal(), TermView(), TermInteractor()).run(title='KE Software Bt3 Serial Terminal v1.0')


if __name__ == '__main__':
  main()

