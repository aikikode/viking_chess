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
ROWS = [9, 13]
COLS = [9, 13]

GTK_COLOR_BASE = 65535
RGB_COLOR_BASE = 255
BUTTON_EMPTY_BG_COLOR = (215, 152, 36)
WHITE_KNIGHT_COLOR = (240, 240, 240)
BLACK_KNIGHT_COLOR = (50, 50, 50)
BLACK_KING_COLOR = (10, 10, 10)

settings = gtk.settings_get_default()
settings.props.gtk_button_images = True

def rgb_to_gtk_simple(rgb_color): return GTK_COLOR_BASE * rgb_color / RGB_COLOR_BASE

def RGB_TO_GTK(rgb_color_tuple):
    return map(rgb_to_gtk_simple, rgb_color_tuple)
##############################################################################
class MainWindow(gtk.Window):
    """ Main window the user sees after application starts.
        It should present choices to start a local game,
        start a server or connectn to existing one """
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("delete-event", gtk.main_quit) # Prevent application hanging after closing the window
        self.set_keep_above(True)
        self.set_title("Viking Chess")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)

        # Put button in HBox and put that HBox in VBox to get some space
        btStartLocalGame = gtk.Button(label="Start Local Game")
        btStartLocalGame.set_size_request(200, 50)
        btStartLocalGame.connect("clicked", self.startLocalGameSetup, None)
        hbox = gtk.HBox(True, 3)
        hbox.pack_start(btStartLocalGame, False, False, 15)
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(hbox, False, False, 15)
        self.add(vbox)

        # Show all controls
        btStartLocalGame.show()
        hbox.show()
        vbox.show()
    #def __init__(self)

    def startLocalGameSetup(self, widget, data = None):
        self.destroy()
        LocalGameSetup().show()
#class MainWindow(gtk.Window)

class LocalGameSetup(gtk.Window):
    """ Settings window shown just before game start:
        choose game field size and other options """
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("delete-event", self.startMainMenu)
        self.set_keep_above(True)
        self.set_title("Setup")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)

        lblFieldSize = gtk.Label("Set field size:")
        self.cboxFieldSize = gtk.combo_box_new_text()
        self.cboxFieldSize.append_text(str(ROWS[0]) + " x " + str(ROWS[0]))
        self.cboxFieldSize.append_text(str(ROWS[1]) + " x " + str(ROWS[1]))
        self.cboxFieldSize.set_active(0)
        btStartGame = gtk.Button(label="Start Game")
        btStartGame.connect("clicked", self.startGame, None)
        hbox = gtk.HBox(True, 3)
        hbox.pack_start(lblFieldSize, False, False, 10)
        hbox.pack_end(self.cboxFieldSize, False, False, 10)
        hbox2 = gtk.HBox(True, 3)
        hbox2.pack_start(btStartGame, False, False, 10)
        vbox = gtk.VBox(False, 3)
        vbox.pack_start(hbox, False, False, 5)
        vbox.pack_end(hbox2, False, False, 5)
        self.add(vbox)

        # Show all controls
        lblFieldSize.show()
        self.cboxFieldSize.show()
        btStartGame.show()
        hbox.show()
        hbox2.show()
        vbox.show()
    #def __init__(self)

    def startMainMenu(self, widget, data=None):
        self.destroy()
        MainWindow().show()

    def startGame(self, widget, data = None):
        # Get options
        index = self.cboxFieldSize.get_active()
        self.destroy()
        VikingChessBoard(index).startGame()

