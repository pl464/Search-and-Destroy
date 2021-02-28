import random
from random import randint

#a cell in the map. terrain is stored as "FLAT", "HILLY", "FOREST", or "CAVES".
class Cell:
    terrain = ""
    containsTarget = False

#returns a list of lists of Cells
def gen_grid (d):
    #initialize cells with terrain
    grid = []
    for x in range (0, d):
        row = []
        for y in range (0, d):
            cell = Cell()
            t = random.random()
            if (t >= 0 and t < 0.2):
                cell.terrain = "FLAT"
            elif (t >= 0.2 and t < 0.5):
                cell.terrain = "HILLY"
            elif (t >= 0.5 and t < 0.8):
                cell.terrain = "FOREST"
            elif (t >= 0.8 and t < 1):
                cell.terrain = "CAVES"
            row.append(cell)
        grid.append(row)
    #randomly place target
    t1 = randint(0, d-1)
    t2 = randint(0, d-1)
    grid[t1][t2].containsTarget = True
    print("[NEW MAP]: Target is in terrain " + grid[t1][t2].terrain)
    return grid

#below is a function to generate a grid with a target in a forced terrain type.
#it was used to see how specific terrain types might affect agent performance.
'''
#generate a grid with target in a specific terrain type
def gen_grid (d, forcedTerrain):
    #initialize cells with terrain
    grid = []
    for x in range (0, d):
        row = []
        for y in range (0, d):
            cell = Cell()
            t = random.random()
            if (t >= 0 and t < 0.2):
                cell.terrain = "FLAT"
            elif (t >= 0.2 and t < 0.5):
                cell.terrain = "HILLY"
            elif (t >= 0.5 and t < 0.8):
                cell.terrain = "FOREST"
            elif (t >= 0.8 and t < 1):
                cell.terrain = "CAVES"
            row.append(cell)
        grid.append(row)
    #randomly place target
    while (True):
        t1 = randint(0, d-1)
        t2 = randint(0, d-1)
        if (grid[t1][t2].terrain == forcedTerrain):
            grid[t1][t2].containsTarget = True
            break
    return grid
'''

#initializes the probabalistic knowledge base
def gen_belief_grid (d):
    grid = []
    priorBelief = 1/(d*d)
    for x in range (0, d):
        row = []
        for y in range(0, d):
            row.append(priorBelief)
        grid.append(row)
    return grid

def print_map (grid):
    for row in grid:
        for cell in row:
            tail = ' '
            if (cell.containsTarget == True):
                tail = '<'
            if (cell.terrain == "FLAT"):
                print('P', end=tail)
            elif (cell.terrain == "HILLY"):
                print('H', end=tail)
            elif (cell.terrain == "FOREST"):
                print('F', end=tail)
            elif (cell.terrain == "CAVES"):
                print('C', end=tail)
        print('\n')

def print_beliefs (belief_grid):
    for row in belief_grid:
        for p in row:
            p*=100
            print('%.3f'%(p), end=' ')
        print('\n')

#given a map, tells whether it is at least 24% caves. Used for Improved Agent
def isCaveHeavy (grid):
    caveCount = 0
    for row in grid:
        for cell in row:
            if (cell.terrain == "CAVES"):
                caveCount += 1
    if (caveCount / (len(grid)*len(grid)) > 0.24):
        return True
    else:
        return False

#given a map, tells whether it is at least 36% forests. Used for Improved Agent
def isForestHeavy (grid):
    forestCount = 0
    for row in grid:
        for cell in row:
            if (cell.terrain == "FOREST"):
                forestCount += 1
    if (forestCount / (len(grid)*len(grid)) > 0.36):
        return True
    else:
        return False

#returns number of probabilistic queries
def search_and_destroy(grid, belief_grid, agentType):
    
    numSearches = 0
    
    #variable below is for Basic Agent 3 (calculating manhattan distance)
    oldLocation = (-1,-1)
    
    #variables/blocks below are for Improved Agent
    caveHeavy = False
    forestHeavy = False
    if (agentType == 4):
        if (isCaveHeavy(grid) == True):
            print("Cave heavy!")
            caveHeavy = True
        if (isForestHeavy(grid) == True):
            print("Forest heavy!")
            forestHeavy = True
    
    while (True):
        location = getNextSearchLocation(grid, belief_grid, agentType, oldLocation)
        row = location[0]
        col = location[1]
        
        searchCell = grid[row][col]
        numSearches+=1
        #if the target is found, return the number of searches; terminate
        if (search(searchCell) == True):
            return numSearches
        else:
            #update belief of cell (Bayes)
            #P(belief|data) = P(F|target was there)*oldBelief/P(data)
            oldBelief = belief_grid[row][col]
            newBelief = oldBelief
            #the variable below represents P(F|target was there)
            terrain_modifier = 0
            if (searchCell.terrain == "FLAT"):
                terrain_modifier = 0.1
            elif (searchCell.terrain == "HILLY"):
                terrain_modifier = 0.3
            elif (searchCell.terrain == "FOREST"):
                terrain_modifier = 0.7
                if (forestHeavy == True):
                    for x in range(0, 3):
                        numSearches+=1
                        if (search(searchCell) == True):
                            print("Found by extra searches of the forest.")
                            return numSearches
            elif (searchCell.terrain == "CAVES"):
                terrain_modifier = 0.9
                if (caveHeavy == True):
                    for x in range(0, 6):
                        numSearches+=1
                        if (search(searchCell) == True):
                            print("Found by extra searches of the caves.")
                            return numSearches
            newBelief *= terrain_modifier
            #the variable below represents P(data)
            p_data = (terrain_modifier * oldBelief) + (1-oldBelief)
            newBelief /= p_data
            belief_grid[row][col] = newBelief
            #normalize the other probabilities
            belief_grid = normalize(belief_grid)
            #print_beliefs(belief_grid)

            oldLocation = location

