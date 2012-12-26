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
        mainWindow.connect("delete-event", gtk.main_quit) # Prevent application hanging after closing the window
        mainWindow.set_keep_above(True)
        self.vbox = gtk.VBox()
        self.hbox = [HBox(x) for x in xrange(ROWS)]
        [self.vbox.pack_start(self.hbox[x]) for x in xrange(ROWS)]

        self.cell = [[Cell(self, x, y) for y in xrange(ROWS)] for x in xrange(COLS)]

        [[self.hbox[x].pack_start(self.cell[x][y]) for y in xrange(ROWS)] for x in xrange(COLS)]

        mainWindow.add(self.vbox)
        self.vbox.show()
        [self.hbox[x].show() for x in xrange(ROWS)]
        [[self.cell[x][y].connect("clicked", self.buttonClicked, None) for y in xrange(ROWS)] for x in xrange(COLS)]
        [[self.cell[x][y].show() for y in xrange(ROWS)] for x in xrange(COLS)]
        mainWindow.show()
        self.startGame()

    def startGame(self):
        self.setInitialPos()
        self.selectedCell = None
        self.winner = None
        self.whiteTurn = True

    def setInitialPos(self):
        self.kingX = -1
        self.kingY = -1
        # Set throne
        self.cell[4][4].isThrone = True
        # Set white
        self.cell[0][3].setWhite()
        self.cell[0][4].setWhite()
        self.cell[0][5].setWhite()
        self.cell[1][4].setWhite()
        self.cell[3][0].setWhite()
        self.cell[4][0].setWhite()
        self.cell[5][0].setWhite()
        self.cell[4][1].setWhite()
        self.cell[3][8].setWhite()
        self.cell[4][8].setWhite()
        self.cell[5][8].setWhite()
        self.cell[4][7].setWhite()
        self.cell[8][3].setWhite()
        self.cell[8][4].setWhite()
        self.cell[8][5].setWhite()
        self.cell[7][4].setWhite()
        # Set black
        self.cell[4][4].setBlackKing()
        self.cell[2][4].setBlack()
        self.cell[3][4].setBlack()
        self.cell[5][4].setBlack()
        self.cell[6][4].setBlack()
        self.cell[4][2].setBlack()
        self.cell[4][3].setBlack()
        self.cell[4][5].setBlack()
        self.cell[4][6].setBlack()
    #def setInitialPos(self)

    def checkGameEnd(self):
        # Check whether the King reached the border
        for x in [0, ROWS - 1]:
            for y in [0, COLS - 1]:
                if self.cell[x][y].isBlackKing:
                    # White win
                    self.winner = "White"
                    return True
        # Now check if the king is between 4 black knights
        for x in [self.kingX - 1, self.kingX + 1]:
            for y in [self.kingY - 1, self.kingY + 1]:
                if not self.cell[x][y].isWhite:
                    return False
        self.winner = "Black"
        return True
    #def checkGameEnd(self)

    # Unpress all buttons except current one
    def clearButtons(self, cellX, cellY):
        for x in xrange(COLS):
            for y in xrange(ROWS):
                if not (x == cellX and y == cellY):
                    self.cell[x][y].set_active(False)
    #def clearButtons(self, cellX, cellY)

    def buttonClicked(self, cell, data=None):
        if cell.get_active():
            # Allow to select only the knights of player color
            if (self.whiteTurn and cell.isWhite) or\
               (not self.whiteTurn and (cell.isBlack or cell.isBlackKing)): # choose the knight to move
                if self.selectedCell is not None:
                    self.selectedCell.set_active(False)
                self.selectedCell = cell
            else: # move the knight if possible
                if self.selectedCell is not None and self.isValidMove(cell):
                    if self.selectedCell.isWhite:
                        cell.setWhite()
                    elif self.selectedCell.isBlack:
                        cell.setBlack()
                    elif self.selectedCell.isBlackKing:
                        cell.setBlackKing()
                    self.selectedCell.set_active(False)
                    cell.set_active(False)
                    self.selectedCell.clear()
                    self.selectedCell = None
                    self.whiteTurn = not self.whiteTurn
                    # Always check whether anybody won the game after each move
                    self.checkGameEnd()
                else:
                    cell.set_active(False)
            #if (self.whiteTurn and cell.isWhite)...
    #def buttonClicked(self, cell, data=None)

    def isValidMove(self, toCell):
        """ check whether the move from self.selectedCell to toCell is valid """
        fromCell = self.selectedCell
        # We should've already checked that the correct knight is selected
        # 1. Allow only horizontal and vertical moves
        if fromCell.x != toCell.x and fromCell.y != toCell.y:
            return False
        # 2. Do not allow jumping over other knights and over (and to) the throne cell
        if toCell.isThrone:
            return False
        if fromCell.x == toCell.x: # move along Y axis
            minY = min(fromCell.y, toCell.y)
            maxY = max(fromCell.y, toCell.y)
            for y in xrange(minY + 1, maxY):
                if not self.cell[fromCell.x][y].isEmpty() or self.cell[fromCell.x][y].isThrone:
                    return False
        else:                      # move along X axis
            minX = min(fromCell.x, toCell.x)
            maxX = max(fromCell.x, toCell.x)
            for x in xrange(minX + 1, maxX):
                if not self.cell[x][fromCell.y].isEmpty() or self.cell[x][fromCell.y].isThrone:
                    return False
        # 3. The King can move 3 cells max
        if fromCell.isBlackKing and abs(toCell.x - fromCell.x + toCell.y - fromCell.y) > 3:
            return False
        # Otherwise the move is valid
        return True
#class VikingChess(object)


class Cell(gtk.ToggleButton):
    def __init__(self, parent, x, y):
#        gtk.Button.__init__(self, str(x) + ":" + str(y))
        gtk.ToggleButton.__init__(self)
        self.mainWindow = parent
        self.x = x
        self.y = y
        self.set_size_request(40, 40)
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False
        self.isThrone = False

    def clear(self):
        self.set_label("")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False

    def setWhite(self):
        self.set_label("W")
        self.isWhite = True
        self.isBlack = False
        self.isBlackKing = False

    def setBlack(self):
        self.set_label("B")
        self.isWhite = False
        self.isBlack = True
        self.isBlackKing = False

    def setBlackKing(self):
        self.set_label("BK")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = True
        self.mainWindow.kingX = self.x
        self.mainWindow.kingY = self.y

    def isEmpty(self):
        return not (self.isWhite or self.isBlack or self.isBlackKing)

#class Cell(gtk.Button)

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