class VikingChessBoard(object):
    def __init__(self, gameIndex):
        self.gameIndex = gameIndex
        self.whiteCount = 0
        self.mainWindow = mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        mainWindow.connect("delete-event", self.startMainMenu) # Show main menu on exit
        mainWindow.set_keep_above(True)
        mainWindow.set_title("Viking Chess")
        mainWindow.set_resizable(False)
        self.vbox = gtk.VBox()
        self.hbox = [HBox(x) for x in xrange(ROWS[self.gameIndex])]
        [self.vbox.pack_start(self.hbox[x]) for x in xrange(ROWS[self.gameIndex])]

        # Place the board on the window
        self.cell = [[Cell(self, x, y) for y in xrange(ROWS[self.gameIndex])] for x in xrange(COLS[self.gameIndex])]
        [[self.hbox[x].pack_start(self.cell[x][y]) for y in xrange(ROWS[self.gameIndex])] for x in xrange(COLS[self.gameIndex])]
        mainWindow.add(self.vbox)
        self.vbox.show()
        [self.hbox[x].show() for x in xrange(ROWS[self.gameIndex])]
        [[self.cell[x][y].connect("clicked", self.buttonClicked, None) for y in xrange(ROWS[self.gameIndex])] for x in xrange(COLS[self.gameIndex])]
        [[self.cell[x][y].show() for y in xrange(ROWS[self.gameIndex])] for x in xrange(COLS[self.gameIndex])]

        # Center the window
        self.mainWindow.set_position(gtk.WIN_POS_CENTER)

    def startMainMenu(self, widget, data=None):
        self.mainWindow.destroy()
        MainWindow().show()

    def startGame(self):
        self.mainWindow.show()
        self.clearAllCells()
        self.setInitialPos()
        self.selectedCell = None
        self.winner = None
        self.whiteTurn = True

    def setInitialPos(self):
        self.kingX = -1
        self.kingY = -1
        if 0 == self.gameIndex:
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
            self.whiteCount = 16
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
        elif 1 == self.gameIndex:
            # Set throne
            self.cell[6][6].isThrone = True
            # Set white
            self.cell[0][4].setWhite()
            self.cell[0][5].setWhite()
            self.cell[0][6].setWhite()
            self.cell[0][7].setWhite()
            self.cell[0][8].setWhite()
            self.cell[1][5].setWhite()
            self.cell[1][7].setWhite()
            self.cell[2][6].setWhite()

            self.cell[4][0].setWhite()
            self.cell[5][0].setWhite()
            self.cell[6][0].setWhite()
            self.cell[7][0].setWhite()
            self.cell[8][0].setWhite()
            self.cell[5][1].setWhite()
            self.cell[7][1].setWhite()
            self.cell[6][2].setWhite()

            self.cell[12][4].setWhite()
            self.cell[12][5].setWhite()
            self.cell[12][6].setWhite()
            self.cell[12][7].setWhite()
            self.cell[12][8].setWhite()
            self.cell[11][5].setWhite()
            self.cell[11][7].setWhite()
            self.cell[10][6].setWhite()

            self.cell[4][12].setWhite()
            self.cell[5][12].setWhite()
            self.cell[6][12].setWhite()
            self.cell[7][12].setWhite()
            self.cell[8][12].setWhite()
            self.cell[5][11].setWhite()
            self.cell[7][11].setWhite()
            self.cell[6][10].setWhite()

            self.whiteCount = 32
            # Set black
            self.cell[6][6].setBlackKing()

            self.cell[3][6].setBlack()
            self.cell[4][4].setBlack()
            self.cell[4][8].setBlack()
            self.cell[5][5].setBlack()
            self.cell[5][6].setBlack()
            self.cell[5][7].setBlack()

            self.cell[6][3].setBlack()
            self.cell[8][4].setBlack()
            self.cell[6][5].setBlack()
            self.cell[7][5].setBlack()

            self.cell[9][6].setBlack()
            self.cell[8][8].setBlack()
            self.cell[7][7].setBlack()
            self.cell[7][6].setBlack()

            self.cell[6][7].setBlack()
            self.cell[6][9].setBlack()
    #def setInitialPos(self)

    def isGameOver(self):
        # Check whether the King reached the border
        for x in [0, ROWS[self.gameIndex] - 1]:
            for y in xrange(COLS[self.gameIndex]):
                if self.cell[x][y].isBlackKing:
                    self.winner = "Black"
                    return True
        for y in [0, COLS[self.gameIndex] - 1]:
            for x in xrange(ROWS[self.gameIndex]):
                if self.cell[x][y].isBlackKing:
                    self.winner = "Black"
                    return True
        # If there are no white knights left, black wins
        if self.whiteCount <= 0:
            self.winner = "Black"
            return True
        # Now check if the king is between 4 white knights or
        # between 3 white knights and a throne
        for (x, y) in [(self.kingX - 1, self.kingY),
                       (self.kingX + 1, self.kingY),
                       (self.kingX, self.kingY - 1),
                       (self.kingX, self.kingY + 1)]:
            if not (self.cell[x][y].isWhite or self.cell[x][y].isThrone):
                return False
        self.winner = "White"
        return True
    #def isGameOver(self)

    # Unpress all buttons except current one
    def clearAllCells(self):
        [[self.cell[x][y].clear() for x in xrange(COLS[self.gameIndex])] for y in xrange(ROWS[self.gameIndex])]

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
                    if self.selectedCell.isThrone:
                        # The king just moved from the Throne -
                        # set special label to indicate the Throne
                        self.selectedCell.set_label("X")
                    self.selectedCell = None
                    self.checkKilledKnights(cell)
                    self.whiteTurn = not self.whiteTurn
                    # Always check whether anybody won the game after each move
                    if self.isGameOver():
                        winner = self.winner
                        winnerDialog = gtk.MessageDialog(
                            parent = None,
                            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
                            type = gtk.MESSAGE_INFO,
                            buttons = gtk.BUTTONS_OK,
                            message_format = self.winner + " wins!"
                        )
                        winnerDialog.set_title("Round complete!")
                        winnerDialog.connect('response', lambda dialog, response: self.startGame())
                        winnerDialog.set_position(gtk.WIN_POS_CENTER)
                        winnerDialog.set_keep_above(True)
                        winnerDialog.run()
                        winnerDialog.destroy()
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
        if toCell.isThrone or not toCell.isEmpty():
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

    def checkKilledKnights(self, curCell):
        # We need to check only the cross 5x5 with the center in the current cell:
        #    X
        #    O
        #  XOXOX
        #    O
        #    X
        # doing so we even don't need to check whose turn it was because we are checking
        # only for knights killed by the 'attack'.
        cell = self.cell
        x = curCell.x
        y = curCell.y
        for (cx, cy) in [(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)]:
            if cx < 0 or cy < 0 or cx >= COLS[self.gameIndex] or cy >= ROWS[self.gameIndex]:
                continue
            (mx, my) = ((cx + x) / 2, (cy + y) / 2)
            if curCell.isWhite and cell[cx][cy].isWhite and cell[mx][my].isBlack:
                cell[mx][my].clear()
            if curCell.isBlack and cell[cx][cy].isBlack and cell[mx][my].isWhite:
                self.whiteCount -= 1
                cell[mx][my].clear()
    #def checkKilledKnights(self, curCell)
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
        self.setColor(BUTTON_EMPTY_BG_COLOR)

    def clear(self):
        self.set_label("")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False
        self.setColor(BUTTON_EMPTY_BG_COLOR)
        self.set_image(gtk.Image())

    def setWhite(self):
        self.set_label("W")
        self.isWhite = True
        self.isBlack = False
        self.isBlackKing = False
        self.setColor(WHITE_KNIGHT_COLOR)

    def setBlack(self):
        self.set_label("B")
        self.isWhite = False
        self.isBlack = True
        self.isBlackKing = False
        self.setColor(BLACK_KNIGHT_COLOR)

    def setBlackKing(self):
        self.set_label("")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = True
        self.mainWindow.kingX = self.x
        self.mainWindow.kingY = self.y
        self.setColor(BLACK_KING_COLOR)
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/circle_red.png")
        scaled_buf = pixbuf.scale_simple(30,30,gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        self.set_image(image)

    def setColor(self, newColor):
        # Make a gdk.color
        map = self.get_colormap()
        gtkColor = RGB_TO_GTK(newColor)
        color = map.alloc_color(gtkColor[0], gtkColor[1], gtkColor[2], False, True)
        # Copy the current style and replace the background
        style = self.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        style.bg[gtk.STATE_PRELIGHT] = color
        # Set the button's style to the one you created
        self.set_style(style)

    def isEmpty(self):
        return not (self.isWhite or self.isBlack or self.isBlackKing)

    def setThrone(self):
        print "setThrone"
        self.isThrone = True
        self.set_label("X")
#class Cell(gtk.Button)

class HBox(gtk.HBox):
    def __init__(self, x):
        gtk.HBox.__init__(self, str(x))


##############################################################################
def main():
    gtk.main()
    return 0


if __name__ == "__main__":
    MainWindow().show()
    main()
