#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from gi.repository import GObject
# import pygtk
# pygtk.require('2.0')
import gtk
import sys

import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/home/michal3141/sat')

from model import Model
from time import time


class SATBoard(object):

    def __init__(self, clauses):
        self.clauses = clauses
        self.num_of_rows = self.row_count()
        self.num_of_cols = len(self.clauses)
        self.create()
        self.layout()
        self.show()

    def row_count(self):
        max_len = 0
        for clause in self.clauses:
            if len(clause) > max_len:
                max_len = len(clause)
        return max_len

    def _get_label(self, j, i):
        try:
            return str(abs(self.clauses[j][i]))
        except IndexError:
            return ""

    def _set_color(self, btn):
        try:
            map = btn.get_colormap() 
            if self.clauses[btn.j][btn.i] < 0:
                color = map.alloc_color("red")
            else:
                color = map.alloc_color("green")

            #copy the current style and replace the background
            style = btn.get_style().copy()
            style.bg[gtk.STATE_NORMAL] = color
            style.bg[gtk.STATE_SELECTED] = style.bg[gtk.STATE_NORMAL]
            style.bg[gtk.STATE_PRELIGHT] = style.bg[gtk.STATE_NORMAL]
            style.bg[gtk.STATE_ACTIVE] = style.bg[gtk.STATE_NORMAL]

            #set the button's style to the one you created
            btn.set_style(style)
        except IndexError:
            pass

    def _set_label(self, btn):
        try:
            lab = str(abs(self.clauses[btn.j][btn.i]))
            btn.set_label(lab)
        except IndexError:
            pass
        
    def create(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(400, 100)
        self.window.connect("destroy", self.destroy)
        self.window.connect("delete_event", self.delete_event)
        self.table = gtk.Table(rows=self.num_of_rows, columns=self.num_of_cols, homogeneous=True)
        self.buttons = [[gtk.Button(label=self._get_label(j, i)) for i in xrange(self.num_of_rows)] for j in xrange(self.num_of_cols)]
        for j, col in enumerate(self.buttons):
            for i, button in enumerate(col):
                button.connect('clicked', self.button_clicked)
                button.j = j
                button.i = i
                self._set_color(button)
                try:
                    _ = self.clauses[j][i]
                    button.clickable = True
                except IndexError:
                    button.clickable = False

    def layout(self):
        for j in xrange(self.num_of_cols):
            for i in xrange(self.num_of_rows):
                self.table.attach(self.buttons[j][i], j, j + 1, i, i + 1)
        self.window.add(self.table)

    def show(self):
        for row in self.buttons:
            for button in row:
                button.show()
        self.table.show()
        self.window.show()

    def is_gameover(self):
        seen = set()
        for clause in self.clauses:
            if -clause[0] in seen:
                return False
            else:
                seen.add(clause[0])

        msg = 'Game Over ! Well done !'
        md = gtk.MessageDialog(self.window,
                                0,
                                gtk.MESSAGE_INFO,
                                gtk.BUTTONS_OK,
                                msg)
        md.run()
        md.destroy()
        return True

    def button_clicked(self, widget):
        if widget.clickable and (not self.is_gameover()):
            # Performing swap
            j = widget.j
            i = widget.i
            self.clauses[j][0], self.clauses[j][i] = self.clauses[j][i], self.clauses[j][0]
            self._set_label(self.buttons[j][0])
            self._set_label(self.buttons[j][i])
            self._set_color(self.buttons[j][0])
            self._set_color(self.buttons[j][i])

            self.is_gameover()

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        return False

    def play(self):
        gtk.main()

if __name__ == "__main__":
    c0 = [[1, 2], [-1, 2], [3, -4]]
    c1 = [[1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3], [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]
    c2 = [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    f.unit_propagate()

    # from gi.repository import Gdk as gdk
    # screen = gdk.Screen.get_default()

    # css_provider = gtk.CssProvider()
    # css_provider.load_from_path('style.css')

    # context = gtk.StyleContext()
    # context.add_provider_for_screen(
    #     screen,
    #     css_provider,
    #     gtk.STYLE_PROVIDER_PRIORITY_USER
    # )

    board = SATBoard(f.clauses)
    start = time()
    print f.solve()
    end = time()
    print 'Time spent:', end - start
    # board = SATBoard(c2)
    board.play()