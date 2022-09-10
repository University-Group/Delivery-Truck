from copy import deepcopy
from termcolor import colored
from queue import PriorityQueue
from tabulate import tabulate
import time

class placePackage():
    count = 0
    @staticmethod
    def inc():
        placePackage.count += 1
    
    def __init__(self,name):

        self.type = name[0]
        self.num = int(name[1:])
        self.isDone = False
        placePackage.inc()
    
    def getNum(self):
        return self.num
    
    def getIsDone(self):
        return self.isDone
    
    def getType(self):
        return self.type
    
    def setIsDone(self, boolean):
        self.isDone = boolean
    
    def __str__(self):
        return self.type + str(self.num)

class cell():

    def __init__(self,isVailible=True,place_package=None):
        self.isVailible = isVailible
        self.Package = place_package
        self.values = []

    def addValue(self,num):
        self.values.append(str(num))
    
    def getTypePackage(self):
        if self.Package is None:
            return None
        return self.Package.getType()
    
    def getNumPackage(self):
        if self.Package is None:
            return None
        
        return self.Package.getNum()
    
    def getIsDonePackage(self):
        if not self.containPackage() :
            return False
        return self.Package.getIsDone()

    def containPackage(self):
        if self.Package is None:
            return False
        return True
    
    def setIsDonePackage(self):
        self.Package.setIsDone(True)

    def __str__(self):
       return  str(self.Package) + ' ('+', '.join(self.values) + ')'