#using agent type, go through the map and determine best cell to search next
def getNextSearchLocation(grid, belief_grid, agentType, oldLocation):
    bestScore = -1
    if (agentType == 3):
        bestScore = float('inf')
    bestCell = (-1, -1)
    for x in range(0, len(grid)):
        for y in range(0, len(grid)):
            score = belief_grid[x][y]
            if (agentType == 2 or agentType == 3 or agentType == 4):
                cell= grid[x][y]
                if (cell.terrain == "FLAT"):
                    score *= 0.9
                elif (cell.terrain == "HILLY"):
                    score *= 0.7
                elif (cell.terrain == "FOREST"):
                    score *= 0.3
                elif (cell.terrain == "CAVES"):
                    score *= 0.1
            #if agent 3, additionally modify each score with man dist
            #and update bestScore with smallest score
            if (agentType == 3):
                x_dist = abs(oldLocation[0] - x)
                y_dist = abs(oldLocation[1] - y)
                man_dist = x_dist + y_dist
                score = (1+man_dist) / score
                if (score < bestScore):
                    bestScore = score;
                    bestCell = (x, y)
            #otherwise, use largest score
            if (agentType != 3):
                if (score > bestScore):
                    bestScore = score
                    bestCell = (x, y)
                    
    return bestCell

#search the cell; return T or F given the terrain
def search(cell):
    t = random.random()
    if (cell.containsTarget == True):
        if (cell.terrain == "FLAT"):
            if (t >= 0 and t < 0.9):
                return True
            else: return False
        elif (cell.terrain == "HILLY"):
            if (t >= 0 and t < 0.7):
                return True
            else: return False
        elif (cell.terrain == "FOREST"):
            if (t >= 0 and t < 0.3):
                return True
            else: return False
        elif (cell.terrain == "CAVES"):
            if (t >= 0 and t < 0.1):
                return True
            else: return False
    else:
        return False

#normalizes belief grid so that sum of beliefs = 1
def normalize(belief_grid):
    belief_sum = 0
    new_belief_grid = []
    for row in belief_grid:
        for p in row:
            belief_sum += p
    norm_const = 1 / belief_sum

    for x in range(0, len(belief_grid)):
        row = []
        for y in range(0, len(belief_grid)):
            new_belief = belief_grid[x][y] * norm_const
            row.append(new_belief)
        new_belief_grid.append(row)
    return new_belief_grid

################## TEST SUITE #####################

dim = 50
numMaps = 20
numReps = 5
a1_results = []
a2_results = []
a3_results = []
a4_results = []

for x in range (0, numMaps):
    grid = gen_grid(dim)
    belief_grid = gen_belief_grid(dim)
    s1 = 0
    s2 = 0
    s3 = 0
    s4 = 0
    for y in range (0, numReps):
        s1 += search_and_destroy(grid, belief_grid, 1)
        s2 += search_and_destroy(grid, belief_grid, 2)
        s3 += search_and_destroy(grid, belief_grid, 3)
        s4 += search_and_destroy(grid, belief_grid, 4)
    a1_results.append(s1 / numReps)
    a2_results.append(s2 / numReps)
    a3_results.append(s3 / numReps)
    a4_results.append(s4 / numReps)
    print("Done with map " + str(x) + "... results so far:")
    print("A1:")
    print(a1_results)
    print("A2:")
    print(a2_results)
    print("A3:")
    print(a3_results)
    print("A4:")
    print(a4_results)
    
print()
print("Agent 1: ", end = ' ')
print("AVERAGE: " + str(sum(a1_results)/len(a1_results)), end = ' ')
print(a1_results)
print()
print("Agent 2: ", end = ' ')
print("AVERAGE: " + str(sum(a2_results)/len(a1_results)), end = ' ')
print(a2_results)
print()
print("Agent 3: ", end = ' ')
print("AVERAGE: " + str(sum(a3_results)/len(a1_results)), end = ' ')
print(a3_results)
print()
print("Agent 4: ", end = ' ')
print("AVERAGE: " + str(sum(a4_results)/len(a1_results)), end = ' ')
print(a4_results)
