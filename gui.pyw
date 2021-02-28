import tkinter as tk
import threading as th
import time
import tkinter.messagebox as mb
from chess import *
from PIL import Image, ImageTk

FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
def start():
    global FEN
    FEN=et.get()
    froot.destroy()

froot=tk.Tk()
froot.resizable(0,0)
g1,g2=(froot.winfo_screenwidth()-300)//2,(froot.winfo_screenheight()-200)//2
froot.geometry(f"300x200+{g1}+{g2}")
froot.title("Chess")

tk.Label(froot,text="Insert FEN to start.\nYou can close this window\nto play in starting position.").pack()

et=tk.Entry(froot,width=30)
et.pack()

bt=tk.Button(froot,text="Go",command=start)
bt.pack()

froot.mainloop()

pieces=[[-1 for _ in range(8)] for __ in range(8)]

bsq="#8ca2ad"
wsq="#dee3e6"

turn=True

pp=5
c1=""
c1C=[]
o=[]
selsq=None
checksq=None
promote=False
shownsq=None

prompieces=[]
p=lambda x,y:list("abcdefgh")[x]+str(8-y)
q_=lambda m:({k:v for k,v in zip("abcdefgh",range(8))}[m[0]],8-int(m[1]))
q=lambda m:q_(m[:2])+q_(m[2:4])

def deqsx():
    global promote,pp
    pp=5
    promote=False

