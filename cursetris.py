#!/usr/bin/env python3
"""
CurseTris - Jeu de Tetris pour terminal.

Version améliorée avec interface curses, couleurs, et gameplay moderne.
"""

__author__ = "Nicolas Méloni"
__version__ = "2.0"

import random
import curses
import time
from copy import deepcopy

# Constantes
HA, LA = 20, 10
BAS, GAUCHE, DROITE = (1,0),(0,-1),(0,1)
ROTATION_G, ROTATION_D = -1, 1
T = 'IOTLJZS'

TETRIMINOS = {
    'I': [[(0, 3), (0, 4), (0, 5), (0, 6)],
          [(0, 5), (1, 5), (2, 5), (3, 5)],
          [(2, 3), (2, 4), (2, 5), (2, 6)],
          [(0, 4), (1, 4), (2, 4), (3, 4)]],
    'O': [[(0, 4), (0, 5), (1, 4), (1, 5)]],
    'T': [[(0, 5), (1, 4), (1, 5), (1, 6)],
          [(0, 5), (1, 5), (2, 5), (1, 6)],
          [(1, 4), (1, 5), (2, 5), (1, 6)],
          [(0, 5), (1, 5), (2, 5), (1, 4)]],
    'L': [[(0, 6), (1, 4), (1, 5), (1, 6)],
          [(0, 5), (1, 5), (2, 5), (2, 6)],
          [(1, 4), (1, 5), (1, 6), (2, 4)],
          [(0, 4), (0, 5), (1, 5), (2, 5)]],
    'J': [[(0, 4), (1, 4), (1, 5), (1, 6)],
          [(0, 5), (1, 5), (2, 5), (0, 6)],
          [(1, 4), (1, 5), (1, 6), (2, 6)],
          [(2, 4), (0, 5), (1, 5), (2, 5)]],
    'Z': [[(0, 4), (0, 5), (1, 5), (1, 6)],
          [(0, 6), (1, 5), (1, 6), (2, 5)],
          [(1, 4), (1, 5), (2, 5), (2, 6)],
          [(0, 5), (1, 4), (1, 5), (2, 4)]],
    'S': [[(0, 5), (0, 6), (1, 4), (1, 5)],
          [(0, 5), (1, 5), (1, 6), (2, 6)],
          [(1, 5), (1, 6), (2, 4), (2, 5)],
          [(0, 4), (1, 4), (1, 5), (2, 5)]],
    '!': [(0,0)]
    }

# Couleurs pour chaque tetrimino
COULEURS = {
    'I': 1,  # Cyan
    'O': 2,  # Jaune
    'T': 3,  # Violet
    'L': 4,  # Orange
    'J': 5,  # Bleu
    'Z': 6,  # Rouge
    'S': 7,  # Vert
    '!': 8   # Blanc
}

class Tetrimino:
    def __init__(self, jeu, piece,lettre):
        self.jeu = jeu
        self.x,self.y,self.o = 0,0,0
        self.piece = piece
        self.lettre = lettre

    def get_coords(self):
        return [(i + self.x, j + self.y) for i, j in self.piece[self.o]]

    def peut_deplacer(self, direction):
        deplacement = True
        piece = self.piece[self.o]
        #on test si on peut la déplacer
        for i,j in piece:
            x = i+self.x+direction[0]
            y = j+self.y+direction[1]
            if self.jeu.grille[x][y] != 0:
                return False
        return True

    def peut_tourner(self, rotation):
        piece = self.piece[(self.o+rotation) % len(self.piece)]
        for i,j in piece:
            if self.jeu.grille[i+self.x][j+self.y] != 0:
                return False
        return True

    def deplacer(self, direction):
        self.x +=  direction[0]
        self.y +=  direction[1]

    def tourner(self, rotation):
        self.o = (self.o+rotation) % len(self.piece)

    def poser(self):
        piece = self.piece[self.o]
        for i,j in piece:
            x = i+self.x
            y = j+self.y
            self.jeu.grille[x][y] = self.lettre

