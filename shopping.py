import os, sys
import yaml
import argparse
import logging
from collections import defaultdict

# TODO: remove this and rely on command line arguments
CUSTOM_ARGS = ['-i', 'test/inventories.json', '-l', 'test/shopping_list.json', '-v']

class ShoppingListSolver(object):
    """
    Given a list of shopping stores and their inventory from a JSON file and a
    shopping list, find the minimum number of stores to visit in order to satisify
    this shopping list. The solver finds all possible minimum solutions and print
    them to a file.
    """
    def __init__(self, inventoryFile, loggingLevel):
        """
        Initialize member variables and read stores information
        """
        logging.basicConfig(level=loggingLevel, format='[%(levelname)s] %(message)s')
        logging.info("Initializing solution solver class")
        self._solutions = list()
        self._storesNames = list()
        self._storesInventories = list()
        self._parseInventoryFile(inventoryFile)


    def solve(self, shoppingListFile, outputFile):
        """
        Parse shopping list file and write all minimum solutions to output file
        """
        logging.info("Solving using shopping list from file: {}".format(shoppingListFile))
        shoppingList = self._parseShoppingListFile(shoppingListFile)

        self._minSolLen = sys.maxsize
        self._solutions = list()
        self._solveHelper(shoppingList, solutionSoFar=[], currentIndex=0)
        self._writeSolutions(outputFile)


    def _parseInventoryFile(self, inventoryFile):
        """
        Parse input JSON file of list of stores and their inventory
        """
        logging.info("Parsing the inventory JSON from file: {}".format(inventoryFile))
        
        stores = None
        with open(inventoryFile, "r") as f:
            data = yaml.safe_load(f)
            assert "stores" in data
            stores = data["stores"]

        for storeInfo in stores:
            assert "name" in storeInfo
            self._storesNames.append(storeInfo["name"])
            
            if "inventory" in storeInfo:
                inventory = defaultdict(int, storeInfo["inventory"])
            else:
                inventory = defaultdict(int)
            self._storesInventories.append(inventory)

        self._numStores = len(self._storesNames)
        logging.info("Parsed {} stores".format(self._numStores))
        logging.debug("Stores Names: {}".format(self._storesNames))
        logging.debug("Stores Inventory: {}".format(self._storesInventories))


    def _parseShoppingListFile(self, shoppingListFile):
        """
        Parse shopping list from JSON
        """
        logging.info("Parsing Shopping list JSON")
        shoppingList = None
        with open(shoppingListFile, "r") as f:
            shoppingList = yaml.safe_load(f)
        
        logging.debug("Got: {}".format(shoppingList))
        return shoppingList


    def _solveHelper(self, shoppingList, solutionSoFar, currentIndex):
        """
        Recursively try all possible solutions
        """
        if currentIndex >= self._numStores:
            return
        
        # Try without this store
        self._solveHelper(shoppingList, solutionSoFar, currentIndex+1)

        # Shop in current store
        inventory = self._storesInventories[currentIndex]
        remainingList = {k: max(v - inventory[k], 0) for k, v in shoppingList.items() if max(v - inventory[k], 0)}

        # If this store contain any interesting items, try it
        numRemaining = sum(remainingList.values())
        if numRemaining == sum(shoppingList.values()):
            return
        
        # If solution is found, add it and update minimum. Otherwise, keep searching
        if numRemaining == 0:
            self._addSolution(solutionSoFar + [currentIndex])
        else:
            self._solveHelper(remainingList, solutionSoFar + [currentIndex], currentIndex+1)


    def _addSolution(self, solution):
        """
        Add solution and remove any non-optimal solutions
        """
        if len(solution) > self._minSolLen:
            return
        elif len(solution) == self._minSolLen:
            self._solutions.append(solution)
        else:
            self._minSolLen = len(solution)
            self._solutions = [x for x in self._solutions if len(x) <= len(solution)]
            self._solutions.append(solution)
        pass


    def _writeSolutions(self, outputFile):
        """
        Write solutions to the output file
        """
        logging.info("Found {} solutions!".format(len(self._solutions)))
        logging.info("Writing solutions to file: {}".format(outputFile))

        data = ["The shopping list can be satisfied by visiting {} store(s):".format(self._minSolLen)]
        for solution in self._solutions:
            data.append(", ".join([self._storesNames[storeID] for storeID in solution]))

        with open(outputFile, 'w') as f:
            f.write("\n".join(data))
        
        pass
    
    pass # End of ShoppingListSolver class


def main():
    """
    Test entry point to the shopping list solver class
    """
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inventory', required=True)
    argParser.add_argument('-l', '--shopping-list', required=True)
    argParser.add_argument('-o', '--output', default='output.txt')
    argParser.add_argument('-v', '--verbose', action='store_true')

    if CUSTOM_ARGS:
        parsedArgs = argParser.parse_args(CUSTOM_ARGS)
    else:
        parsedArgs = argParser.parse_args()

    inventoryFile = os.path.abspath(parsedArgs.inventory)
    shoppingListFile = os.path.abspath(parsedArgs.shopping_list)
    outputFile = os.path.abspath(parsedArgs.output)
    if parsedArgs.verbose:
        loggingLevel = logging.INFO
    else:
        loggingLevel = logging.CRITICAL

    # Actual solution start here
    s = ShoppingListSolver(inventoryFile, loggingLevel)
    s.solve(shoppingListFile, outputFile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
