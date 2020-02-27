"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

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

        # print(prob.get('Earthquake').values)
        # skrrt = factor.Factor([key for key in prob.get('Earthquake').keys() if key!='prob'],
        #                         prob.get('Earthquake').values)
        # print(skrrt.variables)
        # print(skrrt.probabilities)


        # alarm = prob.get('Alarm')
        # print(alarm)
        # alarm_BT_mask = alarm['Burglary'] == 'True'
        # alarm_BT = prob.get('Alarm')[alarm_BT_mask]
        # print (alarm_BT)
        #
        # print(prob.get('Alarm').keys())
        # if('Burglary' in prob.get('Alarm').keys()):
        #     print('success')

    def createFactors(self, prob):
        self.factors = []
        for k in prob.keys():
            self.factors.append(factor.Factor([key for key in prob.get(k).keys() if key != 'prob'],
                          prob.get(k).values))

        for f in self.factors:
            print(f.variables)
            print (f.probabilities)


    def PreProcessing(self, prob, observed):
        for k in observed.keys():
            print('Observed variable: ', k, ' with value ', observed.get(k))
            self.removeObserved(prob, k, observed.get(k))

    def removeObserved(self, prob, observedName, observedValue):
        prob.pop(observedName)
        for k in prob.keys():
            if observedName in prob.get(k).keys():
                origin = prob.get(k)
                mask = origin[observedName] == observedValue
                new = origin[mask]
                prob.update({k:new})


