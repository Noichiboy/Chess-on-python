"""
Ceci est notre fichier principal. Il récupère les instructions des joueurs et l'état de la partie.
"""

import pygame as p              # importe la librairie pygame qui nous permettra de créer une interface graphique
from Echecs import ChessEngine  # donne accès au fichier ChessEngine

WIDTH = HEIGHT = 512            # résolution du jeu
DIMENSION = 8                   # dimension du plateau
SQ_SIZE = HEIGHT // DIMENSION   # taille d'une case
MAX_FPS = 15                    # nombre d'images par secondes pour les animations de déplacement de pièces d'échecs
IMAGES = {}


'''
Initialise un dictionnaire nous permettant de charger les images des pièces dans notre jeu.
'''
def chargerImages():
    pieces = ['bP', 'bT', 'bC', 'bF', 'bR', 'bQ', 'nP', 'nT', 'nC', 'nF', 'nR', 'nQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # p = alias de pygame. On fait appelle aux fonctions de cette librairie.
        # En 2ème position, on a le nom du module utilisé. Dans une librairie, les fonctions sont classées par modules.
        # Le module image par exemple contient toutes les fonctions permettant de manipuler des images.
        # En 3ème position, on a le nom de la fonction appartenant au module.

        # Note : On peut accéder à une image en tapant IMAGES['bP'] par exemple.


'''
Ceci sera notre fonction principale. Elle va prendre en charge les commandes entrées par l'utilisateur et va mettre à 
jour les graphismes du jeu au cours de la partie.
'''
def main():
    p.init()                                        # initialise la librairie
    screen = p.display.set_mode((WIDTH, HEIGHT))    # initialise la taille de notre fenêtre de jeu
    clock = p.time.Clock()                          # initialise une horloge pour pouvoir ajouter une limite de temps
    screen.fill(p.Color("white"))                   # notre écran est mis en blanc
    gs = ChessEngine.GameState()                    # variable stockant l'état de jeu
    validMoves = gs.getValidMoves()                 # liste des coups valides
    moveMade = False                                # tant que le déplacement n'est pas validé, la liste des coups
                                                    # valides n'est pas mise à jour
    chargerImages()                                 # appelle la fonction nous permettant de charger les images
    running = True
    sqSelected = ()     # garde une trace de la dernière case sélectionnée par le joueur, format : (row, col)
    playerClicks = []   # garde une trace des 2 derniers clics de l'utilisateur, format : [(row1, col1), (row2,col2)]
    while running:                                # boucle infini, le jeu continue de tourner tant qu'il n'est pas fermé
        for e in p.event.get():                     # récupère les actions du joueur
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:       # si on clique
                location = p.mouse.get_pos()        # position de la souris récupérée sous forme de coordonnées (x, y)
                col = location[0]//SQ_SIZE          # coordonnée x/taille de case = numéro de colonne
                row = location[1]//SQ_SIZE          # coordonnée y/taille de case = numéro de rangée
                if sqSelected == (row, col):       # si l'utilisateur a cliqué 2 fois sur la même case
                    sqSelected = ()                 # désélectionne la case
                    playerClicks = []               # supprime historique des clics
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)    # ajoute les coordonnées du dernier clic à la fin de playerClicks
                if len(playerClicks) == 2:             # si 2 clics enregistrés
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)               # réalise le coup
                        moveMade = True
                        sqSelected = ()                 # réinitialise la dernière case sélectionnée
                        playerClicks = []               # réinitialise les clics de l'utilisateurs
                    else:
                        playerClicks = [sqSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:                  # annule coup quand z est pressé
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()                            # met à jour le contenu de l'écran


'''
Responsable de tout ce qui est lié aux graphics
'''
def drawGameState(screen, gs):
    drawBoard(screen)               # dessine les cases sur le plateau
    # ajouter suggestions de coups plus tard
    drawPieces(screen, gs.board)    # dessine les pièces sur les cases


'''
Dessine les cases du plateau, la première case en haut à gauche est toujours claire
'''
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):              # pour chaque rangée
        for c in range(DIMENSION):          # pour chaque colonne
            color = colors[((r + c) % 2)]   # si (numéro de rangée + numéro de colonne) % 2 est paire, on met la case
                                            # en gris, sinon, on la met en blanc
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
dessine les pièces sur le plateau
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):      # pour chaque rangée
        for c in range(DIMENSION):  # pour chaque colonne
            piece = board[r][c]     # récupère le nom de la pièce aux coordonnées (r ; c)
            if piece != "--":       # si la case n'est pas vide / si une pièce est présente sur la case
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # affiche la pièce



if __name__ == "__main__":  # le concept n'est pas si simple à comprendre pour un débutant
    main()                  # regarde sur internet à quoi sert cette ligne si tu es curieux