class State():

    def __init__(self,grid,start):
        '''
            grid is : list of list of CELL
            start is : tupel of two number (x , y)  
            truckPosition : position of truck and in first is equal start then is CHANGED
            carriedPackages : list of number (number of carried package)
            delivered Packages : list of number (number of delivered package)
        '''
        self.parent = None
        self.cost = 0
        self.grid = grid
        self.posPlacePackage = dict()
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j].containPackage():
                    if self.posPlacePackage.get(str(self.grid[i][j].getNumPackage()),None) is None:
                        self.posPlacePackage[str(self.grid[i][j].getNumPackage())] = []
                    self.posPlacePackage[str(self.grid[i][j].getNumPackage())].append((self.grid[i][j].getTypePackage(),i,j))
        self.start = start
        self.truckPosition = list(start)
        self.numTotalPackage = int(placePackage.count / 2)
        self.deliveredPackages = []
        self.carriedPackages = []
        self.step = 0
    
    def addCarriedPackage(self,num):
        self.carriedPackages.append(str(num))
    
    def deleteCarriedPackage(self,num):
        if self.isCarriedPackage(num):
            self.carriedPackages.remove(str(num))
    
    def nextState(self):
        processes = self.canMove()
        states = []
        for process in processes :
            states.append(self.move(process))
            
        return states

    def canMove(self):
        lst = []
        x, y = self.truckPosition
        # Top
        if(self.inGrid(x - 1, y) and self.grid[x - 1][y].isVailible):
            lst.append((1, x - 1, y))

        # Bottom
        if(self.inGrid(x + 1, y) and self.grid[x + 1][y].isVailible):
            lst.append((1, x + 1, y))

        # Right
        if(self.inGrid(x, y + 1) and self.grid[x][y + 1].isVailible):
            lst.append((1, x, y + 1))

        # Left
        if(self.inGrid(x, y - 1) and self.grid[x][y - 1].isVailible):
            lst.append((1, x, y - 1))

        if self.grid[x][y].containPackage() and not self.grid[x][y].getIsDonePackage():
            if self.grid[x][y].getTypePackage() == 'D' :
                if self.isCarriedPackage(self.grid[x][y].getNumPackage()) :
                    lst.append((0,'D',self.grid[x][y].getNumPackage()))
            else :
                lst.append((0,'P',self.grid[x][y].getNumPackage()))

        return lst

    def move(self, process) :
        childState = None
        if process[0] == 1 :
            childState = deepcopy(self)
            childState.truckPosition = [process[1], process[2]]
            childState.step += 1
            childState.grid[process[1]][process[2]].addValue(childState.step)
            childState.cost += (1 + childState.carriedPackages.__len__())
            childState.parent = self
        else :
            if process[1] == 'P' :
                childState = deepcopy(self)
                x, y = childState.truckPosition
                childState.grid[x][y].addValue('P')
                childState.grid[x][y].setIsDonePackage()
                childState.parent = self
                childState.addCarriedPackage(process[2])
            else :
                childState = deepcopy(self)
                x, y = childState.truckPosition
                childState.grid[x][y].addValue('D')
                childState.grid[x][y].setIsDonePackage()
                childState.parent = self
                childState.deliveredPackages.append(str(process[2]))
                childState.deleteCarriedPackage(process[2])

        return childState

    def inGrid(self,x,y):
        lenX = self.grid.__len__()
        lenY = self.grid[0].__len__()
        return x < lenX and x >= 0 and y < lenY and y >= 0
        
    def isCarriedPackage(self,num):
        return str(num) in self.carriedPackages

    def isGoal(self):
        if(list(self.start) == self.truckPosition and self.numTotalPackage == self.deliveredPackages.__len__()):
            return True
        return False

    def displayState(self):

        print("\n", end="")
        listAll = []
        for index,row in enumerate(self.grid) :
            listInside = [] 
            for j,cell in enumerate(row) :
                if([index, j] == self.truckPosition):
                    if(cell.values != []):
                        listInside.append('🚚' + ' ('+', '.join(cell.values) + ')')
                    else:
                        listInside.append("🚚")
                elif([index, j] == list(self.start)):
                    if(cell.values != []):
                        listInside.append('S' + ' ('+', '.join(cell.values) + ')')
                    else:
                        listInside.append("S")
                elif(cell.isVailible) :
                    if(cell.containPackage() and cell.values != []):
                        listInside.append(str(cell))
                    elif(cell.containPackage() and cell.values == []):
                        listInside.append(str(cell.Package))
                    elif(cell.values != []):
                        listInside.append('('+', '.join(cell.values) + ')')
                    else:
                        listInside.append(".")
                else :
                    listInside.append("🏠")
            listAll.append(listInside)

        print(tabulate(listAll, tablefmt='fancy_grid'))
        print("\n", end="")

    # def generate_key(self) :
    #     hash = str(self.truckPosition[0]) + ',' + str(self.truckPosition[1])+ ' ' + ','.join(self.carriedPackages) +'-'+ str(len(self.deliveredPackages))
    #     return hash

    # def generate_key(self) :
    #     leftPackages = self.numTotalPackage - (self.carriedPackages.__len__() + self.deliveredPackages.__len__())
    #     hash = str(self.truckPosition[0]) + ',' + str(self.truckPosition[1]) + ' ' + str(leftPackages) + ' ' + str(self.carriedPackages.__len__())
    #     return hash

    def generate_key(self) :
        hash = str(self.truckPosition[0]) + ',' + str(self.truckPosition[1]) + ' ' + ','.join(self.carriedPackages) + ' ' + ','.join(self.deliveredPackages)
        return hash

    def distanceBetweenTwoPoint(self, point, pointFrom = None) : # point is (type, x, y)
        if len(point) == 2:
            point = ('', point[0],point[1])
        if not pointFrom is None and len(pointFrom) == 2:
            pointFrom = ('', pointFrom[0],pointFrom[1])
        if pointFrom is None:
            pointFrom = ('',self.truckPosition[0],self.truckPosition[1])
        return abs(pointFrom[1] - point[1]) + abs(pointFrom[2] - point[2])

    def firstHoristic(self):
        return self.distanceBetweenTwoPoint(self.start)

    def placesSpecificPackage(self, indexPackage = None): #indexPackagre from dict
        tP = ()
        tD = ()
        #posPLacePackage is { 'numPackage' = [(type, x, y),(type, x, y)]        ,  .... }
        if indexPackage is None:
            indexPackage = next(iter(self.posPlacePackage))
            package = self.posPlacePackage[indexPackage]
            tP,tD = (package[0],package[1]) if package[0][0] == 'P' else (package[1],package[0])
        else :
            package = self.posPlacePackage[indexPackage]
            tP,tD = (package[0],package[1]) if package[0][0] == 'P' else (package[1],package[0])
        return tP,tD,indexPackage

    def secondHoristic(self, indexPackage = None): #indexPackage from dict
        pointP, pointD, numPackage = self.placesSpecificPackage(indexPackage)
        if numPackage in self.deliveredPackages:
            return self.firstHoristic()
        elif numPackage in self.carriedPackages:
            return self.distanceBetweenTwoPoint(pointD, self.truckPosition) + self.distanceBetweenTwoPoint(self.start, pointD)
        else:
            return self.distanceBetweenTwoPoint(pointP) + self.distanceBetweenTwoPoint(pointD, pointP) + self.distanceBetweenTwoPoint(self.start, pointD)
    
    def thirdHoristic(self):
        lst = []
        for i in self.posPlacePackage.keys():
            lst.append(self.secondHoristic(i))
        return max(lst)

