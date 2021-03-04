import subprocess
import random

class ChessGame:
    def __init__(self,fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.loadFEN(fen)
    def loadFEN(self,fen):
        pos=[]
        rec=fen.split(" ")
        pc=list("pnbrqk")
        P={k:v for k,v in zip(pc,range(1,len(pc)+1))}
        for i in rec[0].split("/"):
            pos.append([])
            for j in i:
                if j in list("12345678"):
                    pos[-1] += [0 for _ in range(int(j))]
                elif j in pc:
                    pos[-1].append((0,P[j]))
                elif j.lower() in pc:
                    pos[-1].append((1,P[j.lower()]))
        opt=[int(rec[1]=="w"),[0,0,0,0]]
        for i in rec[2]:
            if i=="-":
                break
            opt[1][{"K":0,"Q":1,"k":2,"q":3}[i]]=1
        if rec[3]!="-":
            pos[8-int(rec[3][1])][{k:v for k,v in zip(list("abcdefgh"),range(8))}[rec[3][0]]]=1
        opt.append(int(rec[4]))
        opt.append(int(rec[5]))
        self.pos=[pos,opt]
    def getFEN(self):
        fen=""
        t=0
        ep="-"
        pc=list("pnbrqk")
        P={k:v for v,k in zip(pc,range(1,len(pc)+1))}
        for i,ch1 in zip(self.pos[0],"87654321"):
            for j,ch2 in zip(i,"abcdefgh"):
                if j in [0,1]:
                    t+=1
                    if j==1:
                        ep=ch2+ch1
                elif (type(j)==tuple):
                    if t:
                        fen+=str(t)
                        t=0
                    c=P[j[1]]
                    if j[0]:
                        c=c.upper()
                    fen+=c
            if t:
                fen+=str(t)
                t=0
            fen+="/"
        fen=fen[:-1]+" "+"w"*int(self.pos[1][0])+"b"*int(1-self.pos[1][0])+" "+"K"*self.pos[1][1][0]+"Q"*self.pos[1][1][1]+"k"*self.pos[1][1][2]+"q"*self.pos[1][1][3]+"-"*int(not (sum(self.pos[1][1])))+" "+ep+" "+str(self.pos[1][2])+" "+str(self.pos[1][3])
        return fen
    def table(self):
        a=" a b c d e f g h\n"
        b=self.isOver()
        if b==-1:
            a="-"+a
        elif b==1:
            a="+"+a
        elif b==1/2:
            a="0"+a
        else:
            a=" "+a
        pc=list("pnbrqk")
        P={k:v for v,k in zip(pc,range(1,len(pc)+1))}
        for i,r in zip(self.pos[0],"87654321"):
            a+=r+" "
            for j in i:
                if j in [0,1]:
                    a+="  "
                else:
                    t=P[j[1]]
                    if j[0]:
                        t=t.upper()
                    a+=t+" "
            a=a[:-1]+"\n"
        return a[:-1]
    d=lambda self:print(self.table())
    def isOver(self):
        pb=[]
        pw=[]
        for i in self.pos[0]:
            for j in i:
                if (type(j)!=tuple):
                    continue
                if j[0]:
                    pw.append(j[1])
                else:
                    pb.append(j[1])
        if (pb==[6]) and (pw==[6]):
            return 1/2
        for i,i1 in zip(self.pos[0],range(8)):
            for j,j1 in zip(i,range(8)):
                if (type(j)==tuple) and (self.pos[1][0]==j[0]):
                    for i2 in range(8):
                        for j2 in range(8):
                            if self.isLegal([i1,j1],[i2,j2]) and (self.pos[1][2]<50):
                                return 0
        if self.isCheck(self.pos[1][0],self.pos[0]) and (self.pos[1][2]<50):
            return 1-self.pos[1][0]*2
        else:
            return 1/2
    def isCheck(self,color,pos):
        br=False
        for i,kRow in zip(pos,range(8)):
            for j,kCol in zip(i,range(8)):
                if j==(color,6):
                    br=True
                    break
            if br:
                break
        for i,row in zip(pos,range(8)):
            for j,col in zip(i,range(8)):
                if (j in [0,1]):
                    continue
                if j[0]==color:
                    continue
                rm = (kRow==row) or (kCol==col)
                bm = abs(kRow-row)==abs(kCol-col)
                if (j[1]==2) and ((kRow,kCol) in [(row+1,col+2),(row-1,col+2),(row+1,col-2),(row-1,col-2),(row+2,col+1),(row-2,col+1),(row+2,col-1),(row-2,col-1)]):
                    return True
                if (j[1]==1) and ((kRow,kCol) in [(row+color*2-1,col+1),(row+color*2-1,col-1)]):
                    return True
                if (j[1]==6) and ((kRow,kCol) in [(row+1,col),(row-1,col),(row+1,col-1),(row,col-1),(row-1,col-1),(row+1,col+1),(row,col+1),(row-1,col+1)]):
                    return True
                if j[1] in [1,2,6]:
                    continue
                if ((j[1]==5) and (not (rm or bm))) or ((j[1]==4) and (not rm)) or ((j[1]==3) and (not bm)):
                    continue
                if (j[1]==4) or ((j[1]==5) and rm):
                    if kRow==row:
                        rowMove=0
                        colMove=int(col<kCol)*2-1
                    else:
                        rowMove=int(row<kRow)*2-1
                        colMove=0
                elif (j[1]==3) or ((j[1]==5) and bm):
                    rowMove=int(row<kRow)*2-1
                    colMove=int(col<kCol)*2-1
                t1,t2=row+rowMove,col+colMove
                st=True
                while (t1!=kRow) or (t2!=kCol):
                    if not (pos[t1][t2] in [0,1]):
                        st=False
                        break
                    t1+=rowMove
                    t2+=colMove
                if st:
                    return True
        return False
    def isLegal(self,c1,c2,retPos=False,prom=5):
        try:
            c1p = self.pos[0][c1[0]][c1[1]]
            c2p = self.pos[0][c2[0]][c2[1]]
        except:
            return False
        if c1==c2:
            return False
        if c1p in [0,1]:
            return False
        if (c1p[0]!=self.pos[1][0]):
            return False
        if c1p[0]!=self.pos[1][0]:
            return False
        if (type(c2p)==tuple) and (c1p[0]==c2p[0]) and ((c1p[1]!=6) or (c2p[1]!=4)):
            return False
        tfex=[-1,-1]
        LPos=[[j for j in i] for i in self.pos[0][:]]
        LOpt=[self.pos[1][:][0],self.pos[1][1][:]]+self.pos[1][:][2:]
        LOpt[2]+=1
        if (type(c2p)==tuple) or (c2p==1):
            LOpt[2]=0
        if LOpt[0]==0:
            LOpt[3]+=1
        if (c1p[1]==2):
            if (not (c2 in [[c1[0]+1,c1[1]+2],[c1[0]-1,c1[1]+2],[c1[0]+1,c1[1]-2],[c1[0]-1,c1[1]-2],[c1[0]+2,c1[1]+1],[c1[0]-2,c1[1]+1],[c1[0]+2,c1[1]-1],[c1[0]-2,c1[1]-1]])):
                return False
            LPos[c1[0]][c1[1]]=0
            LPos[c2[0]][c2[1]]=c1p
        if (c1p[1]==1):
            if (c2[1]==c1[1]) and ((c1[0]+1-c1p[0]*2==c2[0]) or (((c1p[0]==0) and (c1[0]==1)) or ((c1p[0]==1) and (c1[0]==6))) and (c1[0]+2-c1p[0]*4==c2[0]) and (self.pos[0][c1[0]+1-c1p[0]*2][c1[1]]==0)) and (c2p==0):
                LPos[c1[0]][c1[1]]=0
                LPos[c2[0]][c2[1]]=c1p
                if (c1[0]+2-c1p[0]*4==c2[0]):
                    LPos[c1[0]+1-c1p[0]*2][c1[1]]=1
                    tfex=[c1[0]+1-c1p[0]*2,c1[1]]
            elif (c1[0]+1-c1p[0]*2==c2[0]) and (abs(c2[1]-c1[1])==1) and ((type(c2p)==tuple) or (c2p==1)):
                LPos[c1[0]][c1[1]]=0
                LPos[c2[0]][c2[1]]=c1p
                if c2p==1:
                    LPos[c1[0]][c2[1]]=0
            else:
                return False
            if c2[0]==7*(1-c1p[0]):
                if not (prom in [2,3,4,5]):
                    return False
                LPos[c2[0]][c2[1]]=(c1p[0],prom)
            LOpt[2]=0
        if (c1p[1]==6):
            if ((type(c2p)==tuple) and (c2p[1]==4) and (c2p[0]==c1p[0])) or (abs(c2[1]-c1[1])==2 and (c2[0]==c1[0]) and (LPos[c1[0]][c1[1]+2-int(c1[1]>c2[1])*4]==0)):
                if self.isCheck(c1p[0],self.pos[0]):
                    return False
                if (abs(c2[1]-c1[1])==2) and (c2[0]==c1[0]) and (LPos[c1[0]][c1[1]+2-int(c1[1]>c2[1])*4]==0):
                    if c1[1]>c2[1]:
                        if (c2[1]<2) or (LPos[c2[0]][c2[1]-2]!=(LOpt[0],4)):
                            return False
                        c2=[c2[0],c2[1]-2]
                    else:
                        if (c2[1]==7) or (LPos[c2[0]][c2[1]+1]!=(LOpt[0],4)):
                            return False
                        c2=[c2[0],c2[1]+1]
                    c2p=LPos[c2[0]][c2[1]]
                if (((c2[1]-c1[1]) == 3) and (LOpt[1][2-2*c1p[0]]==1)):
                    tPos = [[j for j in i] for i in LPos]
                    for i in range(1,3):
                        if tPos[c1[0]][c1[1]+i] != 0:
                            return False
                        tPos[c1[0]][c1[1]+i]=tPos[c1[0]][c1[1]+i-1]
                        tPos[c1[0]][c1[1]+i-1]=0
                        if self.isCheck(c1p[0],tPos):
                            return False
                    LPos[c1[0]][c1[1]+2]=c1p
                    LPos[c1[0]][c1[1]]=0
                    LPos[c1[0]][c1[1]+1]=c2p
                    LPos[c2[0]][c2[1]]=0
                    LOpt[1][2-2*c1p[0]]=0
                    LOpt[1][3-2*c1p[0]]=0
                elif ((c2[1]-c1[1]) == -4) and (LOpt[1][3-2*c1p[0]]==1):
                    tPos = [[j for j in i] for i in LPos]
                    for i in range(-1,-3,-1):
                        if tPos[c1[0]][c1[1]+i] != 0:
                            return False
                        tPos[c1[0]][c1[1]+i]=tPos[c1[0]][c1[1]+i+1]
                        tPos[c1[0]][c1[1]+i+1]=0
                        if self.isCheck(c1p[0],tPos):
                            return False
                    LPos[c1[0]][c1[1]-2]=c1p
                    LPos[c1[0]][c1[1]]=0
                    LPos[c1[0]][c1[1]-1]=c2p
                    LPos[c2[0]][c2[1]]=0
                    LOpt[1][3-2*c1p[0]]=0
                    LOpt[1][2-2*c1p[0]]=0
                else:
                    return False
            else:
                if not (c2 in [[c1[0]+1,c1[1]],[c1[0]-1,c1[1]],[c1[0]+1,c1[1]-1],[c1[0],c1[1]-1],[c1[0]-1,c1[1]-1],[c1[0]+1,c1[1]+1],[c1[0],c1[1]+1],[c1[0]-1,c1[1]+1]]):
                    return False
                LPos[c1[0]][c1[1]]=0
                LPos[c2[0]][c2[1]]=c1p
                LOpt[1][3-2*c1p[0]]=0
                LOpt[1][2-2*c1p[0]]=0
        if (c1p[1]==4) or ((c1p[1]==5) and ((c2[0]==c1[0]) or (c2[1]==c1[1]))):
            if c2[0]==c1[0]:
                rowMove=0
                colMove=int(c1[1]<c2[1])*2-1
            elif c2[1]==c1[1]:
                colMove=0
                rowMove=int(c1[0]<c2[0])*2-1
            else:
                return False
        elif (c1p[1]==3) or ((c1p[1]==5) and (abs(c1[0]-c2[0])==abs(c1[1]-c2[1]))):
            if (abs(c1[0]-c2[0])!=abs(c1[1]-c2[1])):
                return False
            rowMove=int(c1[0]<c2[0])*2-1
            colMove=int(c1[1]<c2[1])*2-1
        if c1p[1] in [3,4,5]:
            if (not ((c2[0]==c1[0]) or (c2[1]==c1[1]))) and (abs(c1[0]-c2[0])!=abs(c1[1]-c2[1])):
                return False
            t1,t2=c1[0]+rowMove,c1[1]+colMove
            while (t1!=c2[0]) or (t2!=c2[1]):
                if not (self.pos[0][t1][t2] in [0,1]):
                    return False
                t1+=rowMove
                t2+=colMove
            LPos[c1[0]][c1[1]] = 0
            LPos[c2[0]][c2[1]] = c1p
        if self.isCheck(LOpt[0],LPos):
            return False
        for i,rr in zip(LPos,range(len(LPos))):
            for j,cc in zip(i,range(len(i))):
                if (j == 1) and (tfex!=[rr,cc]):
                    LPos[rr][cc]=0
        if (type(c2p)==tuple) and (c2p[0]!=LOpt[0]):
            LOpt[2]=0
        LOpt[0]=abs(LOpt[0]-1)
        if retPos:
            return [LPos,LOpt]
        else:
            return True
    def play(self,n):
        f=lambda x:[8-int(x[1]),{k:v for k,v in zip("abcdefgh",range(8))}[x[0]]]
        c1,c2=f(n[:2]),f(n[2:])
        prom=5
        if len(n)==5:
            prom={k:v for k,v in zip("nbrq",[2,3,4,5])}[n[-1]]
        elif len(n)!=4:
            return
        c=self.isLegal(c1,c2,True,prom)
        if not c:
            return False
        else:
            self.pos=c
            return True
    def enginePlay(self,depth=16):
        try:
            engine = subprocess.Popen('stockfish', universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=1,creationflags=0x08000000)
            engine.stdin.write("position fen "+self.getFEN()+"\n"+"go depth "+str(depth)+"\n")
            while True:
                x=engine.stdout.readline()
                if x[:8]=="bestmove":
                    move=x.split(" ")[1]
                    if move[-1]=="\n":
                        move=move[:-1]
                    break
                elif x=="":
                    legals=[]
                    p=lambda x,y:list("abcdefgh")[x]+str(8-y)
                    for i1 in range(8):
                        for j1 in range(8):
                            for i2 in range(8):
                                for j2 in range(8):
                                    for prom in [2,3,4,5]:
                                        if ([i1,j1]!=[i2,j2]) and (type(self.pos[0][i1][j1])==tuple) and self.isLegal([i1,j1],[i2,j2],prom):
                                            legals.append(p(j1,i1)+p(j2,i2)+"nbrq"[prom-2])
                    if len(legals) == 0:
                        return None
                    move=random.choice(legals)
                    self.play(move)
                    engine.kill()
                    return move
            self.play(move)
            engine.kill()
            return move
        except:
            return None
    def evalute(self):
        engine = subprocess.Popen('stockfish', universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=1,creationflags=0x08000000)
        engine.stdin.write("position fen "+self.getFEN()+"\neval\n")
        while True:
            x=engine.stdout.readline()
            if x[:17]=="Final evaluation:":
                b=x[22:].split(" ")[0]
                if b[-1]=="\n":
                    b=b[:-1]
                break
        engine.kill()
        return float(b)

if __name__=="__main__":
    game=ChessGame()
