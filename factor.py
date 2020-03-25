"""
@Author Dimitar 'mechachki' Dimitrov s1018291
@Author Carla Schindler s1017233

important:
the factors work with non-binary variables
throughout the factors I use the term instance, in the context of our solution I use instance to refer to
set of outcomes that have a few variables with the same value throughout the instance and a few which are mutating

Reduction function in Factor does not work as intended, instead we use a function in variable_elim.py to reduce observed
variables, we believe this is justified because this way we can utilize the dictionary in which the probability
distribution come packaged which is supposed to be faster as opposed to our function that iterates over each factor
removing unwanted outcomes.
For this reason we have decided to not fix reduction in Factor and instead reduce before we even create the factors,
in variable_elim.py

"""

import numpy as np
import copy

class Factor():

    def __init__(self, variables, probabilities):
        self.variables = variables
        self.probabilities = probabilities

    """
    reduction over observed variable
    """
    def reduction(self, observedName, observedValue):
        print('TRIGGERED: REDUCTION')
        print('Reducing variable ', observedName, ', with observed value ',
              observedValue, '\nFrom Factor with variables: ', self.variables,
              'and probability table\n',self.probabilities)
        try:
            probs = copy.deepcopy(self.probabilities)
            vars = copy.deepcopy(self.variables)

            #locate target variable's index
            indexObserved = vars.index(observedName)
            print('index of observed variable: ', indexObserved)
            #delete from list of variables
            if(len(vars)>1):
                vars.remove(observedName)
            #queue for deletion
            qReduction=[]

            #go through each outcome in probability table
            for outcome in range (0, len(probs)):
                #if the value of variable at index of target variable is different than observed value
                #a.k.a. if the observed variable's value is different from observed value
                if probs[outcome][indexObserved] != observedValue:
                    #queue this outcome for deletion
                    qReduction.append(outcome)
            #delete all outcomes inconsistent with what we've observed
            probs = np.delete(probs, qReduction, 0)
            #create new table
            newProbs = []
            if (len(vars) > 1):
                for outcome in probs:
                    #go through each outcome
                    newOutcome = []
                    #create new outcome which keeps only unobserved variables
                    for var in range(0, len(outcome)):
                        if var!= indexObserved:
                            newOutcome.append(outcome[var])
                    #append new outcome to table of new outcomes
                    newProbs.append(newOutcome)
                newProbs = np.asarray(newProbs)
            else:
                newProbs = probs
            print('SUCCESSFUL REDUCTION, result:\nFactor with variables: ',
                  vars, '\nwith probability table table:\n', newProbs)
            return Factor(vars,newProbs)
        except:
            print('REDUCTION FAILED, observed variable does not concern this factor')
            return self
        # if the observed variable is not in this factor just return factor as is

    """
    compute product of two factors
    """
    def product(self, other):

        print('TRIGGERED PRODUCT\n','product of factors: ', self.variables,' and ', other.variables)

        if (self.variables == other.variables):
            raise Exception('product of itself')

        #find common variables of two factors
        common = []
        for var in self.variables:
            if var in other.variables:
                common.append(var)

        #if there is no common variables, raise exception
        if len(common)<1:
            raise Exception('no common variables')

        #create deep copies of the variables and probability tables
        # of the two factors, because I'm Paranoid
        ffv = copy.deepcopy(self.variables)
        ffp = copy.deepcopy(self.probabilities)
        sfv = copy.deepcopy(other.variables)
        sfp = copy.deepcopy(other.probabilities)

        #find and store the indices of the common variables in first factor
        indexFFCommon = []
        for c in common:
            indexFFCommon.append(ffv.index(c))

        # find and store the indices of the common variables in second factor
        indexSFCommon = []
        for c in common:
            indexSFCommon.append(sfv.index(c))

        #prepare variables to hold arrays of instances (a 3d array holding 2d arrays of outcomes (1d arrays))
        # in this code I refer to an instance as a set of outcomes who have one or more locked variables which I want
        # to stay the same throughout the set, with the rest of the variables mutating throughout the set.
        FFinstances = []
        SFinstances = []

        for outcome in ffp:
            #get a list of instances with the same value for the common variables in first factor
            FFinstances.append(self.extractUncommon( ffp, outcome, indexFFCommon))
        # remove duplicate instances
        FFinstances = self.clear3Ddupes(FFinstances)

        for outcome in sfp:
            # get a list of instances with the same value for the common variables in 2nd factor
            SFinstances.append(self.extractUncommon( sfp, outcome, indexSFCommon))
        # remove duplicate instances
        SFinstances = self.clear3Ddupes(SFinstances)


        ################################################################
        ################################################################
        ########                                                ########
        ########                TIME FOR THE FUN PART:          ########
        ########            ACTUALLY MULTIPLYING THEM :)        ########
        ########                                                ########
        ################################################################
        ################################################################

        #Create a list of the new variables
        newFactorVars = []
        #first come common variables
        for c in common:
            newFactorVars.append(c)
        # then come uncommon variables of first factor
        for c in ffv:
            if c not in common:
                newFactorVars.append(c)
        # then come uncommon variables of second factor
        for c in sfv:
            if c not in common:
                newFactorVars.append(c)

        #Create a variable that will hold the new probability table
        newFactorProbs = []
        for instance in FFinstances:
            #go through each instance of first factor
            for outcome in instance:
                #go through each outcome in that particular instance of first factor
                for instance2 in SFinstances:
                    #go through each instance in second factor
                    for outcome2 in instance2:
                        #go through each outcome in that particular instance of second factor
                        if np.array_equal([val for val in outcome[indexFFCommon]], [val for val in outcome2[indexSFCommon]]):
                            #if the two outcomes have same values at the indices of common variables
                            newOutcome = self.multiply(outcome, outcome2, indexFFCommon, indexSFCommon)
                            #multiply the two outcomes
                            newFactorProbs.append(newOutcome)
                            #append the new, product outcome to the new table of outcomes

        newFactorProbs = np.asarray(newFactorProbs)

        #return a new Factor, where the outcomes are products of the outcomes of input factors

        print('result of product:\nvariables:', newFactorVars,'\nprobability table:\n', np.asarray(newFactorProbs))

        return Factor(newFactorVars, np.asarray(newFactorProbs))

    """
    multiplication of two outcomes.
    it takes 
    outcome 1, example:= [True, True, False, 0.9]
    outcome 2, example:= [True, False, True, 0.5]
    list of indices where common variables stand in factor 1, example:= [1,2]
    list of indices where common variables stand in factor 1, example:= [0,1]
    :returns product of two outcomes, example:= [True, False, True, True, 0.45]
    
    IT IS EXTREMELY IMPORTANT THAT THE ORDER OF VARIABLES IN RESULT IS 
    [ COMMON VARIABLE 1, COMMON VARIABLE 2, ETC. , UNCOMMON VARIABLE FACTOR1 1, ETC. , UNCOMMON VARIABLE FACTOR 2, ETC.]
    IT HAS TO STAY CONSISTENT WITH THE ORDERING FROM LINES 133-145 OR THE RESULT IS SIMPLY. NOT. CORRECT.
    """
    def multiply(self, outcome1, outcome2, indexCommon1, indexCommon2):
        outcome = []
        #again first come the common variables
        for i in indexCommon1:
            outcome.append(outcome1[i])
        #then come the uncommon variables of outcome 1, except the probability value
        for i in range(0, len(outcome1)-1):
            if i not in indexCommon1:
                outcome.append(outcome1[i])
        #then come the uncommon variables of outcome 2, except the probability value
        for i in range(0, len(outcome2)-1):
            if i not in indexCommon2:
                outcome.append(outcome2[i])
        #then we compute probability value, which is simply product of prob value of outcome 1 and outcome 2
        outcome.append(float(outcome1[-1])*float(outcome2[-1]))
        #return new outcome, product of input outcomes
        return outcome


    """
    takes a 3-dimensional array and treats every 2-dimensional array inside it
    as an item, clears duplicate items.
    result: a (3-dimensional) array with unique 2-dimensional arrays inside it
    """
    def clear3Ddupes(self, list3d):
        q = []
        for i in range(0,len(list3d)):
            #iterate through the 3d array, checking every 2d array
            if i not in q:
                #if the current 2d array hasn't been marked as a duplicate
                for j in range(0,len(list3d)):
                    #iterate through the list
                    if i!=j:
                        #avoid comparing 2nd iteration's element to itself from first iteration
                        if np.array_equal(list3d[i],list3d[j]):
                            #if the two arrays are identical
                            q.append(j)
                            #add the index of the 2nd (duplicate) array to a list
        list3d=np.delete(list3d,q,axis=0)
        #use the previously curated list of duplicates' indices to remove them from the original 3d array
        return list3d

    """
    given a 2d array of outcomes (probabilities) lock particular items and find the iteration of the unlocked items
    probs: the full probabilities/outcomes table
    sample: sample showing us the desired state of locked variables (variables whose value we want to keep constant)
    indices: indices of the locked variables. variables at those indices will stay the same throughout the resulting 
    array. 
    it is preferable that the sample is one of the outcomes in probs
    example:
    probs = [
             [True, True, True, 0.95]
             [True, True, False, 0.05]
             [True, False, True, 0.85]
             [True, False, False, 0.15]
             [False, True, True, 0.75]
             [False, True, False, 0.25]
             [False, False, True, 0.65]
             [False, False, False, 0.35]
            ]
    sample = [True, False, True, 0.85] 
    indices = [0,1] 
    this means we want the result to be ONLY outcomes where the value at index 0 is the same as 
    value at index 0 of the sample (True) and value at index 1 is the same as value at index one in the sample (False).
    The result from running the function with these parameters is a 2d array:
    collect = [
                [True, False, True, 0.85]
                [True, False, False, 0.15]
              ]
    alternative explanation: from a 2d list of 1d outcomes, extract outcomes where only indices NOT mentioned in the 
    indices parameter are different.
    """
    def extractUncommon(self, probs, sample, indices):
        collect = copy.deepcopy(probs)
        removeQ = []
        #make a deepcopy of the probabilities table so that we can change it
        for i in indices:
            #for every index of a common variable
            for outcome in range(0,len(collect)):
                #for every outcome in the probability table
                if collect[outcome][i] != sample[i]:
                    removeQ.append(outcome)
                    #queue the index of the undesired element for deletion
        #delete all unwanted indices (outcomes)
        collect = np.delete(collect, removeQ, axis=0)
        return collect




    """
    marginalization of 2 factors
    """
    def marginalization(self, varName):
        print('Marginalization of factor:', self.variables, " over ", varName)
        # attempt to do marginalization, might fail if the variable
        # over which we're trying to marginalize is not in this factor
        try:
            # get the index of the queried variable for marginalization in this factor's outcomes table
            indexVar = self.variables.index(varName)
            # get the indices of the non-marginalized variables
            indexRest = [i for i in range(0, len(self.variables))]
            indexRest.remove(indexVar)

            #raise an exception if the only variable in the factor is the queried one
            if(len(indexRest)<1):
                raise Exception('no variables besides the target of marginalization')
            # prepare a variable that will hold the resulting table of instances. Each instance has multiple outcomes.
            # in this code I refer to an instance a set of outcomes who have one or more locked variables which I want
            # to stay the same throughout the set, with the rest of the variables mutating throughout the set.
            newProbs = []

            #where the magic happens: take each outcome in the provided outcomes table
            for outcome in self.probabilities:
                # perform extraction of the uncommon variables, like a reverse product,
                # where every variable is a constant, except the variable queried for marginalization
                # and append the result to the new table of outcomes
                newProbs.append(self.extractUncommon(self.probabilities, outcome, indexRest))
            # because every time a new outcome is processed it's complementary
            # outcomes are added we need to remove the duplicates.
            # There will be as many duplicates as there are variations of a variable
            # (if a variable is binary there will be one duplicate, if it's ternary - 2 extra duplicates
            newProbs = self.clear3Ddupes(newProbs)

            # now we need to compute the new probabilities (the last item in each 1d array)
            # prepare a new variable that will hold the final outcomes table
            marginalProb = []

            #go through each instance in newProbs
            for instance in newProbs:
                #prepare a sum variable
                sum = 0
                #prepare an array that will hold the marginalized outcome
                newVals = []
                # collect all variables' values, except the target variable that we need to marginalize over
                # in this set of outcomes (instance as I call it earlier) only the target variable varies
                # because of this we can just run it on the first outcome (instance[0] in the instance
                # we need to manually sum/compute the actual probability that this outcome will have later, which
                # is why we only go from 0 to len(instance) -1 (the last index of outcome is a probability value)
                for i in range(0,len(instance[0])-1):
                    #if it's not the target variable
                    if i != indexVar:
                        #append it to the new outcome array
                        newVals.append(instance[0][i])
                #sum out the probability values in this instance)
                for outcome in instance:
                    sum = sum + float(outcome[-1])
                #add the probability sum to the new outcome
                newVals.append(sum)
                #add the newly created marginalized outcome to the new table of marginalized outcomes
                marginalProb.append(newVals)

            #collect the variables, except the one we marginalized over
            newVars = []
            for var in self.variables:
                #go through all current variables
                if var != varName:
                    #if the current variable is different from the marginalization target
                    newVars.append(var)
                    #add it to the new variables

            #return the new, marginalized factor
            marginalProb = np.asarray(marginalProb)
            print('RESULT FROM MARGINALIZATION\nvariables:\n',newVars,'\nprobability table:\n',marginalProb)
            return Factor(newVars, marginalProb)
        except Exception as e:
            print(e)
            print('Marginalization failed, factor does not contain variable or target is only variable', varName)
        # if the variable is not present in this factor, in which way just return the factor as is
        return self