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
# termview.py     tkinter GUI for Bt3
#

import tkinter as tk
from tkinter import ttk, font
from PIL import ImageTk, Image


class TermView(ttk.tkinter.Tk):
  def __init__(self, *args, **kwargs):
    ttk.tkinter.Tk.__init__(self, *args, **kwargs)
    self._init_gui()


  def put_line(self, line, tag):
    self.output_text.insert('end', line, tag)
    self.output_text.see(tk.END)


  def _init_gui(self):
    self.resizable(width=False, height=True)

    self.view_var = tk.StringVar()
    self.toggle_lf = tk.BooleanVar()
    self.toggle_cr = tk.BooleanVar()
    self.toggle_echo = tk.BooleanVar()
    self.toggle_open = tk.BooleanVar()
    self.toggle_mod = tk.BooleanVar()
    self.toggle_xor = tk.BooleanVar()
    self.toggle_rep = tk.BooleanVar()
    self.toggle_time = tk.BooleanVar()
    self.port_set = tk.StringVar()
    self.baud_set = tk.IntVar()
    self.bits_set = tk.IntVar()
    self.pary_set = tk.StringVar()
    self.stop_set = tk.DoubleVar()

    # Toolbar
    self.toolbar = ttk.Frame(self)

    self.open_ico = ImageTk.PhotoImage(Image.open('open.png'))
    self.open_btn = tk.Checkbutton(self.toolbar, indicatoron=0,
                                     overrelief=tk.GROOVE, offrelief=tk.FLAT,
                                     width=32, height=32,
                                     image=self.open_ico,
                                     variable=self.toggle_open)

    self.clr_ico = ImageTk.PhotoImage(Image.open('clr.png'))
    self.clr_btn = tk.Button(self.toolbar, overrelief=tk.GROOVE, relief=tk.FLAT,
                             width=32, height=32,
                             image=self.clr_ico)

    self.cmd_ico = ImageTk.PhotoImage(Image.open('cmd.png'))
    self.cmd_btn = tk.Button(self.toolbar, overrelief=tk.GROOVE, relief=tk.FLAT,
                             width=32, height=32,
                             image=self.cmd_ico)


    self.btn = ({'img': ImageTk.PhotoImage(Image.open('ascii.png')), 'var': self.view_var,    'val': 'va_asc', },
                {'img': ImageTk.PhotoImage(Image.open('hex.png')),   'var': self.view_var,    'val': 'va_hex', },
                {'img': ImageTk.PhotoImage(Image.open('rep.png')),   'var': self.toggle_rep,                   },
                {'img': ImageTk.PhotoImage(Image.open('xor.png')),   'var': self.toggle_xor,                   },
                {'img': ImageTk.PhotoImage(Image.open('mod.png')),   'var': self.toggle_mod,                   },
                {'img': ImageTk.PhotoImage(Image.open('echo.png')),  'var': self.toggle_echo,                  },
                {'img': ImageTk.PhotoImage(Image.open('lf.png')),    'var': self.toggle_lf,                    },
                {'img': ImageTk.PhotoImage(Image.open('cr.png')),    'var': self.toggle_cr,                    },
                {'img': ImageTk.PhotoImage(Image.open('time.png')),  'var': self.toggle_time,                  })

    for b in self.btn:
      if 'cmd' in b:
        wgt = tk.Button(self.toolbar,
                             overrelief=tk.GROOVE, relief=tk.FLAT,
                             width=32, height=32,
                             image=b['img'],
                             command=b['cmd'])


      elif not 'val' in b:
        wgt = tk.Checkbutton(self.toolbar, indicatoron=0,
                                  overrelief=tk.GROOVE, offrelief=tk.FLAT,
                                  width=32, height=32,
                                  image=b['img'],
                                  variable=b['var'])
      else:
        wgt = tk.Radiobutton(self.toolbar, indicatoron=0,
                                  overrelief=tk.GROOVE, offrelief=tk.FLAT,
                                  width=32, height=32,
                                  image=b['img'],
                                  variable=b['var'],
                                  value=b['val'])

      wgt.pack(side=tk.RIGHT, padx=2, pady=2)

    self.open_btn.pack(side=tk.LEFT, padx=2, pady=2)
    self.clr_btn.pack(side=tk.LEFT, padx=2, pady=2)
    self.cmd_btn.pack(side=tk.LEFT, padx=2, pady=2)


    self.cfg = {'port': ttk.Combobox(self.toolbar, textvariable=self.port_set, values=[], width=8),
                'baud': ttk.Combobox(self.toolbar, textvariable=self.baud_set, values=[], width=8),
                'bits': ttk.Combobox(self.toolbar, textvariable=self.bits_set, values=[], width=2),
                'pary': ttk.Combobox(self.toolbar, textvariable=self.pary_set, values=[], width=2),
                'stop': ttk.Combobox(self.toolbar, textvariable=self.stop_set, values=[], width=2)}

    for key in ['port', 'baud', 'bits', 'pary', 'stop']:
      self.cfg[key].pack(side=tk.LEFT, padx=2, pady=2)

    self.toolbar.pack(side=tk.TOP, fill=tk.X)

    # font for the terminal window
    text_font = font.Font(family="Courier", size=10)

    # use a frame to group the terminal window and scrollbar together
    output_frame = ttk.Frame(self, borderwidth=3, relief=tk.SUNKEN)
    output_frame.pack(side=tk.TOP, fill=tk.Y, expand=1)

    # create a vertical scrollbar
    output_scroll = ttk.Scrollbar(output_frame)
    output_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=2)

    # create a terminal window
    self.output_text = tk.Text(output_frame, width=130, height=24, takefocus=0, font=text_font)
    self.output_text.pack(side=tk.TOP, fill=tk.Y, expand=1)

    # create color tags
    self.output_text.tag_config('foreground_red', foreground="#ff0000")
    self.output_text.tag_config('foreground_grn', foreground="#00c000")
    self.output_text.tag_config('foreground_blk', foreground="#000000")

    # connect the scrollbar
    self.output_text.config(yscrollcommand=output_scroll.set)
    output_scroll.config(command=self.output_text.yview)

    # text entry
    self.entry = ttk.Entry(self, width=80, font=text_font)
    self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=2)
