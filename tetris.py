from random import randrange
from copy import deepcopy
HA,LA=22,12
T='IOTLJZS'
grille=[ [1]+[0]*LA+[1] for i in range(HA)]+[[1]*LA]
tetriminos={'I':[[0,5],[0,6],[0,7],[0,8]],
           'O':[[1,6],[1,7],[0,6],[0,7]],
           'T':[[1,7],[0,6],[0,7],[0,8]],
           'L':[[1,6],[0,6],[0,7],[0,8]],
           'J':[[1,8],[0,6],[0,7],[0,8]],
           'Z':[[1,7],[1,8],[0,6],[0,7]],
           'S':[[1,6],[1,7],[0,7],[0,8]]}
tetrimino=[]

def affiche_grille():
    jeu=""
    for l in grille[:-1]:
        ligne='|'
        for e in l[1:-1]:
            if e:
                ligne+=str('*')
            else:
                ligne+=' '
        jeu+=ligne+'|\n'
    jeu+="-"*(LA+2)
    print(jeu)

def ajoute_tetrimino(t):
    global tetrimino
    tetrimino=deepcopy(tetriminos[t])
    for i,j in tetrimino:
        if grille[i][j]==1:
            return False
        else:
            grille[i][j]=2
    return True
    
def descend():
    global tetrimino
    for i,j in tetrimino:
        if grille[i+1][j]==1:
            return False
    return True

def gauche():
    global tetrimino
    for i,j in tetrimino:
        if grille[i][j-1]==1:
            return False
    return True

def droite():
    global tetrimino
    for i,j in tetrimino:
        if grille[i][j+1]==1:
            return False
    return True

def move_down():
    global tetrimino
    for c in range(len(tetrimino)):
        i,j=tetrimino[c][0],tetrimino[c][1]
        grille[i][j]=0
        grille[i+1][j]=2
        tetrimino[c][0]+=1

def move_left():
    global tetrimino
    for c in range(len(tetrimino)):
        i,j=tetrimino[c][0],tetrimino[c][1]
        grille[i][j]=0
        grille[i][j-1]=2
        tetrimino[c][1]-=1

def move_right():
    global tetrimino
    for c in range(len(tetrimino)):
        i,j=tetrimino[c][0],tetrimino[c][1]
        grille[i][j]=0
        grille[i][j+1]=2
        tetrimino[c][1]+=1

    
def pose():
    for i,j in tetrimino:
        grille[i][j]=1
            
if __name__=="__main__":
    ajoute_tetrimino(T[randrange(7)])
    affiche_grille()
    while True:
        affiche_grille()
        k=input()
        if k=="\x1b[B" and descend():
            move_down()
        elif k=="\x1b[C" and droite():
            move_right()
        elif k=="\x1b[D" and gauche():
            move_left()
            
        if descend():
            move_down()
        else:
            pose()
            if not ajoute_tetrimino(T[randrange(7)]):
                print("Perdu")
                break
        
    
    
