# Importing tkinter module
from tkinter import *
from exampleLib import *
from matImport import readFile
from tkinter.filedialog import askopenfilename
import math
from Scrollwindow import *
from node import removeNodeCall
from noise import addNoiseNodeCall, selectNoiseNodeCall, removeNoiseNodeCall
import networkx as nx

"""
initializing all global components
The structure used for both btnStore and outputStore is as follows [windowsId, WidgetObject, x, y]
windowId is the canvas id generated by create window and widgetObject is the object you can edit to change color and such
the noise store has an extra entry which comes down to [windowsId, WidgetObject, x, y, outputObject] where output Object is the object of the output on which the noise is applied
tempStore follows [widgetId, objectId1, objectId2] object 1 en object 2 is the objects between which the line is connected
widgetId is what you call to remove it from the canvas in draw.delete(widgetId)

lineStore[x][1] and lineStore[x][2] are the modules connected by the line and lineStore[x][3] is the transfer
"""
number_of_nodes = 0
btnStore = []
lineStore = [[]]
lineNumber = 0
outputStore = []
noiseStore = []
connect = []
noiseNumber = 0
outputNumber = 0
excitationStore = []
excitationNumber = 0
noiseNodeNumber = 0
noiseNodeStore = []
storeNG = storeNR = storeNH = []
lineshow = 1;
overlay = 0 #overlay value 0 means the NG matrix and overlay 1 is the Noise overlay
currentAmountOutputSelected = 1 #this variable is so we know the order that outputs are connected. it is not zero because unselected are 0
#global declare is unnecessary since they are declared in the upper script outside any function
#variable which indicates if a click means a module add
clickOperation=0
#A simple function to draw circles in a canvas
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle


#initializes the main menu. you have to pass the mainmenu frame and the canvas so that it could pass the canvas id when clearing it
def initMainMenu(frame, canvas):

    #column 0
    Button(frame, text="load .mat file", command= lambda: loadMat(draw, master), height = 1, width=20).grid(row=0, padx=2, pady=2)
    Button(frame, text="export .mat file", command= lambda: toAdjecencyMatrix(draw, master), height = 1, width=20).grid(row=1, padx=2, pady=2)
    Button(frame, text="load example network", command= lambda: draw_example(draw,-10, -150,master), height = 1, width=20).grid(row=2, padx=2, pady=2)

    #column 1
    Button(frame, text="Options", height = 1, width=20).grid(row=0, column=1, padx=2, pady=2)
    Button(frame, text="Go to global view", height = 1, width=20).grid(row=1, column=1, padx=2, pady=2)
    Button(frame, text="Clear window", command= lambda: clearWindow(canvas), height = 1, width=20).grid(row=2, column=1, padx=2, pady=2)

    #column 2
    Button(frame, text="load noise view", command= lambda: plotNoise(draw,master), height = 1, width=20).grid(row=0, column=2, padx=2, pady=2)
    Button(frame, text="load transfer view", command= lambda: plotMatrix(draw,master,0), height = 1, width=20).grid(row=1, column=2, padx=2, pady=2)
    Button(frame, text="change line view", command= lambda: Dashed_line(draw,master), height = 1, width=20).grid(row=2, column=2, padx=2, pady=2)

    #column 3
    OptionMenu(frame, layoutMethod, *layout).grid(row=0, column=3)
#same as main menu initializes the submenu
def initSubMenu(frame):
    #Label(frame, text="currently selected:", bg="gray").pack()
    #Button(frame, text="Add transfer", command= lambda: addWidget(1), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="connect Transfer/module", command= lambda: connectCall(draw,master), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="Remove transfer", command= lambda: removeNode(draw, master),  height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="add output", command= lambda: addWidget(2), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="remove output", command= lambda: removeOutput(draw, master), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="add noise", command= lambda: addNHCall(master, draw,0), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="remove noise", command= lambda: removeNH(master, draw,0), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="add external excitation", command= lambda: addNHCall(master, draw,1), height = 1, width=20).pack(padx=2, pady=2)
    Button(frame, text="remove external excitation", command= lambda: removeNH(master, draw,1), height = 1, width=20).pack(padx=2, pady=2)
    #Button(frame, text="remove noise source", command= lambda: removeNoise(), height = 1, width=20).pack(padx=2, pady=2)
    #Button(frame, text="Toggle noise", command= lambda: addWidget(2), height = 1, width=20).pack(padx=2, pady=2)

