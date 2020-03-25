"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

@Author Dimitar 'mechachki' Dimitrov
@Author Carla Schindler

Class for the implementation of the variable elimination algorithm.

"""
import factor
import copy

class VariableElimination():

    def __init__(self, network):
        """
        Initialize the variable elimination algorithm with the specified network.
        Add more initializations if necessary.

        """
        self.network = network

    def run(self, query, observed, elim_order):
        """
        Use the variable elimination algorithm to find out the probability
        distribution of the query variable given the observed variables

        Input:
            query:      The query variable
            observed:   A dictionary of the observed variables {variable: value}
            elim_order: Either a list specifying the elimination ordering
                        or a function that will determine an elimination ordering
                        given the network during the run

        Output: A variable holding the probability distribution
                for the query variable

        """


        prob = self.network.probabilities
        # self.PreProcessing(prob, observed)

        evidence = copy.deepcopy(observed)
        factors = self.createFactors(prob)

        reducedFactors = []
        for var, val in evidence.items():
            # remove evidence from elimination order
            if var in elim_order:
                elim_order.remove(var)
            # reduce factors based on evidence
            for factor in factors:
                reducedFactors.append(factor.reduction(var, val))

        print('POST-REDUCTION')
        for f in reducedFactors:
            print(f.variables, f.probabilities)

        if query in elim_order:
            elim_order.remove(query)

        for var in elim_order:
            reducedFactors = self.eliminateVariable(var, reducedFactors)

        for f in reducedFactors:
            print(f.variables, f.probabilities)


    def eliminateVariable(self, var, factors):
        outputFactors = []
        factorQueue = []

        for f in factors:
            if var in f.variables:
                factorQueue.append(f)
            else:
                outputFactors.append(f)

        productFactor = factorQueue[0]

        for i in range(1,len(factorQueue)):
            try:
                productFactor = productFactor.product(factors[i])
            except Exception as e:
                print(e)
        outputFactors.append(productFactor.marginalization(var))
        return outputFactors

    def createFactors(self, prob):
        factors = []
        for k in prob.keys():
            factors.append(factor.Factor([key for key in prob.get(k).keys() if key != 'prob'], #
                          prob.get(k).values))
        print('factors that were created:')
        for f in factors:
            print('factor variables: ',f.variables)
            print('factor probability table:\n',f.probabilities)

        return factors

    def PreProcessing(self, prob, observed):
        for k in observed.keys():
            print('Observed variable: ', k, ' with value ', observed.get(k))
            self.reduce(prob, k, observed.get(k))

    """
    a reduction used during pre-processing. theoretically faster than the factor's built in
    reduction as it uses dictionary to quickly look up values, incorrect as to what we desire
    in output (it keeps the reduced variable and it's values in the probability table)
    """
    def reduce(self, prob, observedName, observedValue):
        prob.pop(observedName)
        #remove the observed variable from the list of variables
        for k in prob.keys():
        #go through the variables
            if observedName in prob.get(k).keys():
            #if the currently explored variable has a dependancy on the observed variable
                origin = prob.get(k)
                #get the original table of probabilities for the explored variable
                mask = origin[observedName] == observedValue
                #create a mask that only accepts instances of desired variable status
                new = origin[mask]
                #apply the mask to get a new variable where only observed values are kept
                prob.update({k:new})
                #update the table for that explored variable with new values

"""
I PRETEND I DO NOT SEE THE BUGS
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWMMWWNNXXXKKKKK0000000KKKXXNNWWWWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWNNXXXXXKKKKKKXXXXKKKKKKKKKKKKKKKKXXNWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMWWMWWNXXKKKKXXXNNNNNNNXXNNXXXXXXXXXXXKKKK00000KKXNWWWWWMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMWWNXXKKXXXNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXKKKKK00OOO0KXNWWWWMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMWWNXKKKXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXKKKKK0000OOO0KXNWWMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMWWNXKKKXXNNXNNNNNNNNNNNNNNNNNNNNNXXXXNNNXXXXXXXXKKKKKKK00000OOOO0XWWMMWMMMMMMMMMMMMM
MMMMMMMMMMMMWMWWXKKKXXNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXKKKKKKKKK000000OOkkOKNWWWWMMMMMMMMMMM
MMMMMMMMMMWWWWXKKKXXNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXKKKKKKKKKKKK000000OOOkkOKNWWMMMMMMMMMMM
MMMMMMMMWWWWXK0KXXNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKK00000000OOOkkOKNWWWMMMMMMMM
MMMMMMMWWWNK0KXXXNNNNNNNNNNNNNNNNXNNNXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKK0000000000OOOkkOXWWWMMMMMMM
MMMMMMMWWX00KXXXNNNNNNNNNNNNNNNNNXXNXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKK000000000000OOOkkk0NWWMMMMMM
MMMMMWWNK0KKXXXXNNNNNNXNNNNNNNNNXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKK0000000000000OOOkkkOXWWMMMMM
MMMMWWN00KXXXNNNNNNNNNXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKK000K0000000000000OOOOOkkkKWWMMMM
MMMMWX00KKXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK00K00000000000000000OOOOOkkxk0NWWMM
MMWWX00KKKXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000000000000000000000OOOOOOkxkKWWWM
MWWN0O0KKKKXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK00KK00000000000000000000000000OOOOOOkkxkKWWM
MWNKO0KKKKKKXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000000000000000000000000000000OOOOOOOkkxkXWW
WWKOO0KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK00000000000000000000000000OOOOOOOkkxxOXW
WX0O00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK0KK000000000000000000OOOOOOkkkxx0W
WKO0000KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK0KKKKK000000000000000000OOOOOkkkxxOX
N0O00000KKK0xk0KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK00KKKKKKKKK0000000000OkO000OOOOOkkkkxxK
XOO00000KKKx,.ck0KKKKKKKKKKKKKKKKKKKKKKKK0OO0KKK00O0KKKKKKKKKK0KKKKKKKKKK0000000Oo',dO0OOOOOkkkkxxx0
KOO0000000K0d,.'d0KKKKKKKK00KKKKK0KKKKK0Ol,cOKKK0d;:d0KKKKKKKKKKKKKKKKKKK000000kc..:kOOOOOOOkkkkkxdk
0kOO000000000kc..:dOKKKKKKKKKKKKKKK0K0xc'.;d0KKK0o;..;d0KKKKKKKKKKKKKKKKK0000ko'.,oOOOOOOOOOkkkkxxdx
0OOO0000000000Ox:..,cdO00KKKKKKK00Oxl,.':dO0000000Ox:..,cxOKKKK0000KKKKKK0ko;'.;okOOOOOOOOOkkkkkxxdx
0kOO0000000000000kl;...',;::::;;,''.':okO00000000000Oxl,..':ldxkkO0OOOxdc;..'cdOOOOOOOOOOOkkkkkxxxdx
0kOOO000000000000000kdl:;;;::::ccloxO000000000000000000Oko:,......''.....,ldkOOOOOOOOOOOOOOkkkkxxxdx
KkOO0O00000000000000000000000000000000000000000000000000000OOkdoollllodxkO0OO00OOOOOOOOOOkkkkkkxxddx
XOkOOOO0000000000000000000000000000000000000000000000000000000000000000O00OOO00OOOOOOOOOkkkkkkxxdddk
N0kOOOO00000000000000000000000000000000000000000000000000000000000000000000OOOOOOOOOOOOkkkkkkxxxdddO
WKkkOOOOO0000000000000000000000000000000000000000000000000000000000000OOOOOOOOOOOOOOOOOkkkkkxxxddoxK
WNOxkOOOOOO000000000000000000000000000000000000000000000000000000OO00OOOOOOOOOOOOOOOOOkkkkkxxxxdookX
WWKkkkkOOOOOOOO00000000OOOO0000000000000000000000OOOO00O00000OOOOOOOOOOOOOOOOOOOOOOkkkkkkkkxxxddox0N
WWN0xxkkOOOOOOOOOO00OOxdddddddddddddddddddddddddddddddddddddddddddddddddddxkOOOOOOkkkkkkkxxxxdoodOXN
MWWN0xxkkOOOOOOOOOOOOx:,'''''''''''',,''''','''''''''''''''''''''''''''''':dkOOOOkkkkkkkxxxxddookKNW
MMWWNOxxkkkkOOOOOOOOOOkxxxxxxxxxxxxxxxkkxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxkOOOOkkkkkkkxxxxddookKXWW
MMMMWNOxxxkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkxxxddooox0XWWM
MMMMWWN0xdxxkkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkxxxxddolokKXNWWM
MMMMMWWWKxddxxkkkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkxxxxdooldOKNWWMMM
MMMMMMWWWXOddxxxkkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkxxxddolox0XNWWMMMM
MMMMMMMMMWNKxdddxxxkkkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkxxxddooxOKNWWWMMMMM
MMMMMMMMMMMWXOdodxxxkkkkkkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkxxxdolox0XNWWMMMMMMM
"""