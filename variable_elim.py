"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

@Author Dimitar 'mechachki' Dimitrov s1018291
@Author Carla Schindler s1017233

Class for the implementation of the variable elimination algorithm.

"""
import factor
import copy
import numpy as np

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
        print("\n########################################################\n")
        print('Given factors(nodes) and their probability distribution tables:')
        origin = self.createFactors(prob)

        ##################################################################
        #           REDUCTION USING FACTOR'S REDUCTION FUNCTION          #
        #                       THIS CODE IS OBSOLETE                    #
        ##################################################################
        # for var, val in evidence.items():                              #
        #     # remove evidence from elimination order                   #
        #     if var in elim_order:                                      #
        #         elim_order.remove(var)                                 #
        #     # reduce factors based on evidence                         #
        #     for factor in origin:                                      #
        #         reducedFactors.append(factor.reduction(var, val))      #
        ##################################################################


        print("\n########################################################\n")
        #pre-processing: reduction of observed variables
        self.PreProcessing(prob, observed)
        print("\n########################################################\n")


        print('Reduced factors ready for variable elimination')
        reducedFactors = self.createFactors(prob)
        # for f in reducedFactors:
        #     print(f.variables, f.probabilities)

        print("\n########################################################\n")

        print('BEGIN VARIABLE ELIMINATION')

        print("\n########################################################\n")

        #execute elimination of each variable in the elimination order
        for var in elim_order:
            reducedFactors = self.eliminateVariable(var, reducedFactors)

        print("\n########################################################\n")
        print('END VARIABLE ELIMINATION')
        print("\n########################################################\n")

        #do post-processing
        result= self.postProcessing(self.findQueriedFactor(reducedFactors, query), query)

        print("\n########################################################\n")

        print('RESULT:\nVariable ', query,' has: ')
        for f in result.probabilities:
            print('probability ', f[-1], ' for value ', f[0])

    def normalization(self, factorr):
        print('Normalizing...')
        sum = 0
        for outcome in factorr.probabilities:
            #compute sum of probabilities
            sum= sum + float(outcome[-1])
        print('Un-normalized sum of outcome probabilities: ', sum)
        # create the new normalized factor
        normalizedFactor = []
        for outcome in factorr.probabilities:
            #create normalized outcome
            normalizedOutcome = []
            for i in range(0,len(outcome)-1):
                #copy every variable value from original outcome
                normalizedOutcome.append(outcome[i])
            #get the normalized probability value by dividing particular probability value by the total probability sum
            normalizedOutcome.append(float(outcome[-1]) / sum)
            #add the normalized outcome to normalized factor
            normalizedFactor.append(normalizedOutcome)
        print('Probability table post normalization:\n', np.asarray(normalizedFactor))
        return factor.Factor(factorr.variables, np.asarray(normalizedFactor))

    def postProcessing(self, factor, query):
        print('POST PROCESSING:')

        #perform marginalization on every non-query variable left in the factor
        #this is just so we can remove observed variables from the factor and make its
        #table look prettier, not really needed
        for var in factor.variables:
            if var != query:
                factor = factor.marginalization(var)

        #normalize factor in case probability values add up to more than 1
        factor = self.normalization(factor)

        return factor

    def findQueriedFactor(self, factors, query):
        #find the factor that contains the queried variable after VE is over
        #usually the desired factor is the first one, this function is just an
        #extra safety measure
        for f in factors:
            if query in f.variables:
                return f
        return factors[0]

    def eliminateVariable(self, var, factors):
        print("\n-------------------------------------------------\n")
        print('BEGIN ELIMINATION CYCLE OF VARIABLE ', var)
        print('PRIOR TO ELIMINATION THE FACTORS LOOK LIKE THIS:\n')

        for f in factors:
            print('factor vars: ',f.variables,'\nfactor probs:\n',f.probabilities)

        print('\nELIMINATION:\n')

        #factors after elimination of current variable
        outputFactors = []
        #queue of factors containing current variable on which we can operate
        factorQueue = []

        #find factors on which we can operate
        for f in factors:
            if var in f.variables:
                #if a factor has the current target variable, add it to queue
                factorQueue.append(f)
            else:
                #if a factor does not contain current target variable, just let it
                #be returned later as is
                outputFactors.append(f)

        #if the factor queue is empty i.e. we don't have factors which we can operate on
        #just return the factors as they are
        if (len(factorQueue)<1):
            print('END OF ELIMINATION CYCLE OF VARIABLE ', var)
            print("\n-------------------------------------------------\n")
            return outputFactors

        #assign a factor that we'll be using for products
        productFactor = factorQueue[0]

        #make the products of the factors
        for i in range(1,len(factorQueue)):
            try:
                #this should always work in principle, as we already made sure the factors
                #have a common variable (the factor queue), this try except is a safety measure
                productFactor = productFactor.product(factors[i])
            except Exception as e:
                print(e)
        #marginalize the product of all the factors with common variables and add them to the
        #output list of factors
        outputFactors.append(productFactor.marginalization(var))

        print('END OF ELIMINATION CYCLE OF VARIABLE ', var)
        print("\n-------------------------------------------------\n")

        return outputFactors

    def createFactors(self, prob):
        factors = []
        #for each key (node) in the bayesnetwork dictionary
        #create a factor representing that Node
        #add the keys of the probability table to a variables list
        #end result: variables = [var1, var2, var3] and exclude 'prob' key
        #add the probability table to the factor as is
        for k in prob.keys():
            factors.append(factor.Factor([key for key in prob.get(k).keys() if key != 'prob'],
                          prob.get(k).values))
        print('factors that were created:')
        for f in factors:
            print('factor variables: ',f.variables)
            print('factor probability table:\n',f.probabilities)

        return factors

    def PreProcessing(self, prob, observed):
        print('PRE-PROCESSING. REDUCTION OF OBSERVED VARIABLES. ')
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