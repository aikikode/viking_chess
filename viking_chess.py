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

import gobject
import socket
import sys
import pygtk
import threading

pygtk.require('2.0')
import pango
import gtk

gtk.gdk.threads_init()

VERSION = "0.0.1"

BOARD_SIZE = (9, 13)  # all boards are square -> no need to store 2 dimensions

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

# Colors definitions (in 256-base RGB)
BUTTON_EMPTY_BG_COLOR = (215, 152,  36)   # initially empty cell
WHITE_FORTRESS_COLOR  = (  0, 100,   0)   # initial white knights location
BLACK_FORTRESS_COLOR  = (  0,   0, 250)   # initial black knights and king location
TARGET_CELL_COLOR     = (100,   0,   0)   # cells where the King should go to win

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

def idle_add_decorator(func):
    def callback(*args):
        gobject.idle_add(func, *args)
    return callback

##############################################################################
class MainWindow(gtk.Window):
    """ Main window the user sees after application starts.
        It should present choices to start a local game,
        start a server or connect to existing one """
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("delete-event", main_quit) # Prevent application hanging after closing the window
        self.set_keep_above(False)
        self.set_title("Viking Chess")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)

        # Put buttons in VBox and put that VBox in HBox to get some space between buttons
        btStartLocalGame = gtk.Button(label="Start Local Game")
        btStartLocalGame.set_size_request(200, 50)
        btStartLocalGame.connect("clicked", self.startLocalGameSetup, None)
        vbox = gtk.VBox(True, 3)
        vbox.pack_start(btStartLocalGame, False, False, 15)
        # Add another button for server start
        btServer = gtk.Button(label="Start Server")
        btServer.set_size_request(200, 50)
        btServer.connect("clicked", self.showServerSetup, None)
        vbox.pack_start(btServer, False, False, 0)
        # Add another button - for client connect
        btClient = gtk.Button(label="Connect")
        btClient.set_size_request(200, 50)
        btClient.connect("clicked", self.showClientSetup, None)
        vbox.pack_start(btClient, False, False, 0)
        # Add another button - for help/rules
        btHelp = gtk.Button(label="Game Rules")
        btHelp.set_size_request(200, 50)
        btHelp.connect("clicked", self.showHelp, None)
        vbox.pack_start(btHelp, False, False, 0)

        hbox = gtk.HBox(False, 5)
        hbox.pack_start(vbox, False, False, 15)
        self.add(hbox)

        # Show all controls
        hbox.show_all()
    #def __init__(self)

    def startLocalGameSetup(self, widget, data = None):
        self.destroy()
        LocalGameSetup()

    def showServerSetup(self, widget, data = None):
        self.destroy()
        ServerSetup()

    def showClientSetup(self, widget, data = None):
        # TODO: make a real setup window
        self.destroy()
        print "Start Client Board"
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(SERVER_ADDRESS)
        vc = VikingChessBoardOnline(False, client_socket)
        vc.isServer = False
        vc.startGame()

    def showHelp(self, widget, data=None):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_resizable(True)
        window.set_title("Viking Chess Rules")
        window.set_border_width(0)

        box1 = gtk.VBox(False, 0)
        window.add(box1)
        box1.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        fontdesc = pango.FontDescription("monospace")
        textview.modify_font(fontdesc)
        textview.set_editable(False)
        textbuffer = textview.get_buffer()
        sw.add(textview)
        sw.show()
        textview.show()

        box2.pack_start(sw)
        # Load the file textview-basic.py into the text window
        infile = open("README.md", "r")

        if infile:
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)
        window.set_size_request(730, 550)
        window.set_position(gtk.WIN_POS_CENTER)
        window.show()
    #def showHelp(self, widget, data=None)
#class MainWindow(gtk.Window)

##############################################################################
class LocalGameSetup(gtk.Window):
    """ Settings window shown just before game start:
        choose game field size and other options """
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("delete-event", self.startMainMenu)
        self.set_keep_above(False)
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
        self.show_all()
    #def __init__(self)

    def startMainMenu(self, widget, data=None):
        self.destroy()
        MainWindow().show()

    def startGame(self, widget, data = None):
        # Get options
        index = self.cboxBoardSize.get_active()
        self.destroy()
        VikingChessBoard(index).startGame()