"""
below are all the functions for

-------------------------------------------------------- Adjecency Matrix --------------------------------------------------------

used to plot adjency matrix and return everything to Adjecency matrix
"""


# Load mat will move everything in from the specific mat file.
def loadMat(draw,master):
    global connect
    global lineNumber
    global lineStore
    global outputStore
    global storeNG
    global storeNR
    global storeNH
    filename = askopenfilename()
    storeNG, storeNR, storeNH = readFile(filename)
    plotMatrix(draw,master,1)

def generateGraph(NG,NH,NR,typeGraph, setScale):

    nmbOutputs = len(NG)
    nmbOutputs2 = len(NG[0])
    #below function will read through the mat file and try to find how many modules their are

    #using the network functions create a direction graph (nodes with a connection with a direction so connection 1 to 2 has a direction and is not the same as 2 to 1)
    plot = nx.DiGraph()
    plot.add_nodes_from(range(nmbOutputs))

    for x in range(nmbOutputs):
        for y in range(nmbOutputs2):
            if(NG[x][y]==1):
                plot.add_edge(y,x)

    print("number of nodes: ", plot.number_of_nodes() ," number of edges: ", plot.number_of_edges())

    pos = []

    typeGraph = layoutMethod.get()
    #creating coordinates
    #the below functions can be chosen and generate position for the network and return them
    if(typeGraph=="circular"):
        pos = nx.circular_layout(plot,scale=setScale,center=(500,500))
        print("circular layout")
    if(typeGraph=="kamada_kawai"):
        pos = nx.kamada_kawai_layout(plot, scale=setScale, center=(500,500), dim=2)
        print("kamada_kawai layout")
    if(typeGraph=="spring"):
        pos = nx.spring_layout(plot, scale=setScale, center=(500,500))
        print("spring layout")
    if(typeGraph=="spectral"):
        pos = nx.spectral_layout(plot, scale=setScale, center=(500,500))
        print("spectral layout")
    if(typeGraph=="spiral"):
        pos = nx.spiral_layout(plot, scale=setScale, center=(500,500))
        print("spiral layout")

    return pos

def plotNoise(draw,master):
    global overlay
    global lineNumber
    global lineStore

    NG, NR, NH = toAdjecencyMatrix(draw,master)
    clearWindow(draw)
    overlay = 1


    nmbOutputs = len(NG)
    nmbNoise = len(NH[0])

    pos = generateGraph(NG,NR,NH,1,2000)
    posNoise = generateGraph(NH,NR,NG,1,1500)
    #below function will read through the mat file and try to find how many modules their are
    #plot each function in a circle

    for x in range(nmbOutputs):
        addOutput(draw, pos[x][0], pos[x][1],master)

    for x in range(nmbOutputs):
        for y in range(nmbOutputs):
            if(NG[x][y]>0):
                node1 = outputStore[y]
                node2 = outputStore[x]
                connectOutputs(node1,node2,draw,master,0)

    for x in range(len(NH[0])):
        addNoiseNode(draw, posNoise[x][0], posNoise[x][1],master)

    for x in range(len(NH)):
        for y in range(len(NH[x])):
            if(NH[x][y]>0):
                node1 = noiseNodeStore[y]
                node2 = outputStore[x]
                connectOutputs(node1,node2,draw,master,1)



def plotMatrix(draw,master,init):
    global overlay
    global storeNH

    if(init):
        NG = storeNG
        NR = storeNR
        NH = storeNH
    else:
        NG, NR, NH = toAdjecencyMatrix(draw,master)
        clearWindow(draw)
        #store noise so that the adjecency function can pick it from global variables
        storeNH = NH

    overlay = 0

    global lineNumber
    global lineStore

    nmbOutputs = len(NG)

    pos = generateGraph(NG,NR,NH,3,2000)

    for x in range(nmbOutputs):
        addOutput(draw, pos[x][0], pos[x][1],master)

    #make all the connectiosn tussen connectOutputs
    for x in range(nmbOutputs):
        for y in range(nmbOutputs):
            if(NG[x][y]==1):
                node1 = outputStore[y]
                node2 = outputStore[x]
                connectOutputs(node1,node2,draw,master,1)


    for x in range(len(NH)):
        for y in range(len(NH[x])):
            if(NH[x][y]==1):
                addNH(outputStore[x],master,draw,0,y)

    for x in range(len(NR)):
        for y in range(len(NR[x])):
            if(NR[x][y]==1):
                addNH(outputStore[x],master,draw,1,y)


    #connecting each output is below