class Logic :

    countOfStates = 0
    costOfSolution = 0
    timeOfSolution = 0
    visited = []

    @staticmethod
    def startGame(fileName):

        init = Logic.initState(fileName)

        print(colored("\nChoose The Algorithm\n", 'cyan'))
        print("1. Dijkstra")
        print("2. AStar With The First Horistic")
        print("3. AStar With The Second Horistic")
        print("4. AStar With The Third Horistic")
        print("5. Exit")
        inp = input(colored("\nWhat Do You Want: ", 'green'))
        while inp.isnumeric() != True or int(inp) < 1 or int(inp) > 5 :
            inp = input(colored("\nWhat Do You Want: ", 'green'))
            
        if(int(inp) == 1):
            Logic.Dijkstra(init).displayState()
            Logic.detailsOfGame()
        elif(int(inp) == 2):
            Logic.AStar(init, 1).displayState()
            Logic.detailsOfGame()
        elif(int(inp) == 3):
            Logic.AStar(init, 2).displayState()
            Logic.detailsOfGame()
        elif(int(inp) == 4):
            Logic.AStar(init, 3).displayState()
            Logic.detailsOfGame()
        else:
            Logic.endOfTheGame()

    @staticmethod
    def initState(filename):
        grid = []
        start = ()
        j = 0
        f = open(filename,"r")
        for line in f.readlines():
            line = line.split()
            lst = []
            for i in range(len(line)):
                if line[i] == 'T' :
                    start = (j,i)
                    lst.append(cell())
                    continue
                if line[i] == '.' :
                    lst.append(cell())
                elif line[i] =='#' :
                    lst.append(cell(False))
                else:
                    lst.append(cell(True,placePackage(line[i])))
            grid.append(lst)
            j += 1
        return State(grid,start)

    @staticmethod
    def Dijkstra(state) :
        start = time.time()
        index = 0
        pqueue = PriorityQueue()
        pqueue.put((0, 1, state))
        while not pqueue.empty() :
            elFormQueue = pqueue.get()
            element = elFormQueue[2]
            Logic.countOfStates += 1

            if (element.isGoal()) :
                Logic.costOfSolution = element.cost
                end = time.time()
                Logic.timeOfSolution = end - start
                return element

            hash = element.generate_key()
            indexOfState = Logic.searchInVisitedStates(hash)
            if(indexOfState != -1 and Logic.visited[indexOfState][1] <= element.cost):
                continue
            # elif (indexOfState != -1 and Logic.visited[indexOfState][1] > element.cost) :
            #     print("Hi")
            #     Logic.visited[indexOfState] = [hash, element.cost]
            else :
                Logic.visited.append([hash, element.cost])
            
            states = element.nextState()
            for el in states:
                pqueue.put((el.cost, index, el))
                index += 1

        return None

    @staticmethod
    def AStar(state, numOfHoristic) :
        start = time.time()
        index = 0
        pqueue = PriorityQueue()
        pqueue.put((0, 1, state))
        while not pqueue.empty() :
            elFormQueue = pqueue.get()
            element = elFormQueue[2]
            Logic.countOfStates += 1

            if (element.isGoal()) :
                Logic.costOfSolution = element.cost
                end = time.time()
                Logic.timeOfSolution = end - start
                return element

            hash = element.generate_key()
            indexOfState = Logic.searchInVisitedStates(hash)
            if(indexOfState != -1 and Logic.visited[indexOfState][1] <= element.cost):
               continue
            # elif (indexOfState != -1 and Logic.visited[indexOfState][1] > element.cost) :
            #     Logic.visited[indexOfState] = [hash, element.cost]
            else :
                Logic.visited.append([hash, element.cost])

            states = element.nextState()
            for el in states:
                if numOfHoristic == 1:
                    pqueue.put((el.cost + el.firstHoristic(), index, el))
                elif numOfHoristic == 2:
                    pqueue.put((el.cost + el.secondHoristic(), index, el))
                else:
                    pqueue.put((el.cost + el.thirdHoristic(), index, el))
                
                index += 1

        return None

    @staticmethod
    def printPath(state) :
        if(state == None):
            return
        Logic.printPath(state.parent)
        state.displayState()

    @staticmethod
    def detailsOfGame():
        print(colored(f"\n\t\t\t\t\t  The Number Of Generation Nodes: {Logic.countOfStates}", 'yellow'))
        print(colored(f"\n\t\t\t\t\t  The Cost Of Solution: {Logic.costOfSolution}", 'yellow'))
        print(colored(f"\n\t\t\t\t\t  The Time Of Solution: {Logic.timeOfSolution:.4} s", 'yellow'))

    @staticmethod
    def searchInVisitedStates(hash):
        for (index,row) in enumerate(Logic.visited) :
            if hash == row[0]:
                return index
        return -1
        
    @staticmethod
    def endOfTheGame():
        print("\n\t\t\t\t\t", end="")
        print(colored("# "*22, 'cyan'))
        print(colored("\n\t\t\t\t\t#\t       T H A N K Y O U\t\t  #", 'cyan'))
        print("\n\t\t\t\t\t", end="")
        print(colored("# "*22, 'cyan'))


########################### Main ###########################

Logic.startGame('c:/Users/USER/Desktop/test3.txt')