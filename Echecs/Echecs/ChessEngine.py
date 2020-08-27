"""
Cette classe se charge de stocker toutes les informations concernant l'état actuel du jeu d'échecs (emplacement de
pièces, coups, etc).
Elle va aussi déterminer si les coups joués sont valides.
"""

class GameState():
    def __init__(self):
        # le plateau est une liste 2D en 8x8 (8 lignes, 8 colonnes), chaque élément de la liste a 2 caractères
        # le premier caractère représente la couleur de la pièce, "n" (noir) ou "b" (blanc)
        # le second caractère représente le type de la pièce, "R" (Roi), "Q" (pour Queen), "F" (Fou), "C" (Cavalier),
        # "T" (Tour) et "P" (Pion)
        # "--" représente une case vide, sans pièce
        self.board = [
            ["nT", "nC", "nF", "nQ", "nR", "nF", "nC", "nT"],
            ["nP", "nP", "nP", "nP", "nP", "nP", "nP", "nP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["bT", "bC", "bF", "bQ", "bR", "bF", "bC", "bT"]
        ]
        self.whiteToMove = True     # Les blancs jouent en premier
        self.moveLog = []           # variable dans laquelle nous stockerons nos coups
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

    '''
    Prend un Move en paramètre et l'éxécute (coups spéciaux comme en passant ou roque non supportés)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"         # la case de départ est désormais vide
        self.board[move.endRow][move.endCol] = move.pieceMoved  # la pièce est ajoutée à la case d'arrivée
        self.moveLog.append(move)                               # enregistre le coup dans moveLog
        self.whiteToMove = not self.whiteToMove                 # alterne tour de jeu
        # met à jour la position du Roi s'il a bougé
        if move.pieceMoved == 'bR':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'nR':
            self.blackKingLocation = (move.endRow, move.endCol)

    '''
    Annule le dernier coup
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:      # s'assure qu'il y a un déplacement à annuler
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove     # redonne son tour à celui qui annule son dernier coup

    '''
    Tous les coups considérés comme en échec
    '''
    def getValidMoves(self):
        # 1. génère tous les coups possibles
        moves = self.getAllPossibleMoves()
        # 2. test les coups
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3. génère tous les coups de l'adversaire
            # 4. pour chaque coup adverse, vérifie si le Roi est attaqué
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5. si le Roi est attaqué, le coup n'est pas valide
            self.whiteToMove = not self.whiteToMove
            self.undoMove()             # annule le dernier coup
        return moves

    '''
    Détermine si le joueur dont c'est le tour est en échec
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.caseEstAttaque(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.caseEstAttaque(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Détermine si l'ennemi peut attaquer la case de coordonnées r, c
    '''
    def caseEstAttaque(self, r, c):
        self.whiteToMove = not self.whiteToMove             # passe au tour adverse pour récupérer ses coups possibles
        advMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove             # retour au tour précédent
        for move in advMoves:
            if move.endRow == r and move.endCol == c:       # la case est attaquée
                return True
        return False

    '''
    Tous les coups non considérés comme en échec
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):            # nombre de rangées
            for c in range(len(self.board[r])):     # nombre de colonnes
                turn = self.board[r][c][0]
                if (turn == 'b' and self.whiteToMove) or (turn == 'n' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.getPionMoves(r, c, moves)
                    elif piece == 'T':
                        self.getTourMoves(r, c, moves)
                    elif piece == 'F':
                        self.getFouMoves(r, c, moves)
                    elif piece == 'C':
                        self.getCavalierMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRoiMoves(r, c, moves)
        return moves


    '''
    Récupère tout les mouvements possibles pour un Pion situé sur une rangée, une colonne
    et ajoute ses mouvements à la liste
    '''
    def getPionMoves(self, r, c, moves):
        if self.whiteToMove:                # moves des pions blancs
            if self.board[r-1][c] == "--":  # si la case en face du pion est vide, il peut avancer (1 case seulement)
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":   # si pion sur rangée 6, il peut avancer de 2 cases
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:    # capture vers la gauche, on ne peut pas capturer en dehors du plateau (sur les bords)
                if self.board[r-1][c-1][0] == 'n':  # si la pièce à capturer est noire
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:    # capture vers la droite, on ne peut pas capturer en dehors du plateau (sur les bords)
                if self.board[r-1][c+1][0] == 'n':  # si la pièce à capturer est noire
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:   # moves des pions noirs
            if self.board[r+1][c] == "--":  # peut avancer d'une case
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":   # si pion sur rangée 1, peut avancer de 2 cases
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:    # capture vers la gauche, on ne peut pas capturer en dehors du plateau (sur les bords)
                if self.board[r+1][c-1][0] == 'b':  # si la pièce à capturer est blanche
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:    # capture vers la droite, on ne peut pas capturer en dehors du plateau (sur les bords)
                if self.board[r+1][c+1][0] == 'b':  # si la pièce à capturer est blanche
                    moves.append(Move((r, c), (r+1, c+1), self.board))
        # ajouter promotion plus tard


    '''
        Récupère tout les mouvements possibles pour une Tour situé sur une rangée, une colonne
        et ajoute ses mouvements à la liste
    '''
    def getTourMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))     # haut, gauche, bas, droite
        enemyColor = "n" if self.whiteToMove else "b"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:     # sur le plateau
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":                    # si la case d'arrivée est vide
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:         # si la case d'arrivée est occupée par un ennemi
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:   # case occupée par une pièce alliée
                        break
                else:       # hors du plateau
                    break

    '''
        Récupère tout les mouvements possibles pour un Cavalier situé sur une rangée, une colonne
        et ajoute ses mouvements à la liste
    '''
    def getCavalierMoves(self, r, c, moves):
        cavalierMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "b" if self.whiteToMove else "n"
        for m in cavalierMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow <8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:    # case d'arrivée pas occupée par une pièce alliée (vide ou ennemi)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
        Récupère tout les mouvements possibles pour un Fou situé sur une rangée, une colonne
        et ajoute ses mouvements à la liste
    '''
    def getFouMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))   # 4 directions
        enemyColor = "n" if self.whiteToMove else "b"
        for d in directions:
            for i in range(1, 8):   # le fou peut bouger de 7 cases maximum
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":    # case d'arrivée vide
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # si la case d'arrivée est occupée par un ennemi
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # case occupée par une pièce alliée
                        break
                else:  # hors du plateau
                    break

    '''
        Récupère tout les mouvements possibles pour une Queen situé sur une rangée, une colonne
        et ajoute ses mouvements à la liste
    '''
    def getQueenMoves(self, r, c, moves):
        self.getTourMoves(r, c, moves)
        self.getFouMoves(r, c, moves)

    '''
        Récupère tout les mouvements possibles pour un Roi situé sur une rangée, une colonne
        et ajoute ses mouvements à la liste
    '''
    def getRoiMoves(self, r, c, moves):
        roiMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "b" if self.whiteToMove else "n"
        for i in range(8):
            endRow = r + roiMoves[i][0]
            endCol = c + roiMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:    # pas de pièce alliée sur la case d'arrivée (vide ou pièce ennemi)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


'''
Cette classe va nous permettre de manipuler les coups et de les stocker dans moveLog
'''
class Move():
    # assigne les clés à des valeurs
    # clé : valeur
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}  # conversion valeur des rangées
    rowsToRanks = {v: k for k, v in ranksToRows.items()}                            # conversion dans l'autre sens
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}  # conversion valeur des colonnes
    colsToFiles = {v: k for k, v in filesToCols.items()}                            # conversion dans l'autre sens

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]                              # rangée case de départ
        self.startCol = startSq[1]                              # colonne case de départ
        self.endRow = endSq[0]                                  # rangée case d'arrivée
        self.endCol = endSq[1]                                  # rangée case d'arrivée
        self.pieceMoved = board[self.startRow][self.startCol]   # pièce présente sur la case de départ
        self.pieceCaptured = board[self.endRow][self.endCol]    # pièce capturée sur la case d'arrivée (dans notre
                                                                # programme une case vide contient une pièce "--")
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # id move

    '''
    Remplace la méthode permettant de comparer 2 objets en python afin d'éviter des conflits avec d'autres
    instructions plus tard
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