def toAdjecencyMatrix(draw,master):
    global storeNG
    global storeNH
    global storeNR
    NG = []
    NR = []
    NH = []

    #set everything first to zero
    for x in range(outputNumber):
        new = []
        for y in range(outputNumber):
            new.append(0)
        NG.append(new)
        new = []
        for y in range(noiseNodeNumber):
            new.append(0)
        NH.append(new)
        new = []
        for y in range(excitationNumber):
            new.append(0)
        NR.append(new)
    #create NG matrix
    #print(noiseNodeStore)
    for x in range(outputNumber):
        if(outputStore[x]!=0):
            currentOutput = outputStore[x][1]
            #check for connections to create NG
            for y in range(lineNumber):
                #print("now scanning for node: ",x," at linestore: ",lineStore[y]," for button: ",currentOutput)
                if(lineStore[y]!=0):
                    if(lineStore[y][2]==currentOutput):
                        #found a lineconnection to currentOutput
                        nodeB = lineStore[y][1]
                        #print(nodeB.nmb)
                        NG[x][nodeB.nmb] = 1


            if(overlay==1):
                for y in range(lineNumber):
                    if(lineStore[y]!=0):
                        if(lineStore[y][2]==currentOutput):
                            nodeB = lineStore[y][1]
                            for a in range(noiseNodeNumber):
                                if(noiseNodeStore[a]!=0):
                                    if(nodeB == noiseNodeStore[a][1]):
                                        print(nodeB.nmb)
                                        NH[x][nodeB.nmb] = 1
            else:
                NH = storeNH

            for y in range(excitationNumber):
                if(excitationStore[y]!=0):
                    if(excitationStore[y][4]==currentOutput):
                        excitation = excitationStore[y][1]
                        nmb = int(excitation.nmb)
                        NR[x][nmb] = 1

    storeNG = NG
    storeNR = NR
    storeNH = NH

    print("NG is generated as following:")
    for value in storeNG:
        print(value)
    print("NR is generated as following:")
    for value in storeNR:
        print(value)
    print("NH is generated as following:")
    for value in storeNH:
        print(value)

    return NG, NR, NH

"""
Below we have the subsection of:

-------------------------------------------------------- nodes --------------------------------------------------------

Each function uses the global variables to store the nodes and to make changes
"""

def selectNode(w,node):
    global btnStore
    global number_of_nodes
    global lineStore
    global lineNumber

    #simpely edit the node its color based on the node object given in the argument

    #print("the node which is to be selected", node)
    if(btnStore[node][1]["bg"]=="cyan"):
        btnStore[node][1]["bg"]="lime"
        for x in range(lineNumber):
            if lineStore[x][3]==btnStore[node][1]:
                w.itemconfig(lineStore[x][0], fill="red")
    else:
        btnStore[node][1]["bg"]="cyan"
        for x in range(lineNumber):
            if lineStore[x][3]==btnStore[node][1]:
                w.itemconfig(lineStore[x][0], fill="black")

