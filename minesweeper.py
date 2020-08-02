# Max Jiang
# June 19, 2020
# Minesweeper

from tkinter import *
from random import randint
import time

# numMines should be less than or equal to number of grids - 9
numRows = 0
numColumns = 0
numMines = 0
mods={"nofail":False, "relax":False, "hidden":False, "easy":False}

class Minesweeper: # Minesweeper game window
    def __init__(self, master):
        self.master = master
        # if easy mod is enabled, remove half the bombs
        if (mods["easy"]):
            global numMines
            numMines//=2
        # make background
        self.bg_image = PhotoImage(file="pics/bg"+str(randint(1,7))+".png")
        self.bg = Label(master, image=self.bg_image)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.gen_images()
        self.make_board()
        # buffer space above grid
        self.buffer_top = Label(master)
        self.buffer_top.grid(row=99,columns=100,pady=(50,0))
        self.buffer_top.lower() # hide behind bg

        # make quit button
        self.quit_button = Label(master,
                                  text="Quit game",
                                  font=("Courier",12),
                                  width=15, height=1)
        self.quit_button.bind("<Button-1>", lambda a: self.master.destroy())
        self.quit_button.grid(row=101+numRows, column=98,
                              padx=(10,50),pady=(50,10))
        # make flag counter
        self.flag_counter = Label(master,
                                  text="Flags left: "+str(self.flags_left),
                                  font=("Courier",12),
                                  width=15, height=1)
        self.flag_counter.grid(row=101+numRows,column=101+numColumns,
                               padx=(50,10),pady=(50,10))

    def gen_images(self): # generate the images and store them in images array
        self.images = [PhotoImage(file="pics/"+str(i)+".png").subsample(10,10)
                       for i in range(0,9)]
        self.images.append(PhotoImage(file="pics/facingDown.png").subsample(10,10))
        self.images.append(PhotoImage(file="pics/flagged.png").subsample(10,10))
        self.images.append(PhotoImage(file="pics/bomb.png").subsample(10,10))
        # 9 is unpressed square
        # 10 is flagged square
        # 11 is bomb
    
    def make_board(self): # generate the board
        # generate the board with all the buttons
        self.board = [[Button(self.master) for y in range(numColumns+1)]
                      for x in range(numRows+1)]
        for r in range(1,numRows+1):
            for c in range(1,numColumns+1):
                self.board[r][c].config(
                    image = self.images[9],
                    command = lambda row=r,col=c : self.left_click(row,col),
                    borderwidth=0)
                self.board[r][c].grid(row=100+r,column=100+c)
                # bind right click to flag
                self.board[r][c].bind(
                    "<Button-3>", lambda event,row=r,col=c : self.right_click(row,col))
                self.board[r][c].bind(
                    "<Button-2>", lambda event,row=r,col=c : self.middle_click(row,col))
        self.minesGenerated = False
        self.flags_left=numMines
        # whether or not space is revealed
        self.vis = [[False for y in range(numColumns+2)]
                    for x in range(numRows+2)]
        # whether or not space is marked
        self.marked = [[False for y in range(numColumns+2)]
                       for x in range(numRows+2)]
        # whether or not space is a mine
        self.is_mine = [[False for y in range(numColumns+2)]
                        for x in range(numRows+2)]
        # counter for number of unrevealed or unmarked spaces left
        self.count_left = numRows*numColumns
        
    def gen_mines(self, r, c): # generate mine positions
        count=numMines
        while (count!=0):
            # generate random position
            posr = randint(1,numRows)
            posc = randint(1,numColumns)
            # cannot be within 1 space from first click
            if (abs(posr-r)<=1 and abs(posc-c)<=1): continue
            if (not self.is_mine[posr][posc]): # if space is not already a mine
                self.is_mine[posr][posc] = True
                count-=1
    
    def get_num(self, r, c): # count number of surrounding mines
        res=0
        for i in range(-1,2):
            for k in range(-1,2):
                if i==0 and k==0: continue
                res+=self.is_mine[r+i][c+k]
        return res

    def left_click(self, r, c): # left button is clicked
        if (self.marked[r][c]): return # cannot reveal flagged square
        if (self.vis[r][c]): return
        if (not self.minesGenerated): # if it's user's first click
            self.gen_mines(r,c)
            self.minesGenerated = True
        if (self.is_mine[r][c]): # if user has clicked on mine
            if (not mods["nofail"]): self.has_lost()
            else:
                self.board[r][c].config(image = self.images[11])
                return
            # no fail: reveal the mine to the player, but they don't lose
            # they can flag it after seeing it
        else: # if space is not a mine
            self.reveal(r,c)
        if (self.flags_left==0): # if all flags are placed
            if (self.check_win()):
                self.end_screen(True)
                return
        # if relax mod is enabled, reveal a random square
        if (mods["relax"] and self.count_left!=0):
            for i in range(0,30): # only try 30 times to find empty space
                posr = randint(1,numRows)
                posc = randint(1,numColumns)
                if (not self.is_mine[posr][posc] and
                    not self.marked[posr][posc] and
                    not self.vis[posr][posc]): break
            self.reveal(posr,posc)

    def middle_click(self, r, c):
        if (not self.vis[r][c]): return # middle click must be on revealed tile
        flag=True
        for i in range(-1,2): # verify surrounding spaces
            for k in range(-1,2):
                if (self.vis[r+i][c+k]): continue
                if (self.marked[r+i][c+k] and not self.is_mine[r+i][c+k]): # wrong flag
                    if (mods["nofail"]): flag=False # if no fail, just don't fail the player
                    else:
                        self.has_lost()
                        return
                if (self.is_mine[r+i][c+k] and not self.marked[r+i][c+k]): # missing flag
                    flag=False
        if (not flag): return # don't reveal
        for i in range(-1,2): # reveal surrounding spaces
            for k in range(-1,2):
                self.reveal(r+i,c+k)
        self.master.update()
        if (self.flags_left==0): # if all flags are placed
            if (self.check_win()):
                self.end_screen(True)

    def right_click(self, r, c): # right button is clicked
        if (self.vis[r][c]): return # cannot flag revealed square
        if (self.marked[r][c]): # if already marked
            self.marked[r][c]=0
            self.board[r][c].config(image = self.images[9])
            self.flags_left+=1
            self.count_left-=1
        else: # if not marked
            self.marked[r][c]=1
            self.board[r][c].config(image = self.images[10])
            self.flags_left-=1
            self.count_left+=1
        # update counter
        self.flag_counter.config(text="Flags left: "+str(self.flags_left))
        if (self.flags_left<0): self.flag_counter.config(foreground="red")
        else: self.flag_counter.config(foreground="black")
        self.master.update()
        if (self.flags_left==0): # if all flags are placed
            if (self.check_win()):
                self.end_screen(True)

    def reveal(self, r, c,): # reveal a space
        if (r<=0 or r>numRows or c<=0 or c>numColumns): return # check if grid is within boundaries
        if (self.is_mine[r][c] or self.vis[r][c]): return # don't reveal mine or already revealed spaces
        if (self.marked[r][c]): return # don't reveal flagged squares
        self.vis[r][c]=1 # mark as visited
        self.count_left-=1 # decrement counter
        self.board[r][c].config(image = self.images[self.get_num(r,c)]) # set button image
        self.master.update()
        if (self.get_num(r,c)==0): # recur neighbours
            for i in range(-1,2):
                for k in range(-1,2):
                    if (i==0 and k==0): continue
                    if (not self.vis[r+i][c+k]): self.reveal(r+i,c+k)
        # buttons disappear if hidden mod is on
        if (mods["hidden"]):
            self.board[r][c].after(2000,lambda : self.board[r][c].config(image = self.images[0]))
        
    def check_win(self): # verify that all flags are on mines
        for r in range(1,numRows+1):
            for c in range(1,numColumns+1):
                # if space is mine but not marked
                if (self.is_mine[r][c] and not self.marked[r][c]): return False
                # if a space is not revealed or mark
                if (not self.marked[r][c] and not self.vis[r][c]): return False
        return True

    def has_lost(self): # reveal all mines, wait a bit, then show lose screen
        # iterate through all spaces
        for r in range(1,numRows+1):
            for c in range(1,numColumns+1):
                # if space is mine but not flagged, reveal it
                if (self.is_mine[r][c] and not self.marked[r][c]):
                    self.board[r][c].config(image = self.images[11])
        self.master.update()
        time.sleep(1)
        self.end_screen(False)

    def end_screen(self, has_won):
        # hide buttons and labels under bg
        for r in range(1,numRows+1):
            for c in range(1,numColumns+1):
                self.board[r][c].lower()
        self.flag_counter.lower()
        # display win or lose
        self.end_message = Label(self.master,
                                text="You win!" if (has_won) else "You lose!",
                                 width=12,
                                 font=("Comic Sans MS",24))
        self.end_message.place(relx=0.5,rely=0.5,anchor=CENTER)

