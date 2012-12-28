#!/usr/bin/env python
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

# TODO: king can fight
# TODO: on small board 2 white knights are enough to kill the black King (4 - on the throne and 3  - 'with' the throne)
# TODO: white knight can move inside the fortress, but once it leaves it, it can't return.
# TODO: no knight or king can move inside the fortress or over it
# TODO: add game rules

import sys
import pygtk
pygtk.require('2.0')
import gtk

VERSION = "0.0.1"

BOARD_SIZE = (9, 13)  # all boards are square -> no need to store 2 dimensions

# Colors definitions (in 256-base RGB)
BUTTON_EMPTY_BG_COLOR = (215, 152,  36)   # initially empty cell
WHITE_FORTRESS_COLOR  = (  0, 100,   0)   # initial white knights location
BLACK_FORTRESS_COLOR  = (  0,   0, 250)   # initial black knights and king location
TARGET_CELL_COLOR     = (255,   0,   0)   # cells where the King should go to win

# Conversion between GTK color system and 256-RGB
GTK_COLOR_BASE = 65535
RGB_COLOR_BASE = 255
def rgb_to_gtk_simple(rgb_color): return GTK_COLOR_BASE * rgb_color / RGB_COLOR_BASE
def RGB_TO_GTK(rgb_color_tuple): return map(rgb_to_gtk_simple, rgb_color_tuple)

# Enable images on buttons (since they are disabled by default)
if sys.platform=="win32":
    gtk.settings_get_default().set_long_property("gtk-button-images", True, "main")
else:
    settings = gtk.settings_get_default()
    settings.props.gtk_button_images = True