# adding a node
def addNode(w,x,y,master,node1,node2):
        global number_of_nodes
        global btnStore
        global outputStore
        global outputNumber
        global overlay
        node = 0


        node_name = "G"
        if(overlay):
            node_name = "H"

        #creating node x
        number_1 = 0
        number_2 = 0
        for a in range(outputNumber):
            if(outputStore[a]==node1):
                number_1 = outputStore[a][5].cget("text")
            if(outputStore[a]==node2):
                number_2 = outputStore[a][5].cget("text")
        for a in range(noiseNodeNumber):
            if(noiseNodeStore[a]==node1):
                number_1 = noiseNodeStore[a][5].cget("text")
        #perform initial node
        pixelVirtual = PhotoImage(width=3,height=1)
        if(number_of_nodes==0):
            btn = Button(master, text = str(node_name)+str(number_2)+","+str(number_1), command = lambda: selectNode(w,0) , bg = "cyan")
            save = [w.create_window(x, y, window=btn),btn,x,y]
            #append it on th end
            btnStore.append(save)
            number_of_nodes = number_of_nodes + 1
            #print("start initial node")

        else:
            #first search if a entry is zero because then a node has been removed their and we can insert a new one
            for m in range(number_of_nodes-1):
                if(btnStore[m]==0):
                    node = m
                    btn = Button(master, text = str(node_name)+str(number_2)+","+str(number_1), command = lambda: selectNode(w,node) , bg = "cyan")
                    save = [w.create_window(x, y, window=btn),btn,x,y]
                    btnStore[m] = save
                    #print("added node in existing place")

            #if no space is free and it is not the initial node append a new one on the end.
            if(number_of_nodes!=0 and node == 0):
                temp = number_of_nodes
                btn = Button(master, text = str(node_name)+str(number_2)+","+str(number_1), command = lambda: selectNode(w,temp) , bg = "cyan")
                save = [w.create_window(x, y, window=btn),btn,x,y]
                btnStore.append(save)
                number_of_nodes = number_of_nodes + 1
                #print("appended node to back of list")

        #print(btnStore)

def removeNode(w, master):
    global number_of_nodes
    global btnStore
    global lineStore
    global lineNumber

    number_of_nodes, btnStore, lineStore, lineNumber = removeNodeCall(draw,master,number_of_nodes,btnStore,lineStore,lineNumber)

"""
below are the functions regarding

-------------------------------------------------------- noise and excitation--------------------------------------------------------

important note! these functions are a bit rewritten to allow both external signals and noise manipulations. NorH = 0 is noise and NorH = 1 is excitation. Because if(var) is true if
var = 1 it becomes that if(NorH) is true when we add a excitation signal. We use this to make the below function availible for both signals. first we load in noise because it is most used
and therefor the fastes one and change it if needed for excitation
"""

def toggleNH(noise,NorH):
    global noiseStore
    global noiseNumber

    nmb = 0
    selectNumber = noiseNumber
    selectStore = noiseStore
    if(NorH):
        selectNumber = excitationNumber
        selectStore = excitationStore

    for x in range(selectNumber):
        if(selectStore[x]!=0):
            if(selectStore[x][1]==noise):
                nmb=selectStore[x][6]
    #switch color base on stat variable bound to the noise.
    if(noise.stat==1):
        noiseImgKnown = PhotoImage(file="data/noiseKnown.png")
        if(NorH):
            noiseImgKnown = PhotoImage(file="data/signalKnown.png")
        noise.image = noiseImgKnown
        nmb.configure(bg="blue")
        if(NorH):
            nmb.configure(bg="red")
        noise.configure(image=noiseImgKnown)
        noise.stat=2
    else:
        noiseImg = PhotoImage(file="data/noise.png")
        if(NorH):
            noiseImg = PhotoImage(file="data/signal.png")
        noise.image = noiseImg
        nmb.configure(bg="white")
        if(NorH):
            nmb.configure(bg="yellow")
        noise.configure(image=noiseImg)
        noise.stat=1


def addNHCall(master, draw,NorH):
    global outputStore
    global outputNumber
    global noiseNumber
    global noiseStore
    global clickOperation

    if(overlay==0):
        call = popupWindow(master)
        master.wait_window(call.top)
        node = 0
        nmb = call.value
    #find output which is selected and save it to node

        for x in range(outputNumber):
            #print(outputStore[x])
            if(outputStore[x]!=0):
                if(outputStore[x][1].stat == 2):
                    node = outputStore[x]
                    addNH(node,master,draw,NorH,nmb)

    else:
        clickOperation=3

