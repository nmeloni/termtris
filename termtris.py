#########################
#
#
#  termtris.py
#
#  author: Nicolas Méloni
#  Université  de toulon
#  11 Octobre 2017
#
#########################


import random
from copy import deepcopy
HA,LA=21,12
BAS, GAUCHE, DROITE = (1,0),(0,-1),(0,1)
ROTATION_G,ROTATION_D = -1, 1
TOUCHES = {'\x1b[B':BAS,'\x1b[C':DROITE,'\x1b[D':GAUCHE,
           'q':ROTATION_G,'d':ROTATION_D}
T='IOTLJZS'
TETRIMINOS = {
            'I':[[(1,5),(1,6),(1,7),(1,8)],
                 [(0,7),(1,7),(2,7),(3,7)],
                 [(2,5),(2,6),(2,7),(2,8)],
                 [(0,6),(1,6),(2,6),(3,6)]],
           'O':[[(1,6),(1,7),(0,6),(0,7)]],
           'T':[[(0,7),(1,6),(1,7),(1,8)],
                [(0,7),(1,7),(2,7),(1,8)],
                [(1,6),(1,7),(2,7),(1,8)],
                [(0,7),(1,7),(2,7),(1,6)]],
           'L':[[(1,6),(1,7),(1,8),(0,8)],
                [(0,7),(1,7),(2,7),(2,8)],
                [(2,6),(1,6),(1,7),(1,8)],
                [(0,6),(0,7),(1,7),(2,7)]],
           'J':[[(0,6),(1,6),(1,7),(1,8)],
                [(0,7),(1,7),(2,7),(0,8)],
                [(1,6),(1,7),(1,8),(2,8)],
                [(2,6),(0,7),(1,7),(2,7)]],
           'Z':[[(1,7),(1,8),(0,6),(0,7)],
                [(1,7),(1,8),(2,7),(0,8)],
                [(1,7),(1,6),(2,7),(2,8)],
                [(1,7),(0,7),(1,6),(2,6)]],
           'S':[[(1,6),(1,7),(0,7),(0,8)],
                [(1,7),(0,7),(1,8),(2,8)],
                [(1,7),(1,8),(2,7),(2,6)],
                [(1,7),(0,6),(1,6),(2,7)]] }

class termtris:
    def __init__(self,h,l):
        """
        Interface du jeu termtris
        """
        self.HA, self.LA = h,l 
        self.grille =  [[1]+[0]*l+[1] for i in range(h)]+[[1]*(l+2)]
        self.score = 0
        self.tetriminos = TETRIMINOS
        self.ttm = None
        

    def affichage(self):
        jeu="\n\n"
        for l in self.grille[:-1]:
            ligne='|'
            for e in l[1:-1]:
                if e==1 or e==2:
                    ligne+='*'
                elif e=='!':
                    ligne+='!'
                else:
                    ligne+=' '
            jeu+=ligne+'|\n'
        jeu+="-"*(self.LA+2)
        jeu+="\nscore:{:8}".format(self.score)
        print(jeu)
        

    def ajouter_tetrimino(self,t):
        self.ttm = tetrimino(self, self.tetriminos[t])
        for i,j in self.ttm.piece[self.ttm.o]:
            if self.grille[i][j]==1:
                return False
            else:
                self.grille[i][j]=2
        return True

    def supprimer_ligne(self):
        lignes = []
        for i in range(len(self.grille)-1):
            if not (0 in self.grille[i]):
                print("ligne:",i)
                lignes.append(i)
                for j in range(1,len(self.grille[i])-1):
                    self.grille[i][j]='!'
       
        self.affichage()
        input()
        if lignes:
            deb,fin=lignes[0],lignes[-1]
            self.score += len(lignes)
            self.grille = self.grille[:deb]+self.grille[fin+1:]
            self.grille = [[1]+[0]*self.LA+[1] for i in lignes] + self.grille


    def manuel(self):
        print("\n   *** Termtris ***\n"+
              "\n"+
              "Tetris dans un terminal!!\n\n"+
              "Deplacements:\n"
              "------------\n\n"
              "gauche:             fleche gauche\n"+
              "droite:             fleche droite\n"+
              "bas:                fleche bas\n"+
              "rotation gauche:    q\n"+
              "rotation droite:    d\n"+
              "----------------------------------\n"
              )
    
    def jouer(self):
        self.score = 0
        self.ajouter_tetrimino(random.choice(T))
        perdu = False
        self.manuel()
        input()
        while not perdu:
            self.affichage()
            k = input(": ")
            if k in TOUCHES:
                if k in "qd":
                    if self.ttm.peut_tourner(TOUCHES[k]):
                        self.ttm.tourner(TOUCHES[k])
                elif k in ['\x1b[B','\x1b[C','\x1b[D']:
                    if self.ttm.peut_deplacer(TOUCHES[k]):
                        self.ttm.deplacer(TOUCHES[k])

            if self.ttm.peut_deplacer(BAS):
                self.ttm.deplacer(BAS)
            else:
                self.ttm.poser()
                self.supprimer_ligne()
                
                if not self.ajouter_tetrimino(random.choice(T)):
                    perdu = True
                    print("\nPERDU  q(Oô)p")
                    
class tetrimino:
    def __init__(self, jeu, piece):
        #coordonnées et orientatio de la piece
        self.jeu = jeu
        self.x,self.y,self.o = 0,0,0
        self.piece = piece
        

    def peut_deplacer(self, direction):
        piece = self.piece[self.o]       
        for i,j in piece:
            x = i+self.x+direction[0]
            y = j+self.y+direction[1]
            if self.jeu.grille[x][y] == 1:
                return False
        return True

    def peut_tourner(self, rotation):
        piece = self.piece[(self.o+rotation) % len(self.piece)]
        for i,j in piece:
            if self.jeu.grille[i+self.x][j+self.y] == 1:
                return False
        return True

    def deplacer(self, direction):
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]
        piece = self.piece[self.o]
        for i,j in piece:
            self.jeu.grille[i+self.x][j+self.y] = 0
        for i,j in piece:
            self.jeu.grille[i+new_x][j+new_y] =  2
        self.x = new_x
        self.y = new_y

    def tourner(self, rotation):
        new_o = (self.o+rotation) % len(self.piece)
        piece = self.piece[self.o]
        new_piece = self.piece[new_o]
        for i,j in piece:
            self.jeu.grille[i+self.x][j+self.y] = 0
        for i,j in new_piece:
            self.jeu.grille[i+self.x][j+self.y] = 2
        self.o = new_o

    def poser(self):
        piece = self.piece[self.o]
        for i,j in piece:
            x = i+self.x
            y = j+self.y
            self.jeu.grille[x][y]=1
            
if __name__=="__main__":
    termtris = termtris(HA,LA)
    termtris.jouer()