class Menu(): # Minesweeper main menu
    def __init__(self, master):
        self.master = master
        self.master.minsize(700,500)
        # make background
        self.bg_image = PhotoImage(file="pics/bg"+str(randint(1,7))+".png")
        self.bg = Label(self.master, image=self.bg_image)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        # window title
        self.title = Label(self.master,
                                text="",
                                width=14,
                                font=("Comic Sans MS",48))
        self.title.place(relx=0.5,rely=0.2,anchor=CENTER)
        # back button
        self.back_button = Label(self.master,
                                  text="",
                                  font=("Courier",12),
                                  width=15, height=1)
        self.back_button.bind("<Button-1>", lambda a: self.master.destroy())
        self.back_button.place(relx=0.01,rely=0.94)
        # draw the menu
        self.draw_menu()
        # load the mod images
        self.mod_images=[PhotoImage(file="pics/mod-nofail.png"),
                             PhotoImage(file="pics/mod-relax.png"),
                             PhotoImage(file="pics/mod-hidden.png"),
                             PhotoImage(file="pics/mod-easy.png")]
        
    def draw_menu(self):
        # config title text & back button
        self.title.config(text="Minesweeper!")
        self.back_button.config(text="Exit")
        self.back_button.bind("<Button-1>", lambda a: self.master.destroy())
        
        # play button
        self.play_button = Label(self.master,
                                 text="Play",
                                 width=12,
                                 font=("Courier",30))
        self.play_button.place(relx=0.5,rely=0.45,anchor=CENTER)
        self.play_button.bind("<Button-1>", lambda a: self.undraw_menu(self.draw_difficulty))
        
        # instructions button
        self.instructions_button = Label(self.master,
                                         text="Instructions",
                                         width=12,
                                         font=("Courier",30))
        self.instructions_button.place(relx=0.5,rely=0.6,anchor=CENTER)
        self.instructions_button.bind("<Button-1>",lambda a: self.undraw_menu(self.draw_instructions))

    def undraw_menu(self,cmd):
        # delete window elements
        self.play_button.destroy()
        self.instructions_button.destroy()
        cmd() # draw next window
    
    def draw_instructions(self):
        # config window elements
        self.title.config(text="Instructions")
        self.instructions = Label(self.master,
                                  text='''
There is a large grid of buttons representing spaces with some
having mines underneath them. The number and locations of the mines is
determined before the game beings and do not change once the game has began. 

The player can left click to reveal a space. If the space has a mine, the
player loses and the game ends. Else, the game will display a number on
the space representing the number of mines adjacent or diagonally adjacent
to that space. If a revealed space has no mines around it, it will instead
reveal all spaces adjacent or diagonally adjacent to it. The player can also
right-click to flag a space if they think there is a mine there. A revealed
space cannot be re-revealed. A player can also use a mouse wheel click to
reveal all spaces around an already revealed space.

The player wins when all non-mine spaces are revealed and all mines are
flagged. The player loses if they reveal a space containing a mine.
''',
                                  font=("Courier",10))
        self.instructions.place(relx=0.5,rely=0.6,anchor=CENTER)
        self.back_button.config(text="Back")
        self.back_button.bind("<Button-1>", lambda a: self.undraw_instructions(self.draw_menu))
    
    def undraw_instructions(self,cmd):
        self.instructions.destroy()
        cmd()

    def draw_difficulty(self):
        self.title.config(text="Difficulty")
        # set up buttons
        self.easy_button = Label(self.master,
                                 text="Easy",
                                 width=10,
                                 font=("Courier",30))
        self.easy_button.place(relx=0.3,rely=0.4,anchor=CENTER)
        self.easy_button.bind("<Button-1>", lambda a: self.undraw_difficulty(self.draw_mods,[9,9,10]))                        
        self.medium_button = Label(self.master,
                                 text="Medium",
                                 width=10,
                                 font=("Courier",30))
        self.medium_button.place(relx=0.3,rely=0.55,anchor=CENTER)
        self.medium_button.bind("<Button-1>", lambda a: self.undraw_difficulty(self.draw_mods,[16,16,40])) 
                              
        self.hard_button = Label(self.master,
                                 text="Hard",
                                 width=10,
                                 font=("Courier",30))
        self.hard_button.place(relx=0.7,rely=0.4,anchor=CENTER)
        self.hard_button.bind("<Button-1>", lambda a: self.undraw_difficulty(self.draw_mods,[16,30,99]))
                              
        self.custom_button = Label(self.master,
                                 text="Custom",
                                 width=10,
                                 font=("Courier",30))
        self.custom_button.place(relx=0.7,rely=0.55,anchor=CENTER)
        self.custom_button.bind("<Button-1>", lambda a: self.set_custom_size())
                                                                                       
        self.back_button.config(text="Back")
        self.back_button.bind("<Button-1>", lambda a: self.undraw_difficulty(self.draw_menu,[numRows,numColumns,numMines]))

    def undraw_difficulty(self, cmd, vals):
        # delete window elements
        self.easy_button.destroy()
        self.medium_button.destroy()
        self.hard_button.destroy()
        self.custom_button.destroy()
        # set grid size
        global numRows, numColumns, numMines
        [numRows,numColumns,numMines]=vals
        cmd() # draw next window

    def draw_mods(self):
        self.title.config(text="Mods")
        self.mod_states=[IntVar() for i in range(0,4)]
        # no fail check button
        self.nofail = Checkbutton(self.master,
                                  image=self.mod_images[0],
                                  variable=self.mod_states[0])
        self.nofail.place(relx=0.3, rely=0.45, anchor=CENTER)
        # relax check button
        self.relax = Checkbutton(self.master,
                                  image=self.mod_images[1],
                                  variable=self.mod_states[1])
        self.relax.place(relx=0.3, rely=0.7, anchor=CENTER)
        # hidden check button
        self.hidden = Checkbutton(self.master,
                                  image=self.mod_images[2],
                                  variable=self.mod_states[2])
        self.hidden.place(relx=0.7, rely=0.45, anchor=CENTER)
        # easy check button
        self.easy = Checkbutton(self.master,
                                  image=self.mod_images[3],
                                  variable=self.mod_states[3])
        self.easy.place(relx=0.7, rely=0.7, anchor=CENTER)

        # play button
        self.play_game = Label(self.master,
                                  text="Play!",
                                  font=("Courier",12),
                                  width=15, height=1)
        self.play_game.bind("<Button-1>", lambda a: self.undraw_mods(None))
        self.play_game.place(relx=0.77,rely=0.94)
        
        self.back_button.config(text="Back")
        self.back_button.bind("<Button-1>", lambda a: self.undraw_mods(self.draw_difficulty))

    def undraw_mods(self, cmd):
        if (cmd==self.draw_difficulty): # if back button was clicked
            self.nofail.destroy()
            self.relax.destroy()
            self.hidden.destroy()
            self.easy.destroy()
            cmd()
            return
        # set mods
        global mods
        mods["nofail"]=self.mod_states[0].get()
        mods["relax"]=self.mod_states[1].get()
        mods["hidden"]=self.mod_states[2].get()
        mods["easy"]=self.mod_states[3].get()
        # state that user wants to play the game
        global playGame
        playGame=True
        # exit the menu screen
        self.master.destroy()

    def set_custom_size(self):
        # Toplevel custom window
        self.cw = Toplevel()
        self.cw.grab_set()
        self.cw.minsize(400,400)
        # make background
        self.bg_image2 = PhotoImage(master=self.master,file="pics/bg"+str(randint(1,7))+".png")
        self.bg2 = Label(self.cw, image=self.bg_image2)
        self.bg2.place(relx=0, y=0, relwidth=1, relheight=1)
        self.build("")

    def build(self,errormsg): # builds entry and buttons
        if (errormsg!=""): # display error message if there is any
            self.error = Label(self.cw,
                               text=errormsg,
                               foreground="red")
            self.error.place(relx=0.5,rely=0.1,anchor=CENTER)
        # Number of rows
        self.row_text = Label(self.cw,
                              text="Number of rows: ")
        self.row_entry = Entry(self.cw,
                               width=10)
        self.row_text.place(relx=0.3,rely=0.2,anchor=CENTER)
        self.row_entry.place(relx=0.7,rely=0.2,anchor=CENTER)
        # Number of columns
        self.col_text = Label(self.cw,
                              text="Number of columns: ")
        self.col_entry = Entry(self.cw,
                               width=10)
        self.col_text.place(relx=0.3,rely=0.4,anchor=CENTER)
        self.col_entry.place(relx=0.7,rely=0.4,anchor=CENTER)
        # Number of mines
        self.mine_text = Label(self.cw,
                              text="Number of mines: ")
        self.mine_entry = Entry(self.cw,
                               width=10)
        self.mine_text.place(relx=0.3,rely=0.6,anchor=CENTER)
        self.mine_entry.place(relx=0.7,rely=0.6,anchor=CENTER)
        # Done button
        self.done_button = Button(self.cw,
                                  text="Done!",
                                  command=self.verify)
        self.done_button.place(relx=0.5,rely=0.8,anchor=CENTER)
        
    def verify(self):
        # try to erase previous error message
        try: self.error.destroy()
        except: pass
        # rows, columns, mines
        r,c,m = self.row_entry.get(), self.col_entry.get(), self.mine_entry.get()
        if (r=="" or c=="" or m==""): # no empty entries
            self.build("Entries cannot be empty")
            return
        if (not r.isdigit() or not c.isdigit() or not m.isdigit()): # must all be positive integers
            self.build("All entries must be positive integers.")
            return
        r,c,m=int(r),int(c),int(m)
        if (r<3 or c<3 or r>30 or c>30): # too little or many rows or columns
            self.build("Row and column count must be between 3 and 30 inclusive.")
            return
        if (m<0 or m>r*c-9): # too little or many mines
            self.build("Mine count must be between 0 and rows*columns-9 inclusive.")
            return
        global numRows, numColumns, numMines
        numRows, numColumns, numMines = r,c,m
        self.cw.destroy()
        self.undraw_difficulty(self.draw_mods,[numRows,numColumns,numMines])

    
playGame=False
while (True):
    # main menu
    root_menu = Tk()
    root_menu.title("Menu")
    menu = Menu(root_menu)
    root_menu.mainloop()
    if (not playGame): break # end if user exits the menu without playing
    # game
    playGame=False
    root_game = Tk()
    root_game.title("Minesweeper")
    game = Minesweeper(root_game)
    root_game.mainloop()