def addNH(node,master, draw,NorH,nmb):
    global outputStore
    global outputNumber
    global noiseNumber
    global noiseStore
    global excitationStore
    global excitationNumber
    switch = 0
    #print("NorH: ",NorH)
    #move the x y to left above the center of the output
    x = node[2] - 30
    y = node[3] - 50
    if(NorH==1):
        x = node[2] + 30
        y = node[3] - 50


    #creating noise button
    noiseImg = PhotoImage(file="data/noise.png")
    if(NorH):
        noiseImg = PhotoImage(file="data/signal.png")
    nmbLabel = Label(master, text=str(nmb), bg="white")
    noise = Button(master, image = noiseImg, highlightthickness = 0, bd = 0)
    if(NorH):
        nmbLabel.configure(bg="yellow")
    noise.configure(command = lambda: toggleNH(noise,NorH))
    noise.image = noiseImg
    noise.stat = 1
    noise.nmb = nmb
    save = [draw.create_window(x,y, window=noise),noise,x,y,node[1],draw.create_window(x,y,window=nmbLabel),nmbLabel]

    #store noise in a open spot
    if(node!=0):
        if(NorH):
            for x in range(excitationNumber):
                if(excitationStore[x]==0 and switch==0):
                    excitationStore.insert(x,save)
                    switch = 1
        else:
            for x in range(noiseNumber):
                if(noiseStore[x]==0 and switch==0):
                    noiseStore.insert(x,save)
                    switch = 1

        #if no open space left append it on the end
        if(switch==0):
            if(NorH):
                excitationStore.append(save)
                excitationNumber = excitationNumber + 1
            else:
                noiseStore.append(save)
                noiseNumber = noiseNumber + 1
            #print("noise or excitation added! number: ",noise)

def removeNH(master, draw, NorH):
    global noiseStore
    global noiseNumber
    global outputStore
    global outputNumber
    global excitationNumber
    global excitationStore

    if(overlay==1):
        removeNoise()
    else:

        node = 0

        #print("trying to remove the noise")

        #find selected output
        for x in range(outputNumber):
            if(outputStore[x]!=0):
                if(outputStore[x][1].stat == 2):
                    node = outputStore[x]
                    #print("found output: ",node)

        #search for noise entry which has the selected output
        if(NorH):
            for x in range(excitationNumber):
                #print("scanning: ",excitationStore[x])
                if(excitationStore[x]!=0):
                    if(excitationStore[x][4] == node[1]):
                        #print("removing excitation")
                        #remove it
                        draw.delete(excitationStore[x][5])
                        draw.delete(excitationStore[x][0])
                        excitationStore[x] = 0
                        if(x == excitationNumber):
                            excitationNumber = excitationNumber - 1
        else:
            for x in range(noiseNumber):
                #print("scanning: ",noiseStore[x])
                if(noiseStore[x]!=0):
                    if(noiseStore[x][4] == node[1]):
                        #print("removing noise")
                        #remove it
                        draw.delete(noiseStore[x][5])
                        draw.delete(noiseStore[x][0])
                        noiseStore[x] = 0
                        if(x == noiseNumber):
                            noiseNumber = noiseNumber - 1



"""
Below are the functions for

-------------------------------------------------------- noise Node --------------------------------------------------------

tada
"""

def addNoiseNode(draw,x,y,master):
    global noiseNodeNumber
    global noiseNodeStore

    img1Btn = Button(master, highlightthickness = 0, bd = 0)
    img1Btn.configure(command = lambda: selectNoiseNode(img1Btn))
    noiseNodeNumber, noiseNodeStore = addNoiseNodeCall(draw,x,y,master,noiseNodeNumber,noiseNodeStore, img1Btn)

def selectNoiseNode(node):
    global currentAmountOutputSelected

    currentAmountOutputSelected = selectNoiseNodeCall(draw,master,noiseNodeNumber,noiseNodeStore, currentAmountOutputSelected, node)

def removeNoise():
    global noiseNodeStore
    global lineStore
    global noiseNodeNumber

    noiseNodeStore, lineStore, noiseNodeNumber = removeNoiseNodeCall(noiseNodeStore, noiseNodeNumber, lineStore, lineNumber, draw)
    removeNode(draw, master)

"""
Below are the functions for

-------------------------------------------------------- output --------------------------------------------------------

tada
"""
def addOutput(draw, x, y, master):
        global outputStore
        global outputNumber
        #create output
        switch = 0
        node = 0
        img1 = PhotoImage(file="data/outputS.png")
        img1Btn = Button(master, image=img1, highlightthickness = 0, bd = 0)
        nmb = Label(master, text="1", bg="white")
        img1Btn.configure(command = lambda: selectOutput(img1Btn))
        img1Btn.image = img1
        img1Btn.stat = 1
        img1Btn.nmb = 0
        img1Btn.order = 0
        img1Btn["border"] = "0"


        save = [draw.create_window(x, y, window=img1Btn),img1Btn,x,y,draw.create_window(x+10,y+5,window=nmb),nmb]

        #earch if their is a empty entry.
        for m in range(outputNumber):
            if(outputStore[m]==0):
                node=m
                nmb.configure(text=str(m+1))
                save[1].nmb = m
                outputStore[m] = save
                img1Btn.image.text = str(m+1)
                switch = 1

                #initial output
        if(outputNumber==0):
            outputStore.append(save)
            outputNumber = outputNumber + 1
            switch = 1

        #append if no empty entry
        if(switch==0):
            nmb.configure(text=str(outputNumber+1))
            save[1].nmb=outputNumber
            outputStore.append(save)
            outputNumber = outputNumber + 1