def pcf(e):
    global pp,promote,shownsq,s
    if not ((0<=e.x<=int(400*s)) and (0<=e.y<=int(100*s))):
        return
    pp=[5,4,3,2][e.x//int(100*s)]
    promote=False
    shownsq=None

def pcs(e,qcanv):
    global shownsq,prompieces
    if not ((0<=e.x<=int(400*s)) and (0<=e.y<=int(100*s))):
        return
    if shownsq:
        qcanv.delete(shownsq)
        shownsq=None
    qcanv.delete(prompieces[e.x//int(100*s)])
    shownsq=qcanv.create_rectangle((e.x//int(100*s))*int(100*s),0,(e.x//int(100*s)+1)*int(100*s),int(100*s),fill="#6f6f6f",outline="")
    prompieces[e.x//int(100*s)]=qcanv.create_image((e.x//int(100*s))*int(100*s),0,image=pis[[(game.pos[1][0],5),(game.pos[1][0],4),(game.pos[1][0],3),(game.pos[1][0],2)][e.x//int(100*s)]],anchor=tk.NW)

def PROD(x,y):
    global promote,pis,pp,checksq,c1,c1C,prompieces,s
    qsx=tk.Toplevel()
    gx1,gx2=(qsx.winfo_screenwidth()-int(400*s))//2,(qsx.winfo_screenheight()-int(100*s))//2
    qsx.geometry(f"{int(400*s)}x{int(100*s)}+{gx1}+{gx2}")
    qsx.resizable(0,0)
    qsx.config(bg="black")
    root.title("Promote")
    qcanv=tk.Canvas(qsx,width=int(400*s),height=int(100*s),bg="#7f7f7f")
    qcanv.pack()
    for i,j in zip([(game.pos[1][0],5),(game.pos[1][0],4),(game.pos[1][0],3),(game.pos[1][0],2)],range(4)):
        prompieces.append(qcanv.create_image(j*int(100*s),0,image=pis[i],anchor=tk.NW))
    promote=True
    qsx.protocol("WM_DELETE_WINDOW",deqsx)
    qcanv.bind("<Button-1>",pcf)
    qcanv.bind("<Motion>",lambda e,qcanv=qcanv:pcs(e,qcanv))
    while promote:
        time.sleep(0.05)
    qsx.destroy()
    if checksq:
        canv.delete(checksq)
        checksq=None
    game.play(c1+p(x,y)+{k:v for k,v in zip([2,3,4,5],"nbrq")}[pp])
    playPiece(c1C[0],c1C[1],x,y)
    c1=""
    c1C=[]
    th.Thread(target=enginePlay).start()

def on_click(e):
    global c1,c1C,checksq,promote,pis,pp,turn
    x=e.x//int(100*s)
    y=e.y//int(100*s)
    if (x<0) or (7<x) or (y<0) or (7<y) or (not turn) or promote:
        return
    if c1:
        clearLegals()
        canv.delete(selsq)
        if (7*(1-game.pos[0][c1C[1]][c1C[0]][0])==y) and (game.pos[0][c1C[1]][c1C[0]][1]==1) and game.isLegal(c1C[::-1],[y,x]):
            th.Thread(target=PROD,args=(x,y),daemon=True).start()
            return
        if not game.play(c1+p(x,y)):
            c1=""
            c1C=[]
            return
        if checksq:
            canv.delete(checksq)
            checksq=None
        playPiece(c1C[0],c1C[1],x,y)
        c1=""
        c1C=[]
        gio=game.isOver()
        if gio:
            if gio==-1:
                msg="Black Won!"
            elif gio==1/2:
                msg="Draw!"
            elif gio==1:
                msg="White Won!"
            mb.showinfo(title="Game Over", message=msg)
            canv.unbind("<Button-1>")
            turn=False
            return
        th.Thread(target=enginePlay).start()
    elif type(game.pos[0][y][x])==tuple:
        showLegals(x,y)
        selSquare(x,y)
        c1=p(x,y)
        c1C=[x,y]

def enginePlay():
    global turn,checksq
    turn=False
    try:
        x1,y1,x2,y2=q(game.enginePlay(20))
    except:
        return
    if checksq:
        canv.delete(checksq)
        checksq=None
    playPiece(x1,y1,x2,y2)
    gio=game.isOver()
    if gio:
        if gio==-1:
            msg="Black Won!"
        elif gio==1/2:
            msg="Draw!"
        elif gio==1:
            msg="White Won!"
        mb.showinfo(title="Game Over", message=msg)
        canv.unbind("<Button-1>")
        turn=False
        return
    turn=True

def selSquare(x,y):
    global pieces,selsq,s

    selsq=canv.create_rectangle(x*int(100*s),y*int(100*s),(x+1)*int(100*s),(y+1)*int(100*s),fill="#00fa00")
    canv.delete(pieces[y][x])
    pieces[y][x]=canv.create_image(x*int(100*s),y*int(100*s),image=pis[game.pos[0][y][x]],anchor=tk.NW)

def playPiece(x1,y1,x2,y2):
    global pieces,selsq,checksq,s

    if game.isCheck(game.pos[1][0],game.pos[0]):
        for i,tf1 in zip(game.pos[0],range(8)):
            for j,tf2 in zip(i,range(8)):
                if j == (game.pos[1][0],6):
                    canv.delete(pieces[tf1][tf2])
                    checksq=canv.create_rectangle(tf2*int(100*s),tf1*int(100*s),(tf2+1)*int(100*s),(tf1+1)*int(100*s),fill="#fd0000")
                    pieces[tf1][tf2]=canv.create_image(tf2*int(100*s),tf1*int(100*s),image=pis[j],anchor=tk.NW)
                    
    canv.delete(pieces[y1][x1])
    pieces[y1][x1]=-1
    canv.delete(pieces[y2][x2])
    try:
        if game.pos[0][y2+2*game.pos[0][y2][x2][0]-1][x2]==0:
            canv.delete(pieces[y2+2*game.pos[0][y2][x2][0]-1][x2])
    except:
        pass
    if ((game.pos[0][y1][x1]==0) and (game.pos[0][y2][x2]==0)) or ((game.pos[0][y2][x2][1]==6) and (abs(x1-x2)==2)):
        x3=x1+int(x1<x2)*4-2
        x4=x1+int(x1<x2)*2-1
        pieces[y1][x4]=canv.create_image(x4*int(100*s),y2*int(100*s),image=pis[game.pos[0][y2][x4]],anchor=tk.NW)
        pieces[y1][x3]=canv.create_image(x3*int(100*s),y2*int(100*s),image=pis[game.pos[0][y2][x3]],anchor=tk.NW)
        if (abs(x1-x2)==2):
            canv.delete(pieces[y1][-int(x1<x2)])
            pieces[y1][-int(x1<x2)]=-1
    else:
        pieces[y2][x2]=canv.create_image(x2*int(100*s),y2*int(100*s),image=pis[game.pos[0][y2][x2]],anchor=tk.NW)

def clearLegals():
    global o
    for i in o:
        canv.delete(i)
    o=[]

def showLegals(x,y):
    global o
    clearLegals()
    for i in range(8):
        for j in range(8):
            if (i!=y) or (j!=x):
                if game.isLegal([y,x],[i,j]):
                    o.append(canv.create_oval(j*int(100*s)+int(40*s),i*int(100*s)+int(40*s),j*int(100*s)+int(60*s),i*int(100*s)+int(60*s),fill="#00fa00",outline=""))

game=ChessGame()
game.loadFEN(FEN)

root = tk.Tk()
s=1080/root.winfo_screenheight()
root.resizable(0,0)
g1,g2=(root.winfo_screenwidth()-int(800*s))//2,(root.winfo_screenheight()-int(800*s))//2
root.geometry(f"{int(800*s)}x{int(800*s)}+{g1}+{g2}")
root.title("Chess")

pis={
(0,1):ImageTk.PhotoImage(Image.open("pieces/pb.png").resize((int(100*s),int(100*s)))),
(0,2):ImageTk.PhotoImage(Image.open("pieces/nb.png").resize((int(100*s),int(100*s)))),
(0,3):ImageTk.PhotoImage(Image.open("pieces/bb.png").resize((int(100*s),int(100*s)))),
(0,4):ImageTk.PhotoImage(Image.open("pieces/rb.png").resize((int(100*s),int(100*s)))),
(0,5):ImageTk.PhotoImage(Image.open("pieces/qb.png").resize((int(100*s),int(100*s)))),
(0,6):ImageTk.PhotoImage(Image.open("pieces/kb.png").resize((int(100*s),int(100*s)))),
(1,1):ImageTk.PhotoImage(Image.open("pieces/pw.png").resize((int(100*s),int(100*s)))),
(1,2):ImageTk.PhotoImage(Image.open("pieces/nw.png").resize((int(100*s),int(100*s)))),
(1,3):ImageTk.PhotoImage(Image.open("pieces/bw.png").resize((int(100*s),int(100*s)))),
(1,4):ImageTk.PhotoImage(Image.open("pieces/rw.png").resize((int(100*s),int(100*s)))),
(1,5):ImageTk.PhotoImage(Image.open("pieces/qw.png").resize((int(100*s),int(100*s)))),
(1,6):ImageTk.PhotoImage(Image.open("pieces/kw.png").resize((int(100*s),int(100*s))))
    }

canv = tk.Canvas(root,width=int(800*s),height=int(800*s),bg=wsq)
canv.pack()

canv.bind("<Button-1>",on_click)

for i in range(8):
    for j in range(8):
        if abs(i+j)%2:
            canv.create_rectangle(i*int(100*s),j*int(100*s),(i+1)*int(100*s),(j+1)*int(100*s),fill=bsq)

for i,i2 in zip(game.pos[0],range(8)):
    for j,j2 in zip(i,range(8)):
        if type(j)==tuple:
            pieces[i2][j2]=canv.create_image(j2*int(100*s),i2*int(100*s),image=pis[j],anchor=tk.NW)

if not mb.askyesno(message="Want to start first?"):
    turn=False
    th.Thread(target=enginePlay).start()

root.mainloop()
