# Pychess board.py

from piece import *
import time
import os # for clear ou cls

class Board:
    
    "The chess board"
    
    # Names of the 64 sqares
    coord=[
        'a8','b8','c8','d8','e8','f8','g8','h8',
        'a7','b7','c7','d7','e7','f7','g7','h7',
        'a6','b6','c6','d6','e6','f6','g6','h6',
        'a5','b5','c5','d5','e5','f5','g5','h5',
        'a4','b4','c4','d4','e4','f4','g4','h4',
        'a3','b3','c3','d3','e3','f3','g3','h3',
        'a2','b2','c2','d2','e2','f2','g2','h2',
        'a1','b1','c1','d1','e1','f1','g1','h1',
        ]

    ####################################################################
    
    def __init__(self):
        self.init()
    
    ####################################################################
    
    def init(self):
        
        "Init the chess board at starting position"
        
        # Chessboard has 64 squares, numbered from 0 to 63 (a8 to h1)
        # Placing pieces ('cases' is 'square' in french :)
        self.cases = [
            Piece('TOUR','noir'),Piece('CAVALIER','noir'),Piece('FOU','noir'),Piece('DAME','noir'),Piece('ROI','noir'),Piece('FOU','noir'),Piece('CAVALIER','noir'),Piece('TOUR','noir'),
            Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),Piece('PION','noir'),
            Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),
            Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),
            Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),
            Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),Piece(),
            Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),Piece('PION','blanc'),
            Piece('TOUR','blanc'),Piece('CAVALIER','blanc'),Piece('FOU','blanc'),Piece('DAME','blanc'),Piece('ROI','blanc'),Piece('FOU','blanc'),Piece('CAVALIER','blanc'),Piece('TOUR','blanc')
            ]
            
        self.side2move='blanc'
        self.ep=-1 # the number of the square where to take 'en passant'
        self.history=[] # the moves history
        self.ply=0 # half-move number since the start

        # Castle rights
        self.white_can_castle_56=True
        self.white_can_castle_63=True
        self.black_can_castle_0=True
        self.black_can_castle_7=True    
    
    ####################################################################

    def gen_moves_list(self,color='',dontCallIsAttacked=False):
        
        """Returns all possible moves for the requested color.
        If color is not given, it is considered as the side to move.
        dontCallIsAttacked is a boolean flag to avoid recursive calls,
        due to the actually wrotten is_attacked() function calling
        this gen_moves_list() function.
        A move is defined as it :
        - the number of the starting square (pos1)
        - the number of the destination square (pos2)
        - the name of the piece to promote '','q','r','b','n'
          (queen, rook, bishop, knight)
        """
        
        if(color==''):
            color=self.side2move
        mList=[]
        
        # For each 'piece' on the board (pos1 = 0 to 63)
        for pos1,piece in enumerate(self.cases):
                
            # Piece (or empty square) color is not the wanted ? pass
            if piece.couleur!=color:
                continue
            
            if(piece.nom=='ROI'): # KING
                mList+=piece.pos2_roi(pos1,self.oppColor(color),self,dontCallIsAttacked)
                continue
                
            elif(piece.nom=='DAME'): # QUEEN = ROOK + BISHOP moves !
                mList+=piece.pos2_tour(pos1,self.oppColor(color),self)
                mList+=piece.pos2_fou(pos1,self.oppColor(color),self)
                continue
                
            elif(piece.nom=='TOUR'): # ROOK
                mList+=piece.pos2_tour(pos1,self.oppColor(color),self)
                continue
                
            elif(piece.nom=='CAVALIER'): # KNIGHT
                mList+=piece.pos2_cavalier(pos1,self.oppColor(color),self)
                continue
                
            elif(piece.nom=='FOU'): # BISHOP
                mList+=piece.pos2_fou(pos1,self.oppColor(color),self)
                continue
                
            if(piece.nom=='PION'): # PAWN
                mList+=piece.pos2_pion(pos1,piece.couleur,self)
                continue
                
        return mList
    
    def domove(self,depart,arrivee,promote):
        
        """Move a piece on the board from the square numbers
        'depart' to 'arrivee' (0..63) respecting rules :
        - prise en passant
        - promote and under-promote
        - castle rights
        Returns :
        - TRUE if the move do not let king in check
        - FALSE otherwise and undomove is done.
        """

		# Informations to save in the history moves
        pieceDeplacee=self.cases[depart] # moved piece
        piecePrise=self.cases[arrivee] # taken piece, can be null : Piece()
        isEp=False # will be used to undo a ep move
        histEp=self.ep # saving the actual ep square (-1 or square number TO)
        hist_roque_56=self.white_can_castle_56
        hist_roque_63=self.white_can_castle_63
        hist_roque_0=self.black_can_castle_0
        hist_roque_7=self.black_can_castle_7       
        flagViderEp=True # flag to erase ep or not : if the pawn moved is not taken directly, it can't be taken later
        
        # Moving piece
        self.cases[arrivee]=self.cases[depart]
        self.cases[depart]=Piece()
        
        self.ply+=1
                
        # a PAWN has been moved -------------------------------------
        if(pieceDeplacee.nom=='PION'):
            
            # White PAWN
            if(pieceDeplacee.couleur=='blanc'):
                
                # If the move is "en passant"
                if(self.ep==arrivee):
                    piecePrise=self.cases[arrivee+8] # take black pawn
                    self.cases[arrivee+8]=Piece()
                    isEp=True

                # The white pawn moves 2 squares from starting square
                # then blacks can take "en passant" next move
                elif(self.ROW(depart)==6 and self.ROW(arrivee)==4):
                    self.ep=arrivee+8
                    flagViderEp=False
		
            # Black PAWN
            else:
                
                if(self.ep==arrivee):
                    piecePrise=self.cases[arrivee-8]
                    self.cases[arrivee-8]=Piece()
                    isEp=True

                elif(self.ROW(depart)==1 and self.ROW(arrivee)==3):
                    self.ep=arrivee-8
                    flagViderEp=False
                    
        # a ROOK has been moved--------------------------------------
        # update castle rights
        
        elif(pieceDeplacee.nom=='TOUR'):
            
            # White ROOK
            if(pieceDeplacee.couleur=='blanc'):
                if(depart==56):
                    self.white_can_castle_56=False
                elif(depart==63):
                    self.white_can_castle_63=False
                
            # Black ROOK
            else:
                if(depart==0):
                    self.black_can_castle_0=False
                elif(depart==7):
                    self.black_can_castle_7=False
                
        # a KING has been moved-----------------------------------------
        
        elif(pieceDeplacee.nom=='ROI'):
            
            # White KING
            if(pieceDeplacee.couleur=='blanc'):    
                
                # moving from starting square
                if(depart==60):
                    # update castle rights
                    self.white_can_castle_56=False
                    self.white_can_castle_63=False                    

                    # If castling, move the rook
                    if(arrivee==58):
                        self.cases[56]=Piece()
                        self.cases[59]=Piece('TOUR','blanc')

                    elif(arrivee==62):
                        self.cases[63]=Piece()
                        self.cases[61]=Piece('TOUR','blanc')
                
            # Black KING
            else:                

                if(depart==4):
                    self.black_can_castle_0=False
                    self.black_can_castle_7=False                    

                    if(arrivee==6):
                        self.cases[7]=Piece()
                        self.cases[5]=Piece('TOUR','noir')

                    elif(arrivee==2):
                        self.cases[0]=Piece()
                        self.cases[3]=Piece('TOUR','noir')                
        
        # End pieces cases-----------------------------------------------
                
        # Any move cancels the ep move
        if(flagViderEp==True):
            self.ep=-1
            
        # Promote : the pawn is changed to requested piece
        if(promote!=''):
            if(promote=='q'):
                self.cases[arrivee]=Piece('DAME',self.side2move)
            elif(promote=='r'):
                self.cases[arrivee]=Piece('TOUR',self.side2move)
            elif(promote=='n'):
                self.cases[arrivee]=Piece('CAVALIER',self.side2move)
            elif(promote=='b'):
                self.cases[arrivee]=Piece('FOU',self.side2move)

        # Change side to move
        self.changeTrait()
            
        # Save move to the history list
        self.history.append((depart,\
        arrivee,\
        pieceDeplacee,\
        piecePrise,\
        isEp,\
        histEp,\
        promote,\
        hist_roque_56,\
        hist_roque_63,\
        hist_roque_0,\
        hist_roque_7))
		
        # If the move lets king in check, undo it and return false
        if(self.in_check(self.oppColor(self.side2move))):
            self.undomove()
            return False
            
        return True
        
    ####################################################################
    
    def undomove(self):
        
        if(len(self.history)==0):
            print('No move played')
            return

        # The last move in history is : self.historique[-1]
        lastmove=self.history[-1]
        
        pos1=lastmove[0]
        pos2=lastmove[1]
        piece_deplacee=lastmove[2]
        piece_prise=lastmove[3]
        isEp=lastmove[4]
        ep=lastmove[5]
        promote=lastmove[6]
        self.white_can_castle_56=lastmove[7]
        self.white_can_castle_63=lastmove[8]
        self.black_can_castle_0=lastmove[9]
        self.black_can_castle_7 =lastmove[10]
        
        self.ply-=1

        # Change side to move
        self.changeTrait()
                
        # Replacing piece on square number 'pos1'
        self.cases[pos1]=self.cases[pos2]
        
        # Square where we can take "en pasant"
        self.ep=ep
        
        # If undoing a promote, the piece was a pawn
        if(promote!=''):
            self.cases[pos1]=Piece('PION',self.side2move)

        # Replacing capture piece on square 'pos2'
        self.cases[pos2]=piece_prise

        # Switch the piece we have replaced to 'pos1'-------------------
        if(self.cases[pos1].nom=='PION'):
            # If a pawn has been taken "en passant", replace it
            if(isEp):
                self.cases[pos2]=Piece()
                if(self.cases[pos1].couleur=='noir'):
                    self.cases[pos2-8]=Piece('PION','blanc')
                else:
                    self.cases[pos2+8]=Piece('PION','noir')
                    
        # Replacing KING -----------------------------------------------
        elif(self.cases[pos1].nom=='ROI'):
            
            # White KING
            if(self.cases[pos1].couleur=='blanc'):
                # Replacing on initial square
                if(pos1==60):
                    # If the move was castle, replace ROOK
                    if(pos2==58):
                        self.cases[56]=Piece('TOUR','blanc')
                        self.cases[59]=Piece()
                    elif(pos2==62):
                        self.cases[63]=Piece('TOUR','blanc')
                        self.cases[61]=Piece()
            # Black KING
            else:
                if(pos1==4):
                    if(pos2==2):
                        self.cases[0]=Piece('TOUR','noir')
                        self.cases[3]=Piece()
                    elif(pos2==6):
                        self.cases[7]=Piece('TOUR','noir')
                        self.cases[5]=Piece()
        # End switch piece----------------------------------------------
 
        # Delete the last move from history
        self.history.pop()
            
    ####################################################################
    
    def changeTrait(self):
        
        "Change the side to move"
        
        if(self.side2move=='blanc'):
            self.side2move='noir'
        else:
            self.side2move='blanc'   
            
    ####################################################################
    
    def oppColor(self,c):
        
        "Returns the opposite color of the 'c' color given"
        
        if(c=='blanc'):
            return 'noir'
        else:
            return 'blanc'           

    ####################################################################

    def in_check(self,couleur):
        
        """Returns TRUE or FALSE 
        if the KING of the given 'color' is in check"""
        
        # Looking for the id square where is the king
        # sure, we can code better to avoid this and win kn/s...
        for i in range(0,64):
            if(self.cases[i].nom=='ROI' and self.cases[i].couleur==couleur):
                pos=i
                break

        return self.is_attacked(pos,self.oppColor(couleur))
        
    ####################################################################

    def is_attacked(self,pos,couleur):
        
        """Returns TRUE or FALSE if the square number 'pos' is a 
        destination square for the color 'couleur'.
        If so we can say that 'pos' is attacked by this side.
        This function is used for 'in check' and for castle moves."""
        
        mList=self.gen_moves_list(couleur,True)

        for pos1,pos2,promote in mList:
            if(pos2==pos):
                return True
        
        return False    
            
    ####################################################################
            
    def render(self):
        
        "Display the chessboard in console mode"
        os.system('cls' if os.name == 'nt' else 'clear')
   
        print('8',end='   ')
        i,y=1,7
        for piece in self.cases:
            if(piece.couleur=='noir'):
                print(piece.nom[0].lower(),end='   ')
            else:
                print(piece.nom[0],end='   ')
                                    
            if(i%8==0):
                print()
                print()
                if(y>0):
                    print(str(y),end='   ')
                y=y-1

            i+=1
        print('    a   b   c   d   e   f   g   h')
        
        print('Side to move : '+self.side2move)
        
        print()

        # Displaying moves done from the history
        self.showHistory()
        
    ####################################################################
    
    def caseStr2Int(self,c):
        
        """'c' given in argument is a square name like 'e2'
        "This functino returns a square number like 52"""

        err=(
        'The square name must be 2 caracters i.e. e2,e4,b1...',
        'Incorrect square name. Please enter i.e. e2,e4,b1...'
        )            
        letters=('a','b','c','d','e','f','g','h')
        numbers=('1','2','3','4','5','6','7','8')
                
        if(len(c)!=2):
            print(err[0])
            return -1
        
        if(c[0] not in letters):
            print(err[1])
            return -1
            
        if(c[1] not in numbers):
            print(err[1])
            return -1
            
        return self.coord.index(c)
        
    ####################################################################
    
    def caseInt2Str(self,i):
        
        """Given in argument : an integer between 0 and 63
        Returns a string like 'e2'"""

        err=(
        'Square number must be in 0 to 63',
        )            
        letters=('a','b','c','d','e','f','g','h')
        numbers=('1','2','3','4','5','6','7','8')
                
        if(i<0 or i>63):
            print(err[0])
            return

        return self.coord[i] 
        
    ####################################################################
    
    @staticmethod
    def ROW(x):
        """ROW returns the number of the row from 0(a8-h8) to 7(a1-h1)
        in which is the square 'x'"""
        return (x >> 3)

    ####################################################################

    @staticmethod
    def COL(x):
        """COL returns the number of the colon (from 0 to 7)
        in which is the square 'x'"""
        return (x & 7)
        
    ####################################################################
    
    def showHistory(self):
        
        "Displays the history of the moves played"
        
        if(len(self.history)==0):
            return
        
        print()
        aff=True
        for (depart,\
        arrivee,\
        pieceDeplacee,\
        piecePrise,\
        isEp,\
        histEp,\
        promote,\
        roque56,\
        roque63,\
        roque0,\
        roque7) in self.history:
            a=self.caseInt2Str(depart)
            b=self.caseInt2Str(arrivee)
            if(promote!=''):
                b=b+promote
            if(aff==True):
                print("{}{} ".format(a,b),end='')
                aff=False
            else:
                print("{}{} ".format(a,b),end='')
                aff=True
        print()
        
    ###################################################################
    
    def evaluer(self):
        
        """A wonderful evaluate() function returning score"""
        
        WhiteScore=0
        BlackScore=0
        
        # Parsing the board squares from 0 to 63
        for pos1,piece in enumerate(self.cases):

            # Score ( using PESTO table )
            if(piece.couleur=='blanc'):
                WhiteScore+=piece.valeur
                
                if piece.nom == 'PION':
                # Assigning positional bonuses for pawns
                    pawn_position_bonus =  [   0,   0,   0,   0,   0,   0,  0,   0,
                                              98, 134,  61,  95,  68, 126, 34, -11,
                                              -6,   7,  26,  31,  65,  56, 25, -20,
                                             -14,  13,   6,  21,  23,  12, 17, -23,
                                             -27,  -2,  -5,  12,  17,   6, 10, -25,
                                             -26,  -4,  -4, -10,   3,   3, 33, -12,
                                             -35,  -1, -20, -23, -15,  24, 38, -22,
                                               0,   0,   0,   0,   0,   0,  0,   0]
                    WhiteScore += pawn_position_bonus[pos1]/200
                
                if piece.nom == 'CAVALIER':
                # Assigning positional bonuses for knights
                    knight_position_bonus = [-167, -89, -34, -49,  61, -97, -15, -107,
                                              -73, -41,  72,  36,  23,  62,   7,  -17,
                                              -47,  60,  37,  65,  84, 129,  73,   44,
                                               -9,  17,  19,  53,  37,  69,  18,   22,
                                              -13,   4,  16,  13,  28,  19,  21,   -8,
                                              -23,  -9,  12,  10,  19,  17,  25,  -16,
                                              -29, -53, -12,  -3,  -1,  18, -14,  -19,
                                             -105, -21, -58, -33, -17, -28, -19,  -23]
                    WhiteScore += knight_position_bonus[pos1]/200
                
                if piece.nom == 'FOU':
                # Assigning positional bonuses for bishops
                    bishop_position_bonus = [-29,   4, -82, -37, -25, -42,   7,  -8,
                                             -26,  16, -18, -13,  30,  59,  18, -47,
                                             -16,  37,  43,  40,  35,  50,  37,  -2,
                                              -4,   5,  19,  50,  37,  37,   7,  -2,
                                              -6,  13,  13,  26,  34,  12,  10,   4,
                                               0,  15,  15,  15,  14,  27,  18,  10,
                                               4,  15,  16,   0,   7,  21,  33,   1,
                                             -33,  -3, -14, -21, -13, -12, -39, -21]
                    WhiteScore += bishop_position_bonus[pos1]/200
                
                if piece.nom == 'TOUR':
                # Assigning positional bonuses for rooks
                    rook_position_bonus =  [ 32,  42,  32,  51, 63,  9,  31,  43,
                                             27,  32,  58,  62, 80, 67,  26,  44,
                                             -5,  19,  26,  36, 17, 45,  61,  16,
                                            -24, -11,   7,  26, 24, 35,  -8, -20,
                                            -36, -26, -12,  -1,  9, -7,   6, -23,
                                            -45, -25, -16, -17,  3,  0,  -5, -33,
                                            -44, -16, -20,  -9, -1, 11,  -6, -71,
                                            -19, -13,   1,  17, 16,  7, -37, -26]
                    WhiteScore += rook_position_bonus[pos1]/200
                
                if piece.nom == 'DAME':
                # Assigning positional bonuses for queen(s)
                    queen_position_bonus =  [-28,   0,  29,  12,  59,  44,  43,  45,
                                             -24, -39,  -5,   1, -16,  57,  28,  54,
                                             -13, -17,   7,   8,  29,  56,  47,  57,
                                             -27, -27, -16, -16,  -1,  17,  -2,   1,
                                              -9, -26,  -9, -10,  -2,  -4,   3,  -3,
                                             -14,   2, -11,  -2,  -5,   2,  14,   5,
                                             -35,  -8,  11,   2,   8,  15,  -3,   1,
                                              -1, -18,  -9,  10, -15, -25, -31, -50]
                    WhiteScore += queen_position_bonus[pos1]/200
                
                if piece.nom == 'ROI':
                # Assigning positional bonuses for king
                    king_position_bonus =   [-65,  23,  16, -15, -56, -34,   2,  13,
                                              29,  -1, -20,  -7,  -8,  -4, -38, -29,
                                              -9,  24,   2, -16, -20,   6,  22, -22,
                                             -17, -20, -12, -27, -30, -25, -14, -36,
                                             -49,  -1, -27, -39, -46, -44, -33, -51,
                                             -14, -14, -22, -46, -44, -30, -15, -27,
                                               1,   7,  -8, -64, -43, -16,   9,   8,
                                             -15,  36,  12, -54,   8, -28,  24,  14]
                    WhiteScore += king_position_bonus[pos1]/200
                
            else: 
                BlackScore+=piece.valeur
                
                if piece.nom == 'PION':
                # Assigning positional bonuses for pawns
                    pawn_position_bonus =  [   0,   0,   0,   0,   0,   0,  0,   0,
                                              98, 134,  61,  95,  68, 126, 34, -11,
                                              -6,   7,  26,  31,  65,  56, 25, -20,
                                             -14,  13,   6,  21,  23,  12, 17, -23,
                                             -27,  -2,  -5,  12,  17,   6, 10, -25,
                                             -26,  -4,  -4, -10,   3,   3, 33, -12,
                                             -35,  -1, -20, -23, -15,  24, 38, -22,
                                               0,   0,   0,   0,   0,   0,  0,   0]
                    BlackScore += pawn_position_bonus[pos1^56]/200
                
                if piece.nom == 'CAVALIER':
                # Assigning positional bonuses for knights
                    knight_position_bonus = [-167, -89, -34, -49,  61, -97, -15, -107,
                                              -73, -41,  72,  36,  23,  62,   7,  -17,
                                              -47,  60,  37,  65,  84, 129,  73,   44,
                                               -9,  17,  19,  53,  37,  69,  18,   22,
                                              -13,   4,  16,  13,  28,  19,  21,   -8,
                                              -23,  -9,  12,  10,  19,  17,  25,  -16,
                                              -29, -53, -12,  -3,  -1,  18, -14,  -19,
                                             -105, -21, -58, -33, -17, -28, -19,  -23]
                    BlackScore += knight_position_bonus[pos1^56]/200
                
                if piece.nom == 'FOU':
                # Assigning positional bonuses for bishops
                    bishop_position_bonus = [-29,   4, -82, -37, -25, -42,   7,  -8,
                                             -26,  16, -18, -13,  30,  59,  18, -47,
                                             -16,  37,  43,  40,  35,  50,  37,  -2,
                                              -4,   5,  19,  50,  37,  37,   7,  -2,
                                              -6,  13,  13,  26,  34,  12,  10,   4,
                                               0,  15,  15,  15,  14,  27,  18,  10,
                                               4,  15,  16,   0,   7,  21,  33,   1,
                                             -33,  -3, -14, -21, -13, -12, -39, -21]
                    BlackScore += bishop_position_bonus[pos1^56]/200
                
                if piece.nom == 'TOUR':
                # Assigning positional bonuses for rooks
                    rook_position_bonus =  [ 32,  42,  32,  51, 63,  9,  31,  43,
                                             27,  32,  58,  62, 80, 67,  26,  44,
                                             -5,  19,  26,  36, 17, 45,  61,  16,
                                            -24, -11,   7,  26, 24, 35,  -8, -20,
                                            -36, -26, -12,  -1,  9, -7,   6, -23,
                                            -45, -25, -16, -17,  3,  0,  -5, -33,
                                            -44, -16, -20,  -9, -1, 11,  -6, -71,
                                            -19, -13,   1,  17, 16,  7, -37, -26]
                    BlackScore += rook_position_bonus[pos1^56]/200
                
                if piece.nom == 'DAME':
                # Assigning positional bonuses for queen(s)
                    queen_position_bonus =  [-28,   0,  29,  12,  59,  44,  43,  45,
                                             -24, -39,  -5,   1, -16,  57,  28,  54,
                                             -13, -17,   7,   8,  29,  56,  47,  57,
                                             -27, -27, -16, -16,  -1,  17,  -2,   1,
                                              -9, -26,  -9, -10,  -2,  -4,   3,  -3,
                                             -14,   2, -11,  -2,  -5,   2,  14,   5,
                                             -35,  -8,  11,   2,   8,  15,  -3,   1,
                                              -1, -18,  -9,  10, -15, -25, -31, -50]
                    BlackScore += queen_position_bonus[pos1^56]/200
                
                if piece.nom == 'ROI':
                # Assigning positional bonuses for king
                    king_position_bonus =   [-65,  23,  16, -15, -56, -34,   2,  13,
                                              29,  -1, -20,  -7,  -8,  -4, -38, -29,
                                              -9,  24,   2, -16, -20,   6,  22, -22,
                                             -17, -20, -12, -27, -30, -25, -14, -36,
                                             -49,  -1, -27, -39, -46, -44, -33, -51,
                                             -14, -14, -22, -46, -44, -30, -15, -27,
                                               1,   7,  -8, -64, -43, -16,   9,   8,
                                             -15,  36,  12, -54,   8, -28,  24,  14]
                    BlackScore += king_position_bonus[pos1^56]/200

        if(self.side2move=='blanc'):
            return WhiteScore-BlackScore
        else:
            return BlackScore-WhiteScore
    
    ####################################################################