def removeOutput(draw,master):
    global outputStore
    global outputNumber
    #search for output and set it to 0
    removeNH(draw,master,0)
    removeNH(draw,master,1)

    for x in range(outputNumber):
        if(outputStore[x]!=0):
            if(outputStore[x][1].stat == 2):
                for i in range(lineNumber):
                    #print("i: ",i," lineStore:",lineStore[i],"")
                    if(lineStore[i]!=0):
                        if(lineStore[i][1]==outputStore[x][1] or lineStore[i][2]==outputStore[x][1]):
                            #print("i: ",i," is deleted")
                            lineStore[i][3]["bg"]="lime"
                            draw.delete(lineStore[i][0])
                            removeNode(draw, master)
                            lineStore[i]=0
                draw.delete(outputStore[x][4])
                draw.delete(outputStore[x][0])
                outputStore[x] = 0

def selectOutput(id):
    global currentAmountOutputSelected
    #each output has a stat variable which indicates state. stat == 1 is not selected, stat == 2 is selected
    #work in progress image swap werkt nog niet
    nmb = 0
    #finding corresponding label
    for x in range(outputNumber):
        if(outputStore[x]!=0):
            if(outputStore[x][1]==id):
                nmb=outputStore[x][5]


    if(id.stat==1):
        imgGreen = PhotoImage(file="data/outputGreenS.png")
        id.image = imgGreen
        id.stat = 2
        id.order = currentAmountOutputSelected
        currentAmountOutputSelected = currentAmountOutputSelected + 1
        nmb.configure(bg="limegreen")
        id.configure(image=imgGreen)
        print("setting output green")
        for a in range(lineNumber):
            if (id==lineStore[a][1] or id==lineStore[a][2]):
                draw.itemconfig(lineStore[a][0], fill="red")
    else:
        imgWhite = PhotoImage(file="data/outputS.png")
        id.image=imgWhite
        id.stat = 1
        id.order = 0
        currentAmountOutputSelected = currentAmountOutputSelected - 1
        nmb.configure(bg="white")
        id.configure(image=imgWhite)
        print("setting output white")
        for a in range(lineNumber):
            if (id==lineStore[a][1] or id==lineStore[a][2]):
                draw.itemconfig(lineStore[a][0], fill="black")

"""
below are the remaining functions

-------------------------------------------------------- Remaining --------------------------------------------------------
"""
def Dashed_line(draw,master):
    global lineshow
    global lineStore
    global lineNumber
    global overlay

    #only in the noise view dashed lines are existing
    if(overlay):
        if(lineshow):
            for x in range(lineNumber):
                if(lineStore[x][3]==1):
                    draw.itemconfig(lineStore[x][0],fill = "white")
            lineshow = 0
        else:
            for x in range(lineNumber):
                if(lineStore[x][3]==1):
                    draw.itemconfig(lineStore[x][0],fill = "black")
            lineshow = 1

def clearWindow(canvas):
    #remove everythin and set all global to 0
    global number_of_nodes
    global outputNumber
    global btnStore
    global outputStore
    global noiseStore
    global noiseNumber
    global excitationNumber
    global excitationStore
    global currentAmountOutputSelected
    global lineNumber
    global lineStore
    global noiseNodeStore
    global noiseNodeNumber
    global storeNG
    global storeNR
    global storeNH
    global overlay
    canvas.delete("all")
    number_of_nodes = 0
    outputNumber = 0
    btnStore = []
    outputStore = []
    noiseStore = []
    noiseNumber = 0
    excitationStore = []
    excitationNumber = 0
    currentAmountOutputSelected = 0
    linestore = 0
    lineNumber = 0
    noiseNodeNumber = 0
    noiseNodeStore = []
    storeNG = storeNR = storeNH = []
    overlay = 0



