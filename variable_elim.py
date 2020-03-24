"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

@Author Dimitar 'mechachki' Dimitrov
@Author Carla Schindler

Class for the implementation of the variable elimination algorithm.

"""
import factor

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
        self.PreProcessing(prob, observed)
        self.createFactors(prob)

        #todo: implement Variable Elimination

    def createFactors(self, prob):
        self.factors = []
        for k in prob.keys():
            self.factors.append(factor.Factor([key for key in prob.get(k).keys() if key != 'prob'], #
                          prob.get(k).values))
        print('factors that were created:')
        for f in self.factors:
            print('factor variables: ',f.variables)
            print('factor probability table: ',f.probabilities)

    def PreProcessing(self, prob, observed):
        for k in observed.keys():
            print('Observed variable: ', k, ' with value ', observed.get(k))
            self.reduce(prob, k, observed.get(k))

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


