# -*- coding: utf-8 -*-
#
# Copyright 2012
#
# Authors: Denis Kovalev <aikikode@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public
# License version 3 and version 2.1 along with this program.  If not, see
# <http://www.gnu.org/licenses>
#

import gtk

VERSION = "0.0.1"
ROWS=9
COLS=9

##############################################################################
class VikingChess(object):
    def __init__(self):
        self.mainWindow = mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        mainWindow.set_keep_above(True)
        self.vbox = gtk.VBox()
        self.hbox = [HBox(x) for x in xrange(ROWS)]
        [self.vbox.pack_start(self.hbox[x]) for x in xrange(ROWS)]

        self.cell = [[Cell(x, y) for y in xrange(ROWS)] for x in xrange(COLS)]

        [[self.hbox[x].pack_start(self.cell[x][y]) for y in xrange(ROWS)] for x in xrange(COLS)]

        mainWindow.add(self.vbox)
        self.vbox.show()
        [self.hbox[x].show() for x in xrange(ROWS)]
        [[self.cell[x][y].show() for y in xrange(ROWS)] for x in xrange(COLS)]
        mainWindow.show()

class Cell(gtk.Button):
    def __init__(self, x, y):
        gtk.Button.__init__(self, str(x) + ":" + str(y))

class HBox(gtk.HBox):
    def __init__(self, x):
        gtk.HBox.__init__(self, str(x))


##############################################################################
def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    vc = VikingChess()
    main()