#Deze functie word aangeroepen van uit het menu en haalt dan 2 nodes er uit die hij door geeft aan connectoutput
def connectCall(draw,master):
    global number_of_nodes
    global btnStore
    global lineStore
    global lineNumber
    node1 = 0
    node2 = 0

    #serach first for selected outputs
    for x in range(outputNumber):
        if(outputStore[x][1].stat==2):
            if(outputStore[x][1]!=node1 and node1==0):
                node1 = outputStore[x]
            elif(node2!=outputStore[x][1]):
                node2 = outputStore[x]

    if(overlay==1):
        node2 = 0
        for x in range(noiseNodeNumber):
            if(noiseNodeStore[x][1].stat==2):
                if(noiseNodeStore[x][1]!=node2 and node2==0):
                    node2 = noiseNodeStore[x]
                    #print("found noise at: ",node2," linking to ",node1)


    #check if the node is not the same or not 0.
    if((node1==node2) or (node1 == 0 or node2 == 0)):
        print("error occured with node selection")

    else:
        #check for which order they are selected so that the last selected is the target module and the first the origin.
        if(node1[1].order > node2[1].order):
            connectOutputs(node2,node1,draw,master,1)
        else:
            connectOutputs(node1,node2,draw,master,1)
        selectOutput(node1[1])
        if(overlay==0):
            selectOutput(node2[1])
        else:
            selectNoiseNode(node2[1])

#connect outputs is nu 2 functies zodat je via plotmatrix ook connectOutputs direct kan aangroepen
def connectOutputs(node1,node2,draw,master, placeBtn):
    global number_of_nodes
    global btnStore
    global lineStore
    global lineNumber
    temp = 0
    node3 = 0

    for x in range(lineNumber):
        if(lineStore[x]!=0):
            if(node1[1]==lineStore[x][1] and node2[1]==lineStore[x][2]):
                temp = 1
    if(node1==node2):
        temp = 1
    #make sure that the connection is not made already or the nodes are the same
    #else make the connection
    if(temp==0):
        x_middle = (node2[2] + node1[2])/2
        y_middle = (node1[3] + node2[3])/2

        #draw the curve

        if((node2[2]-node1[2])!=0):
            theta = math.degrees(math.atan((node2[3]-node1[3])/(node2[2]-node1[2])))
        else:
            theta = 90;
        length_line = math.sqrt(math.pow(node2[2]-node1[2],2)+math.pow(node2[3]-node1[3],2))/2
        height_curve = length_line/3
        if(node1>node2):
            x_transfer = x_middle + math.cos(math.radians(90-theta))*height_curve
            y_transfer = y_middle - math.sin(math.radians(90-theta))*height_curve
        else:
            x_transfer = x_middle - math.cos(math.radians(90-theta))*height_curve
            y_transfer = y_middle + math.sin(math.radians(90-theta))*height_curve
        #draw the transfer
        #set btn when needed.
        if(placeBtn):
            addNode(draw,(x_transfer+x_middle)/2,(y_transfer+y_middle)/2,master,node1,node2)
            for x in range(number_of_nodes):
                if(btnStore[x]!=0):
                    if(btnStore[x][2==(x_transfer+x_middle)/2] and btnStore[x][3]==(y_transfer+y_middle)/2):
                        node3 = btnStore[x]
        else:
            #create a fake note
            node3 = [1,1]
        #end of draw the tranfer

        if(placeBtn):
            lineWidget = draw.create_line(node1[2], node1[3], x_transfer, y_transfer, node2[2], node2[3], smooth="true")
        else:
            lineWidget = draw.create_line(node1[2], node1[3], x_transfer, y_transfer, node2[2], node2[3], smooth="true", width=0.01, dash=(5, 10))
        tempStore = [lineWidget, node1[1], node2[1], node3[1]]
        lineStore.insert(lineNumber,tempStore)
        lineNumber = lineNumber+1


        #draw the arrow

        gamma = 45/2 #adjust the angle of the arrow
        length_arrow = 20 #adjust the lenght of the arrow

        sign_2 = 1
        if(node1[2]>node2[2]):
            sign_2 = -1
        epsilon = 180-gamma-theta-height_curve/20-90
        if(node1>node2):
            x_arrow0 = (x_middle+node2[2])/2 + math.cos(math.radians(90-theta))*height_curve/5*2
            y_arrow0 = (y_middle+node2[3])/2 - math.sin(math.radians(90-theta))*height_curve/5*2
        else:
            x_arrow0 = (x_middle+node2[2])/2 - math.cos(math.radians(90-theta))*height_curve/5*2
            y_arrow0 = (y_middle+node2[3])/2 + math.sin(math.radians(90-theta))*height_curve/5*2
        x_arrow1 = x_arrow0 - sign_2*math.sin(math.radians(epsilon))*length_arrow
        y_arrow1 = y_arrow0 - sign_2*math.cos(math.radians(epsilon))*length_arrow
        alpha = gamma+epsilon
        alpha_hypotenusa = sign_2*math.sin(math.radians(gamma))*length_arrow*2
        x_arrow2 = x_arrow1 - math.cos(math.radians(alpha))*alpha_hypotenusa
        y_arrow2 = y_arrow1 + math.sin(math.radians(alpha))*alpha_hypotenusa
        tempStore2 = [draw.create_line(x_arrow1, y_arrow1, x_arrow0,y_arrow0, x_arrow2, y_arrow2),node1[1],node2[1],node3[1]]
        lineStore.insert(lineNumber,tempStore2)
        lineNumber = lineNumber+1

