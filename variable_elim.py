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