class Termtris:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.HA, self.LA = HA, LA
        self.grille =  [[1]+[0]*LA+[1] for i in range(HA)]+[[1]*(LA+2)]
        self.lignes = 0
        self.score = 0
        self.niveau = 1
        self.tetriminos = TETRIMINOS
        self.ttm = None
        self.prochain = random.choice(T)
        self.game_over = False
        self.vitesse = 0.5
        
        # Initialiser les couleurs
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLORS - 10, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        #affichage extérieur
        self.stdscr.addstr(0, 2, "╔"+"══"*LA+ " TERMTRIS "+"══"*LA +"╗",
                                    curses.color_pair(9) | curses.A_BOLD)
        #initialisation de la zone de jeu
        self.game_window = curses.newwin(HA+2, LA*2+4, 2, 4)

        #intialisation de la zone d'info
        self.info_window = curses.newwin(HA+2, LA*2+2, 2, LA*2+10)

        #intialisation de la zone piece suivante
        self.next_piece_window = curses.newwin(6, 13, 4, LA*2+14)


    def draw_next_piece_window(self):
        # affichage de la piece suivante
        self.next_piece_window.box()
        next_piece = TETRIMINOS[self.prochain][0]
        couleur = COULEURS.get(self.prochain, 8)
        decalage_y, decalage_x = -2,5
        for x,y in next_piece:
            self.next_piece_window.addstr( y+decalage_y, decalage_x+x*2, "██", curses.color_pair(couleur))
            
        
        
    def draw_info_window(self):
                
        # Score Niveau
        self.info_window.addstr(9,  2, "┌─────────────┐")
        self.info_window.addstr(10, 2, f"│ Score: {self.score:4d} │")
        self.info_window.addstr(11, 2, f"│ Lignes:{self.lignes:4d} │")
        self.info_window.addstr(12, 2, f"│ Niveau:{self.niveau:4d} │")
        self.info_window.addstr(13, 2, "└─────────────┘")

        # Commandes
        self.info_window.addstr(15, 2, "COMMANDES:")
        self.info_window.addstr(16, 2, "← → : Déplacer")
        self.info_window.addstr(17, 2, "↓   : Descendre")
        self.info_window.addstr(18, 2, "s/d : Rotation")
        self.info_window.addstr(19, 2, "SPC : Hard drop")
        self.info_window.addstr(20, 2, "P   : Pause")
        self.info_window.addstr(21, 2, "Q   : Quitter")
        self.info_window.box()
        
    def draw_game_window(self):
        self.game_window.box()
        if self.ttm:
            for x, y in self.ttm.get_coords():
                if 0 <= x < self.HA and 0 <= y <= self.LA:
                    couleur = COULEURS.get(self.ttm.lettre, 9)
                    self.game_window.addstr(x+1 , y * 2, "██", curses.color_pair(couleur))
        
        for x in range(len(self.grille)):
            for y in range(len(self.grille[0])):
                if 0 <= x < self.HA and 0 <= y <= self.LA:
                    if self.grille[x][y] in TETRIMINOS :                        
                        couleur = COULEURS.get(self.grille[x][y], 9)
                        self.game_window.addstr(x+1 , y * 2, "██", curses.color_pair(couleur))
            
    def ajouter_tetrimino(self):
        lettre = self.prochain
        self.prochain = random.choice(T)
        self.ttm = Tetrimino(self, self.tetriminos[lettre], lettre)
        
        # Vérifier si on peut placer le tetrimino
        for x, y in self.ttm.get_coords():
            if self.grille[x][y] != 0:
                return False
        return True

    def supprimer_ligne(self):
        lignes = []
        for i in range(len(self.grille)-1):
            if not (0 in self.grille[i]):
                lignes.append(i)
                for j in range(1,len(self.grille[i])-1):
                    self.grille[i][j]='!'
        
        if lignes:
            self.lignes += len(lignes)
            self.score += len(lignes)**2 * 100
            
            # Mise à jour du niveau
            self.niveau = 1 + self.lignes // 10
            self.vitesse = max(0.1, 0.5 - (self.niveau - 1) * 0.05)
            
            self.game_window.erase()
            self.draw_game_window()
            self.game_window.noutrefresh()
            self.info_window.noutrefresh()
            self.next_piece_window.noutrefresh()
            curses.doupdate()
            time.sleep(0.8)
            
            self.grille = [elt for i, elt in enumerate(self.grille) if i not in lignes]
            self.grille = [[1]+[0]*self.LA+[1] for i in lignes] + self.grille
    
    def jouer(self):
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

        pause = False

        dernier_mouvement = time.time()
        self.ajouter_tetrimino()
        
        while not self.game_over:
            key = self.stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('p') or key == ord('P'):
                pause = not pause
                if pause:
                    self.game_window.addstr(self.HA // 2 + 2, self.LA - 2, " PAUSE ", 
                                       curses.A_REVERSE | curses.A_BOLD)
                    self.game_window.refresh()
                continue
            

            if not pause:
                if key == curses.KEY_LEFT and self.ttm.peut_deplacer(GAUCHE):
                    self.ttm.deplacer(GAUCHE)
                elif key == curses.KEY_RIGHT and self.ttm.peut_deplacer(DROITE):
                    self.ttm.deplacer(DROITE)
                elif key == curses.KEY_DOWN and self.ttm.peut_deplacer(BAS):
                    self.ttm.deplacer(BAS)
                elif key == ord('s') or key == ord('S'):
                    if self.ttm.peut_tourner(ROTATION_G):
                        self.ttm.tourner(ROTATION_G)
                elif key == ord('d') or key == ord('D'):
                    if self.ttm.peut_tourner(ROTATION_D):
                        self.ttm.tourner(ROTATION_D)
                elif key == ord(' '):  # Hard drop
                    while self.ttm.peut_deplacer(BAS):
                        self.ttm.deplacer(BAS)
                        
           
            if not pause and time.time() - dernier_mouvement > self.vitesse:
                if self.ttm.peut_deplacer(BAS):
                    self.ttm.deplacer(BAS)
                else:
                    self.ttm.poser()
                    self.ttm = None
                    self.supprimer_ligne()
                    if not self.ajouter_tetrimino():
                        self.game_over = True
                        self.stdscr.addstr(self.HA // 2 + 2, self.LA, 
                                         " GAME OVER! ", 
                                         curses.A_REVERSE | curses.A_BOLD)
                        self.stdscr.addstr(self.HA // 2 + 4, self.LA, 
                                         f"Score final: {self.score}", 
                                         curses.A_BOLD)
                        self.stdscr.refresh()
                        time.sleep(3)
                dernier_mouvement = time.time()

            time.sleep(0.01)
            self.game_window.erase()
            self.draw_game_window()
            self.next_piece_window.erase()
            self.draw_next_piece_window()
            self.info_window.erase()
            self.draw_info_window()
            self.game_window.noutrefresh()
            self.info_window.noutrefresh()
            self.next_piece_window.noutrefresh()
            curses.doupdate()
            
            
def main(stdscr):
    jeu = Termtris(stdscr)
    jeu.jouer()


if __name__ == "__main__":
    curses.wrapper(main)