def addWidget(input):
    #set the clickOperation variable
    global clickOperation
    clickOperation = input


def clickEvent(event):
    #on button press perform an action based on click clickOperation
    global clickOperation
    x = draw.canvasx(event.x)
    y = draw.canvasy(event.y)
    if(clickOperation==1):
        addNode(event.widget, x, y, master)
        clickOperation=0

    if(clickOperation==2):
        addOutput(event.widget, x, y, master)
        clickOperation=0

    if(clickOperation==3):
        addNoiseNode(draw, x, y, master)
        clickOperation=0

""""
    Zoom_buttons(unit.imscale)

def Zoom_buttons(scale):
    global scale_prev
    global number_of_nodes
    global btnStore
    if(scale_prev!=scale):
        scale_prev = scale
        for x in range(number_of_nodes):
            if(btnStore[x]!=0):
                btnStore[x][1].configure(height=int(scale*10),width=int(scale*30))
                btnStore[x][1].pack()
"""

"""
Below you will find the basic setup of the grid

-------------------------------------------------------- Grid interface setup and initialization --------------------------------------------------------
"""
# creating Tk window
master = Tk()
master.configure(background="gray")
master.title("Delivery Demo")
#set initial size
master.geometry("1500x1500")

#create a grid which can reize with the resizing of the box
Grid.rowconfigure(master, 0, weight=1)
Grid.columnconfigure(master, 0, weight=1)
masterFrame = Frame(master)
masterFrame.grid(row=0, column=0, sticky=N+S+E+W)
Grid.rowconfigure(masterFrame, 0, weight=1)
Grid.rowconfigure(masterFrame, 1, weight=100)
Grid.columnconfigure(masterFrame, 0, weight=100)
Grid.columnconfigure(masterFrame, 1, weight=1)

#seperating the menu in different frames which will hold all the components so that it is easier to use .grid for button placemant
#main menu is for the upper buttons, canvas is for draw, subMenu is for the component selection
mainMenu = Frame(masterFrame, bg="gray")
canvas = Frame(masterFrame, bg="white")
subMenu = Frame(masterFrame, bg="gray")

#set each frame in the grid
mainMenu.grid(row=0,sticky=N+S+E+W)
canvas.grid(row=1, sticky=N+S+E+W)
subMenu.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)

#create a canvas called draw in the canvas frame
draw = Canvas(canvas, bg="white")
draw.pack(fill="both", expand=True)

layout = [
"circular",
"kamada_kawai",
"spring",
"spectral",
"spiral"
]

layoutMethod = StringVar(master)
layoutMethod.set(layout[0])

#bind functions to events
initMainMenu(mainMenu, draw)
initSubMenu(subMenu)

#set the draw canvas with the scroll and pan option
unit = Zoom_Advanced(draw)
#bind button Release to the clickevent
unit.canvas.bind("<ButtonRelease-1>",clickEvent)

mainloop()
