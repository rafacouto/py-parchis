#!/usr/bin/env python

""" board.py: board and square data structures for playing Parchis. """

__author__      = "Rafa Couto"
__copyright__   = "Copyright 2012, aplicacionesYredes.com"
__credits__     = ["Rafa Couto"]
__license__     = "GPLv3"
__version__     = "2012.11.16"
__maintainer__  = "Rafa Couto"
__email__       = "caligari@treboada.net"



PLAYER_COLORS = ('YELLOW', 'BLUE', 'RED', 'GREEN')
"""@var: Colors identifying players"""


class Square(object):
    """Square of board"""   

    def __init__(self, name, isSafe = False, color = None, rampAccess = None):
        """ Square constructor: inits data data structures.

            @type  name: string
            @param name: Unique name to identify a square.
	    @type  isSafe: boolean
            @param isSafe: Pawns are not captured in a safe square.
	    @type  color: number
            @param color: Color of the square to draw in the board.
	    @type  rampAccess: number
            @param rampAccess: Color of the ramp where this square links to. 
        """
        self._name = name
        self.isSafe = isSafe
        self.color = color
        self._rampAccess = rampAccess
        self.pawns = []
        self._next = None       

    def __str__(self):
        return self._name

    def put(self, color):
        """Puts a pawn in the square. Returns the captured pawn (if any)."""
        captured = None
        if len(self.pawns) == 1 and (not self.isSafe) and self.pawns[0] != color:
            captured = self.pawns[0]
            self.pawns[0] = color
        elif len(self.pawns) == 2 and color == self.color:
            other = 1 if self.pawns[1] != color else 0
            captured = self.pawns[other]
            self.pawns[other] = color
        else:
            self.pawns.append(color)
        return captured

    def get(self, color):
        """Remove a pawn from the square."""
        self.pawns.remove(color)
        return color



class Board(object):
    """Board of parchis"""

    def __init__(self, playersCount, pawnsOut = 1):
        """Constructor of Board."""
        self._squares = {}
        self._playersCount = playersCount
        self._nests = []
        self._path = []
        self._ramps = [ [], [], [], [] ]
        self._goals = []
        self._buildBoard()
        self._putPawns(pawnsOut)

    def _createSquare(self, name, isSafe, color = None, rampAccess = None):
        """Creates a square on board."""
        square = Square(name, isSafe, color, rampAccess)
        self._squares[name] = square
        return square

    def _buildBoard(self):
        """Builds nests, squares, ramps and goals."""
        for color in xrange(4):
            playerColor = PLAYER_COLORS[color]
            playerColorInitial = playerColor[0].lower()
            # nests
            self._nests.append(self._createSquare("N" + playerColorInitial, True, color))
            # path
            for number in xrange(17):
                squareNumber = (17 * color) + number + 1
                squareColor = color if number == 5 else None
                isSafe = (number == 5 or number == 12 or number == 17)
                rampAccess = ((color + 1) % 4) if number == 17 else None                
                self._path.append(self._createSquare(str(squareNumber), isSafe, squareColor, rampAccess))
            # ramps
            for number in xrange(7):
                squareName = "G" + playerColorInitial + "-" + str(7 - number)
                self._ramps[color].append(self._createSquare(squareName, True, color))
            # goals
            self._goals.append(self._createSquare("G" + playerColorInitial, True, color))
        self._linkSquares()

    def _linkSquares(self):
        """Links the natural advance from a square to another one."""
        for color in xrange(4):
            # nests
            self._nests[color]._next = self._path[(17 * color) + 4]
            # ramps
            for index in xrange(6):
                self._ramps[color][index]._next = self._ramps[color][index + 1]
            self._ramps[color][6]._next = self._goals[color]
        # path
        pathLen = len(self._path)
        for index in xrange(pathLen):
            self._path[index]._next = self._path[(index + 1) % (pathLen)]

    def _putPawns(self, pawnsOut):
        """Puts pawns at nests."""
        for color in xrange(self._playersCount):
            for pawn in xrange(4 - pawnsOut):
                self._nests[color].pawns.append(color)
            for pawn in xrange(pawnsOut):
                self._nests[color]._next.pawns.append(color)

    def __str__(self):
        """String represenation."""
        players = []        
        for color in xrange(4):
            squares = map(str, self._findPawns(color))
            if len(squares) > 0:
                players.append("%s: %s" % (PLAYER_COLORS[color], " ".join(squares)))
        return " - ".join(players)

    def _squareFromName(self, name):
        """Returns the named's square of the board as an instance of type Square."""
        if self._squares.has_key(name):
            return self._squares[name]
        else:
            raise SyntaxError, "Square '%s' doesn't exist." % name

    def _findPawns(self, color):
        """Returns the squares of the pawns for a player."""
        squares = []
        for square in self._squares.values():
            for pawn in square.pawns:
                if pawn == color:
                    squares.append(square)
        return squares

    def _forwardSquare(self, square, color, advances):
        """Returns the square calculated from a square for a player and the number of advances"""       
        for a in xrange(advances):
            if square._rampAccess == color:
                square = self._ramps[color][0]
            else:
                square = square._next
            if square == None: return None
        return square

    def forwardSquare(self, square, playerColor, advances):
        """Returns the square's name calculated from a square for a player and the number of advances."""
        square = self._squareFromName(square)
        color = PLAYER_COLORS.index(playerColor)
        return str(self._forwardSquare(square, color, advances))

    def move(self, squareFrom, squareTo, playerColor):
        """Moves a pawn a from a square to another one. Returns the captured pawn (it is carried to its nest automatically)."""
        # squares
        ori = self._squareFromName(squareFrom)
        des = self._squareFromName(squareTo)
        # color
        color = PLAYER_COLORS.index(playerColor)
        if not (color in ori.pawns):
            raise LookupError, "There is not %s pawn at %s square." % (color_str, str(square))
        # moving
        ori.get(color)
        captured = des.put(color)
        # captured pawn goes nest
        if captured:
            self._nests[captured].append(captured)
        return captured