#class LocalGameSetup(gtk.Window)

class ServerSetup(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("delete-event", self.startMainMenu)
        self.set_resizable(True)
        self.set_title("Viking Chess Server Setup")
        self.set_border_width(0)
        self.set_position(gtk.WIN_POS_CENTER)

        lblBoardSize = gtk.Label("Set board size:")
        self.cboxBoardSize = gtk.combo_box_new_text()
        self.cboxBoardSize.append_text(str(BOARD_SIZE[0]) + " x " + str(BOARD_SIZE[0]))
        self.cboxBoardSize.append_text(str(BOARD_SIZE[1]) + " x " + str(BOARD_SIZE[1]))
        self.cboxBoardSize.set_active(0)
        btStartServer = gtk.Button(label="Start Server")
        btStartServer.connect("clicked", self.startServer, None)
        hbox = gtk.HBox(True, 3)
        hbox.pack_start(lblBoardSize, False, False, 10)
        hbox.pack_end(self.cboxBoardSize, False, False, 10)
        hbox2 = gtk.HBox(True, 3)
        hbox2.pack_start(btStartServer, False, False, 10)
        vbox = gtk.VBox(False, 3)
        vbox.pack_start(hbox, False, False, 5)
        vbox.pack_end(hbox2, False, False, 5)
        self.add(vbox)
        self.show_all()

    def startMainMenu(self, widget, data=None):
        self.destroy()
        MainWindow().show()

    def startServer(self, widget, data = None):
        # Get options
        index = self.cboxBoardSize.get_active()
        self.destroy()
        # starting the server waiting for cnnections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(2)
        print "Start Server"
        print "Waiting for a client to connect"
        connection_socket, connection_addr = server_socket.accept()
        # Send game index to the client
        connection_socket.send(str(index))
        vc = VikingChessBoardOnline(True, connection_socket, index)
        vc.isServer = True
        vc.startGame()
    #def startServer(self, widget, data = None)
#class ServerSetup(gtk.Window)

##############################################################################
class VikingChessBoard(object):
    def __init__(self, gameIndex = 0):
        self.gameIndex = gameIndex
        self.whiteCount = 0
        self.winner = None
        self.mainWindow = mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        mainWindow.connect("delete-event", self.onClose)
        mainWindow.set_keep_above(False)
        self.mainWindow.set_title("Viking Chess - White")
        mainWindow.set_resizable(False)

        vboxBoard = gtk.VBox()
        hbox = [gtk.HBox() for x in xrange(BOARD_SIZE[self.gameIndex])]
        [vboxBoard.pack_start(hbox[x]) for x in xrange(BOARD_SIZE[self.gameIndex])]
        # Define cells and connect them to button click
        self.cell = [[Cell(self, x, y) for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]
        [[self.cell[x][y].connect("clicked", self.buttonClicked, None) for y in xrange(BOARD_SIZE[self.gameIndex])] for x in xrange(BOARD_SIZE[self.gameIndex])]
        # Place the cells in HBox containers
        [[hbox[y].pack_start(self.cell[x][BOARD_SIZE[self.gameIndex] - 1 - y]) for x in xrange(BOARD_SIZE[self.gameIndex])] for y in xrange(BOARD_SIZE[self.gameIndex])]

        # X axises from below and from above the board
        hboxXAxisBelow = gtk.HBox()
        xAxis = [gtk.Label(chr(ord('a') + x)) for x in xrange(BOARD_SIZE[self.gameIndex])]
        [hboxXAxisBelow.pack_start(xAxis[x]) for x in xrange(BOARD_SIZE[self.gameIndex])]
        hboxXAxisAbove = gtk.HBox()
        xAxis = [gtk.Label(chr(ord('a') + x)) for x in xrange(BOARD_SIZE[self.gameIndex])]
        [hboxXAxisAbove.pack_start(xAxis[x]) for x in xrange(BOARD_SIZE[self.gameIndex])]
        # Y axises from the left and from the right of the board
        vboxYAxisLeft = gtk.VBox()
        yAxis = [gtk.Label(y + 1) for y in xrange(BOARD_SIZE[self.gameIndex])]
        [vboxYAxisLeft.pack_end(yAxis[y]) for y in xrange(BOARD_SIZE[self.gameIndex])]
        vboxYAxisRight = gtk.VBox()
        yAxis = [gtk.Label(y + 1) for y in xrange(BOARD_SIZE[self.gameIndex])]
        [vboxYAxisRight.pack_end(yAxis[y]) for y in xrange(BOARD_SIZE[self.gameIndex])]
        # Log text view
        self.sw = sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        fontdesc = pango.FontDescription("monospace")
        textview.modify_font(fontdesc)
        textview.set_editable(False)
        self.textbuffer = textview.get_buffer()
        self.textbuffer.connect('changed', self.scrollLog)
        sw.add(textview)
        sw.set_size_request(200, 50)
        sw.set_border_width(3)
        # Pack the board and axises in one large container - table
        table = gtk.Table(3, 4, False)
        table.attach(gtk.Label(), 0, 1, 0, 1)
        table.attach(hboxXAxisAbove, 1, 2, 0, 1)
        table.attach(gtk.Label(), 2, 3, 0, 1)
        table.attach(vboxYAxisLeft, 0, 1, 1, 2)
        table.attach(vboxBoard, 1, 2, 1, 2)
        table.attach(vboxYAxisRight, 2, 3, 1, 2)
        table.attach(gtk.Label(), 0, 1, 2, 3)
        table.attach(hboxXAxisBelow, 1, 2, 2, 3)
        table.attach(gtk.Label(), 2, 3, 2, 3)
        table.attach(gtk.Label(), 2, 3, 2, 3)
        table.attach(gtk.Label("Moves Performed:"), 3, 4, 0, 1)
        table.attach(sw, 3, 4, 1, 3)
        table.set_border_width(3)

        mainWindow.add(table)
        # Center the window
        self.mainWindow.set_position(gtk.WIN_POS_CENTER)

    def coordToText(self, x, y):
        return chr(ord('a') + x) + str(y + 1)

    def scrollLog(self, widget, data=None):
        adj = self.sw.get_vadjustment()
        adj.set_value(adj.upper - adj.page_size)
    def logMessage(self, message):
        iter = self.textbuffer.get_end_iter()
        iter.backward_char()
        self.textbuffer.insert(iter, message)
    def logMove(self, isWhite, fromCell, toCell):
        self.movesCount += 1
        who = "W" if isWhite else "B"
        self.textbuffer.insert(self.textbuffer.get_end_iter(),
            str(self.movesCount) + ". " + who + ": " +
            self.coordToText(fromCell.x, fromCell.y) +
            " -> " +
            self.coordToText(toCell.x, toCell.y) +
            ";\n")
    def clearLog(self):
        self.movesCount = 0
        self.textbuffer.set_text("")

    def onClose(self, widget, data=None):
        dialog = gtk.MessageDialog(self.mainWindow,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_YES_NO,
            "Quit the game? It will discard all game progress.")
        dialog.set_title("Confirm Quit")
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            self.mainWindow.destroy()
            MainWindow().show() # Show main menu on exit
        else:
            return True
    #def onClose(self, widget, data=None)

    def startGame(self):
        self.mainWindow.show_all()
        self.clearLog()
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

    def addWhiteFortressPos(self, coordsList):
        # Although white fortress cells are defined during white knights setting,
        # on some boards we need to add move fortress cells to make a fortress
        # without 'empty' cells inside. Because if they exist and white knight
        # moves to it, it will never come out due to the game rule: "no knight
        # or king can move from an 'empty' cell to or over a fortress cell"
        for (x, y) in coordsList:
            self.cell[x][y].set_label("")
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
            self.cell[4][4].setColor(TARGET_CELL_COLOR)
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
            self.addWhiteFortressPos([(6, 1), (1, 6), (6, 11), (11, 6)])
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
            self.cell[6][6].setColor(TARGET_CELL_COLOR)
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
        # If it was black turn and they couldn't break the check, they loose the game
        # NB: self.whiteTurn should point to the current turn that just finished!
        if self.isCheck and not self.whiteTurn:
            self.winner = "White"
            return True
        # In all other cases the game continues
        return False
    #def isGameOver(self)

    # Unpress all buttons except current one
    def clearAllCells(self):
        [[self.cell[x][y].clear() for x in xrange(BOARD_SIZE[self.gameIndex])] for y in xrange(BOARD_SIZE[self.gameIndex])]

    def buttonClicked(self, cell, data=None):
        if cell.get_active():
            # Allow to select only the knights of player color
            if (self.whiteTurn and cell.isWhite) or\
               (not self.whiteTurn and (cell.isBlack or cell.isBlackKing)): # choose the knight to move
                if self.selectedCell is not None and self.selectedCell != cell:
                    self.selectedCell.set_active(False)
                self.selectedCell = cell
            else: # move the knight if possible
                if self.selectedCell is not None and self.isValidMove(cell):
                    self.performMove(self.selectedCell.x, self.selectedCell.y, cell.x, cell.y)
                else:
                    cell.set_active(False)
        else:
            if self.selectedCell == cell:
                # Unselect current cell
                self.selectedCell = None
            #if (self.whiteTurn and cell.isWhite)...
    #def buttonClicked(self, cell, data=None)

    def isValidMove(self, toCell):
        """ check whether the move from self.selectedCell to toCell is valid """
        fromCell = self.selectedCell
        cell = self.cell
        # We should've already checked that the correct knight is selected
        # 1. Allow only horizontal and vertical moves
        if fromCell.x != toCell.x and fromCell.y != toCell.y:
            return False
        # 2. Do not allow jumping into the white fortress
        if not fromCell.isWhiteFortress and toCell.isWhiteFortress:
            return False
        # 3. Do not allow jumping over other knights and over (and to) the throne cell
        #    and over the fortress
        if toCell.isThrone or not toCell.isEmpty():
            return False
        if fromCell.x == toCell.x: # move along Y axis
            minY = min(fromCell.y, toCell.y)
            maxY = max(fromCell.y, toCell.y)
            for y in xrange(minY + 1, maxY):
                if not cell[fromCell.x][y].isEmpty() or cell[fromCell.x][y].isThrone or\
                   (cell[fromCell.x][y].isWhiteFortress and not fromCell.isWhiteFortress):
                    return False
        else:                      # move along X axis
            minX = min(fromCell.x, toCell.x)
            maxX = max(fromCell.x, toCell.x)
            for x in xrange(minX + 1, maxX):
                if not cell[x][fromCell.y].isEmpty() or cell[x][fromCell.y].isThrone or\
                   (cell[x][fromCell.y].isWhiteFortress and not fromCell.isWhiteFortress):
                    return False
        # 2*. Do not allow moving from one fortress to another:
        #     if the dist between cells is > half the board - deny the move
        if fromCell.isWhiteFortress and toCell.isWhiteFortress and\
           abs(fromCell.x - toCell.x + fromCell.y - toCell.y) > (BOARD_SIZE[self.gameIndex] - 1) / 2:
            return False
        # 4. Only the King can move to a corner
        if toCell.isCorner and not fromCell.isBlackKing:
            return False
        # 5. The King can move 3 cells max
        if fromCell.isBlackKing and abs(toCell.x - fromCell.x + toCell.y - fromCell.y) > 3:
            return False
        # Otherwise the move is valid
        return True

    def performMove(self, fromCellX, fromCellY, toCellX, toCellY):
        fromCell = self.cell[fromCellX][fromCellY]
        toCell = self.cell[toCellX][toCellY]
        self.logMove(self.whiteTurn, fromCell, toCell)
        if fromCell.isWhite:
            toCell.setWhite()
        elif fromCell.isBlack:
            toCell.setBlack()
        elif fromCell.isBlackKing:
            toCell.setBlackKing()
        toCell.set_active(False)
        fromCell.clear()
        if fromCell.isThrone:
            # The king just moved from the Throne -
            # set special label to indicate the Throne
            fromCell.set_label("X")
        fromCell.set_active(False)
        self.checkKilledKnights(toCell)
        self.checkClearCheck()
        # Always check whether anybody won the game after each move
        if not self.isGameOver():  # It's important not to switch turns before calling this function!
            self.whiteTurn = not self.whiteTurn # ...now it's safe
            whoseTurn = "White" if self.whiteTurn else "Black"
            self.mainWindow.set_title("Viking Chess - " + whoseTurn)
        else:
            threading.Thread(target=self.showGameOverDialog).start()
    #def performMove(self, fromCellX, fromCellY, toCellX, toCellY)

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
            if curCell.isWhite and (cell[cx][cy].isWhite or cell[cx][cy].isCorner or cell[cx][cy].isThrone):
                if cell[mx][my].isBlack:
                    if not cell[cx][cy].isBlackKing: # black knight can be killed by pushing to the empty throne
                        cell[mx][my].clear()
                        self.logMessage(" -" + self.coordToText(mx, my))
                elif cell[mx][my].isBlackKing:
                    # Check for 'check': point is we can flag 'check' only after white knight move,
                    # but unflag it after any move based on king surrounding
                    #
                    # Check if the king is on the border -> then it's check
                    if 0 == mx or BOARD_SIZE[self.gameIndex] - 1 == mx or\
                       0 == my or BOARD_SIZE[self.gameIndex] - 1 == my:
                        self.isCheck = True
                        self.logMessage(" Check!")
#                        self.showCheckWarn()
                        continue
                    # This may be a check, usually it is, but we need to check 2 exclusions:
                    # 1. the king is on the throne and surrounded by white knights
                    # 2. the king is near the throne and surrounded by white knights from 3 other sides
                    if cell[mx][my].isThrone:
                        # 1-st case
                        for (x, y) in [(self.kingX - 1, self.kingY),
                                   (self.kingX + 1, self.kingY),
                                   (self.kingX, self.kingY - 1),
                                   (self.kingX, self.kingY + 1)]:
                            if not cell[x][y].isWhite:
                                break
                        else:
                            self.isCheck = True
                            self.logMessage(" Check!")
#                            self.showCheckWarn()
                            continue
                    else:
                        whiteCounts = 0
                        isThroneNear = False
                        for (x, y) in [(self.kingX - 1, self.kingY),
                                       (self.kingX + 1, self.kingY),
                                       (self.kingX, self.kingY - 1),
                                       (self.kingX, self.kingY + 1)]:
                            if cell[x][y].isWhite:
                                whiteCounts += 1
                            elif cell[x][y].isThrone:
                                isThroneNear = True
                        if isThroneNear:
                            # 2-nd case
                            if whiteCounts == 3:
                                self.isCheck = True
                                self.logMessage(" Check!")
#                                self.showCheckWarn()
                                continue
                        else:
                            # Throne is not nearby and the King is between 2 white knights -> it's check
                            self.isCheck = True
                            self.logMessage(" Check!")
#                            self.showCheckWarn()
                            continue
                    #if cell[mx][my].isThrone
                #elif cell[mx][my].isBlackKing
            #if curCell.isWhite and (cell[cx][cy].isWhite or cell[cx][cy].isCorner or cell[cx][cy].isThrone)
            # Black King can fight too
            if (curCell.isBlack or curCell.isBlackKing) and\
               (cell[cx][cy].isBlack or cell[cx][cy].isBlackKing or cell[cx][cy].isCorner or cell[cx][cy].isThrone) and\
               cell[mx][my].isWhite:
                self.whiteCount -= 1
                cell[mx][my].clear()
                self.logMessage(" -" + self.coordToText(mx, my))
            # Special situation: white can kill a black knight if it is surrounded
            # from 3 sides and the black king if from the 4-th side
            if curCell.isWhite and cell[cx][cy].isBlackKing and cell[mx][my].isBlack:
                # Make sure the knight we attack is not near the border
                if not (0 == mx or BOARD_SIZE[self.gameIndex] - 1 == mx or
                        0 == my or BOARD_SIZE[self.gameIndex] - 1 == my):
                    if cx == mx:
                        if cell[mx - 1][my].isWhite and cell[mx + 1][my].isWhite:
                            cell[mx][my].clear()
                            self.logMessage(" -" + self.coordToText(mx, my))
                    elif cy == my:
                        if cell[mx][my - 1].isWhite and cell[mx][my + 1].isWhite:
                            cell[mx][my].clear()
                            self.logMessage(" -" + self.coordToText(mx, my))
    #def checkKilledKnights(self, curCell)

    def showCheckWarn(self):
        dialog = gtk.MessageDialog(self.mainWindow,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_CLOSE,
            "Black king is in check!\nYou have one move to rescue him!")
        dialog.set_title("King in check!")
        dialog.run()
        dialog.destroy()

    def checkClearCheck(self):
        """ Try to clear isCheck flag """
        cell = self.cell
        kingX = self.kingX
        kingY = self.kingY
        gameIndex = self.gameIndex
        # If the king is in the corner there's no check
        if cell[kingX][kingY].isCorner:
            self.isCheck = False
            return
        # If the king is near the border and is not surrounded from 2 sides -> no check
        if 0 == kingX or BOARD_SIZE[gameIndex] - 1 == kingX:
            if not cell[kingX][kingY - 1].isWhite or\
                not cell[kingX][kingY + 1].isWhite:
                self.isCheck = False
                return
            else:
                return
        elif 0 == kingY or BOARD_SIZE[gameIndex] - 1 == kingY:
            if not cell[kingX - 1][kingY].isWhite or\
                not cell[kingX + 1][kingY].isWhite:
                self.isCheck = False
                return
            else:
                return
        # Now we know that the king is not near the border
        # Check whether we are surrounded on the throne
        if cell[kingX][kingY].isThrone:
            for (x, y) in [(kingX - 1, kingY),
                           (kingX + 1, kingY),
                           (kingX, kingY - 1),
                           (kingX, kingY + 1)]:
                if not cell[x][y].isWhite:
                    self.isCheck = False
                    return
        else:
            # check whether we are near the throne
            whiteCounts = 0
            isThroneNear = False
            for (x, y) in [(kingX - 1, kingY),
                           (kingX + 1, kingY),
                           (kingX, kingY - 1),
                           (kingX, kingY + 1)]:
                if cell[x][y].isWhite:
                    whiteCounts += 1
                elif cell[x][y].isThrone:
                    isThroneNear = True
            if isThroneNear:
                if whiteCounts < 3:
                    self.isCheck = False
                    return
            else:
                # Throne is not nearby
                if whiteCounts < 2:
                    # King cannot be in check with one white knight
                    self.isCheck = False
                    return
                else:
                    # Is the king not between two white knights?
                    if not ((cell[kingX - 1][kingY].isWhite and cell[kingX + 1][kingY].isWhite) or
                            (cell[kingX][kingY - 1].isWhite and cell[kingX][kingY + 1].isWhite)):
                        self.isCheck = False
                        return
        #if cell[kingX][kingY].isThrone
    #def checkClearCheck(self)

    @idle_add_decorator
    def showGameOverDialog(self):
        winner = self.winner
        self.mainWindow.set_title("Viking Chess - " + winner + " won!")
        winnerDialog = gtk.MessageDialog(
            parent = None,
            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
            type = gtk.MESSAGE_INFO,
            buttons = gtk.BUTTONS_OK,
            message_format = winner + " won!"
        )
        winnerDialog.set_title("Round complete!")
        winnerDialog.connect('response', self.gameOverDialogResponse)
        winnerDialog.connect('close', self.gameOverDialogResponse)
        winnerDialog.set_position(gtk.WIN_POS_CENTER)
        winnerDialog.set_keep_above(True)
        winnerDialog.show()
    @idle_add_decorator
    def gameOverDialogResponse(self, widget, data=None):
        widget.destroy()
        self.startGame()
#class VikingChessBoard(object)


##############################################################################
class VikingChessBoardOnline(VikingChessBoard):
    def __init__(self, isServer, msocket, gameIndex=0):
        print "OnlineChess Server: " + str(isServer) + " Index = " + str(gameIndex)
        self.isServer = isServer
        self.msocket = msocket
        self.gameIndex = gameIndex
        if not self.isServer:
            # Get game index from the server
            self.gameIndex = int(self.msocket.recv(1024).strip())
        VikingChessBoard.__init__(self, self.gameIndex)

    def startGame(self):
        print "New Game Started"
        VikingChessBoard.startGame(self)
        if not self.isServer:
            threading.Thread(target=self.wait_for_move).start()

    # Override buttonClicked() according to client/server behaviour
    # to send data about the move to the other player.
    #
    # Call performMove() on receiving the data from client/server
    # to move the knight like the other player did.
    def buttonClicked(self, cell, data=None):
        if self.isServer and self.whiteTurn or\
           not self.isServer and not self.whiteTurn:
            if cell.get_active():
                # Allow to select only the knights of player color
                if (self.whiteTurn and cell.isWhite) or\
                   (not self.whiteTurn and (cell.isBlack or cell.isBlackKing)): # choose the knight to move
                    if self.selectedCell is not None and self.selectedCell != cell:
                        self.selectedCell.set_active(False)
                    self.selectedCell = cell
                else: # move the knight if possible
                    if self.selectedCell is not None and self.isValidMove(cell):
                        to_send = str(self.selectedCell.x) + ":" + str(self.selectedCell.y) + ":" + str(cell.x) + ":" + str(cell.y) + "\n"
                        self.msocket.send(to_send)
                        self.performMove(self.selectedCell.x, self.selectedCell.y, cell.x, cell.y)
                        if self.winner is None:
                            threading.Thread(target=self.wait_for_move).start()
                    else:
                        cell.set_active(False)
            else:
                if self.selectedCell == cell:
                    # Unselect current cell
                    self.selectedCell = None
        else:
            cell.set_active(False)
    #def buttonClicked(self, cell, data=None)

    def wait_for_move(self):
        data = self.msocket.recv(1024).strip()
        from_cell_x, from_cell_y, to_cell_x, to_cell_y = data.split(':')
        # Use idle_add to update GUI not from the main thread
        gobject.idle_add(self.performMove, int(from_cell_x), int(from_cell_y), int(to_cell_x), int(to_cell_y))

    def onClose(self, widget, data=None):
        dialog = gtk.MessageDialog(self.mainWindow,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_YES_NO,
            "Quit the game? It will discard all game progress.")
        dialog.set_title("Confirm Quit")
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            self.msocket.shutdown(socket.SHUT_WR)
            self.msocket.close()
            self.mainWindow.destroy()
            MainWindow().show() # Show main menu on exit
        else:
            return True
    #def onClose(self, widget, data=None)
#class VikingChessBoardOnline(VikingChessBoard)


##############################################################################
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
        self.set_label("")
        self.isWhite = False
        self.isBlack = False
        self.isBlackKing = False
        self.set_image(gtk.Image())

    def setWhite(self):
        self.set_label("")
        self.isWhite = True
        self.isBlack = False
        self.isBlackKing = False
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/white_knight.png")
        scaled_buf = pixbuf.scale_simple(30,30,gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        self.set_image(image)

    def setBlack(self):
        self.set_label("")
        self.isWhite = False
        self.isBlack = True
        self.isBlackKing = False
        pixbuf = gtk.gdk.pixbuf_new_from_file("./ico/black_knight.png")
        scaled_buf = pixbuf.scale_simple(30,30,gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        self.set_image(image)

    def setBlackKing(self):
        self.set_label("")
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
        style.bg[gtk.STATE_ACTIVE] = color
        style.bg[gtk.STATE_INSENSITIVE] = color
        style.bg[gtk.STATE_SELECTED] = color
        # Set the button's style to the one you created
        self.set_style(style)

    def isEmpty(self):
        return not (self.isWhite or self.isBlack or self.isBlackKing)

    def setThrone(self):
        self.isThrone = True
        self.set_label("X")
#class Cell(gtk.ToggleButton)


##############################################################################
def main():
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    return 0

def main_quit(widget=None, data=None):
    # TODO: stop server here and close all connections
    gtk.main_quit()

if __name__ == "__main__":
    MainWindow().show()
    main()