##############################################################################
class MainWindow(gtk.Window):
    """ Main window the user sees after application starts.
        It should present choices to start a local game,
        start a server or connect to existing one """
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

        lblBoardSize = gtk.Label("Set board size:")
        self.cboxBoardSize = gtk.combo_box_new_text()
        self.cboxBoardSize.append_text(str(BOARD_SIZE[0]) + " x " + str(BOARD_SIZE[0]))
        self.cboxBoardSize.append_text(str(BOARD_SIZE[1]) + " x " + str(BOARD_SIZE[1]))
        self.cboxBoardSize.set_active(0)
        btStartGame = gtk.Button(label="Start Game")
        btStartGame.connect("clicked", self.startGame, None)
        hbox = gtk.HBox(True, 3)
        hbox.pack_start(lblBoardSize, False, False, 10)
        hbox.pack_end(self.cboxBoardSize, False, False, 10)
        hbox2 = gtk.HBox(True, 3)
        hbox2.pack_start(btStartGame, False, False, 10)
        vbox = gtk.VBox(False, 3)
        vbox.pack_start(hbox, False, False, 5)
        vbox.pack_end(hbox2, False, False, 5)
        self.add(vbox)

        # Show all controls
        lblBoardSize.show()
        self.cboxBoardSize.show()
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
        index = self.cboxBoardSize.get_active()
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
        self.hbox = [HBox(x) for x in xrange(BOARD_SIZE[self.gameIndex])]
        [self.vbox.pack_start(self.hbox[x]) for x in xrange(BOARD_SIZE[self.gameIndex])]

        # Place the board on the window
        self.cell = [[Cell(self, x, y) for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]
        [[self.hbox[x].pack_start(self.cell[x][y]) for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]
        mainWindow.add(self.vbox)
        self.vbox.show()
        [self.hbox[x].show() for x in xrange(BOARD_SIZE[self.gameIndex])]
        [[self.cell[x][y].connect("clicked", self.buttonClicked, None) for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]
        [[self.cell[x][y].show() for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]

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

    def setInitialWhitePos(self, coordsList):
        for (x, y) in coordsList:
            self.cell[x][y].set_label("")
            self.cell[x][y].setWhite()
            self.cell[x][y].isTarget = False
            self.cell[x][y].isWhiteFortress = True
            self.cell[x][y].setColor(WHITE_FORTRESS_COLOR)

    def setInitialBlackPos(self, coordsList):
        for (x, y) in coordsList:
            self.cell[x][y].set_label("")
            self.cell[x][y].setBlack()
            self.cell[x][y].setColor(BLACK_FORTRESS_COLOR)

    def setTargetPos(self, coordsList):
        for (x, y) in coordsList:
            self.cell[x][y].set_label("")
            self.cell[x][y].isTarget = True
            self.cell[x][y].setColor(TARGET_CELL_COLOR)

    def setCornerPos(self, coordsList):
        for (x, y) in coordsList:
            self.cell[x][y].set_label("X")
            self.cell[x][y].isCorner = True

    def setInitialPos(self):
        self.kingX = -1
        self.kingY = -1
        # Set locked corner cells
        corners = [(0, 0),
                   (BOARD_SIZE[self.gameIndex] - 1, 0),
                   (0, BOARD_SIZE[self.gameIndex] - 1),
                   (BOARD_SIZE[self.gameIndex] - 1, BOARD_SIZE[self.gameIndex] - 1)]
        if 0 == self.gameIndex:
            # Set white
            self.setInitialWhitePos([(0, 3), (0, 4), (0, 5), (1, 4),
                                     (3, 0), (4, 0), (5, 0), (4, 1),
                                     (3, 8), (4, 8), (5, 8), (4, 7),
                                     (8, 3), (8, 4), (8, 5), (7, 4)])
            self.whiteCount = 16
            # Set black
            # NB: set king position among black knights first to color the cell
            self.setInitialBlackPos([(2, 4), (3 ,4), (5, 4), (6, 4),
                                     (4, 2), (4, 3), (4, 5), (4, 6),
                                     (4, 4)])
            # Set king
            self.cell[4][4].isThrone = True
            self.cell[4][4].setBlackKing()
            # Set target positions for a King to reach - in this game they are the corners
            self.setTargetPos(corners)
        elif 1 == self.gameIndex:
            # Set target positions for a King to reach
            # NB: this should be done before setting the knights on the board
            #     because these cells may overlap and 'knights' cells are excluded
            #     from 'target' cells
            targetCells = []
            for y in [0, BOARD_SIZE[self.gameIndex] - 1]:
                for x in xrange(BOARD_SIZE[self.gameIndex]):
                    targetCells.append((x, y))
            for x in [0, BOARD_SIZE[self.gameIndex] - 1]:
                for y in xrange(BOARD_SIZE[self.gameIndex]):
                    targetCells.append((x, y))
            self.setTargetPos(targetCells)
            # Set white
            self.setInitialWhitePos([(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 5), (1, 7), (2, 6),
                                     (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (5, 1), (7, 1), (6, 2),
                                     (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (11, 5), (11, 7), (10, 6),
                                     (4, 12), (5, 12), (6, 12), (7, 12), (8, 12), (5, 11), (7, 11), (6, 10)])
            self.whiteCount = 32
            # Set black
            self.setInitialBlackPos([(3, 6), (4, 4), (4, 8), (5, 5), (5, 6), (5, 7),
                                     (6 ,3), (8, 4), (6, 5), (7, 5),
                                     (9, 6), (8, 8), (7, 7), (7, 6),
                                     (6, 7), (6, 9),
                                     (6, 6)])
            # Set king
            self.cell[6][6].isThrone = True
            self.cell[6][6].setBlackKing()
        self.setCornerPos(corners)
    #def setInitialPos(self)

    def isGameOver(self):
        # Check whether the King reached the target cell
        if self.cell[self.kingX][self.kingY].isTarget:
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
        [[self.cell[x][y].clear() for x in xrange(BOARD_SIZE[self.gameIndex])] for y in xrange(BOARD_SIZE[self.gameIndex])]

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
        # 3. Do not allow jumping over and into the white fortress,
        #    but only if the knight is already in it
        # 4. Only the King can move to a corner
        if toCell.isCorner and not fromCell.isBlackKing:
            return False
        # 5. The King can move 3 cells max
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
            if cx < 0 or cy < 0 or cx >= BOARD_SIZE[self.gameIndex] or cy >= BOARD_SIZE[self.gameIndex]:
                continue
            (mx, my) = ((cx + x) / 2, (cy + y) / 2)
            if curCell.isWhite and (cell[cx][cy].isWhite or cell[cx][cy].isCorner) and cell[mx][my].isBlack:
                cell[mx][my].clear()
            if curCell.isBlack and (cell[cx][cy].isBlack or cell[cx][cy].isCorner) and cell[mx][my].isWhite:
                self.whiteCount -= 1
                cell[mx][my].clear()
    #def checkKilledKnights(self, curCell)
#class VikingChess(object)


class Cell(gtk.ToggleButton):
    def __init__(self, parent, x, y):
        gtk.ToggleButton.__init__(self)
        self.mainWindow = parent
        self.x = x
        self.y = y
        self.set_size_request(40, 40)
        self.set_label("")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False
        self.isThrone = False
        self.isTarget = False
        self.isCorner = False
        self.isWhiteFortress = False
        self.setColor(BUTTON_EMPTY_BG_COLOR)

    def clear(self):
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False
        self.set_image(gtk.Image())

    def setWhite(self):
        self.isWhite = True
        self.isBlack = False
        self.isBlackKing = False
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/white_knight.png")
        scaled_buf = pixbuf.scale_simple(30,30,gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        self.set_image(image)


    def setBlack(self):
        self.isWhite = False
        self.isBlack = True
        self.isBlackKing = False
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/black_knight.png")
        scaled_buf = pixbuf.scale_simple(30,30,gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        self.set_image(image)


    def setBlackKing(self):
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = True
        self.mainWindow.kingX = self.x
        self.mainWindow.kingY = self.y
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/black_king.png")
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
#class Cell(gtk.ToggleButton)

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
