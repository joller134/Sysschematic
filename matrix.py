from tkinter import *

class Excel(Frame):
    def __init__(self, master, rows, columns, width, matrix, indicator):
        super().__init__(master)
        self.col = columns
        self.row = rows

        for i in range(columns):
            self.make_entry(0, i+1, width, f'{indicator}{i+1}', False)

        for row in range(rows):
            self.make_entry(row+1, 0, 5, f'w{row+1}', False)

            for column in range(columns):
                self.make_entry(row+1, column+1, width, str(matrix[row][column]), True)

    def make_entry(self, row, column, width, text, state):
        e = Entry(self, width=width)
        if text: e.insert(0, text)
        e['state'] = NORMAL if state else DISABLED
        e.coords = (row-1, column-1)
        e.grid(row=row, column=column)

    def show_cells(self):
        buckets = [[0 for col in range(self.col)] for row in range(self.row)]
        print('\n--== dumping cells ==--')
        i = 0
        j = 0
        w = self.col
        #print("i:",i,"w:",w,"col:",self.col)
        for e in self.children:
            v = self.children[e]
            #print(f'{v.get()}', end=', ')
            if(j>0 and i>0):
                #print("j:",j,"i:",i)
                buckets[j-1][i-1] = int(v.get())
            i = i+1
            if((i==w and j==0) or (i==w+1 and j>0)):
                #print("")
                j = j+1
                i = 0
        for x in buckets:
            print(x)
        
        self.matrix = buckets
    
    def print(self):
        print(self.matrix)

class matrixWindow(object):
    def __init__(self,master,NG,NR,NH):
        top=self.top=Toplevel(master)
        self.l=Label(top,text="Matrix editor")
        self.l.grid(row=0)
        self.loadCells(NG,top,'w')
        self.current = 1
        self.NG = NG
        self.NR = NR
        self.NH = NH
        self.bt = Button(top, text='Save', command=self.cleanup).grid(row=2, column=0,pady=10)
        self.NG = Button(top, text='NG', command= lambda: self.change(NG,1,top,'w')).grid(row=2,column=1,pady=10)
        self.NR = Button(top, text='NR', command= lambda: self.change(NR,2,top,'r')).grid(row=2,column=2,pady=10)
        self.NH = Button(top, text='NH', command= lambda: self.change(NH,3,top,'e')).grid(row=2,column=3,pady=10)

    def change(self,adjMatrix,id,top,indicator):
        print("matrix: ",adjMatrix)
        self.ex.pack_forget()
        self.loadCells(adjMatrix,top,indicator)
        self.current = id

    def loadCells(self,adjMatrix,top,indicator):
        self.ex = Excel(top, rows=len(adjMatrix), columns=len(adjMatrix[0]), width=6,matrix=adjMatrix, indicator=indicator)
        self.ex.grid(row=1,sticky=W+E,columnspan=4,padx=10,pady=10)

    def cleanup(self):
        self.ex.show_cells()
        if(self.current==1):
            self.NG=self.ex.matrix
        if(self.current==2):
            self.NR=self.ex.matrix
        if(self.current==3):
            self.NH=self.ex.matrix
        self.top.destroy()

def loadMatrixEditor(master,NG,NR,NH):

    call = matrixWindow(master,NG,NR,NH)
    master.wait_window(call.top)
    #print("following result ", call.value)
    return call.NG, call.NR, call.NH