"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

@Author Dimitar 'mechachki' Dimitrov s1018291
@Author Carla Schindler s1017233

Entry point for the creation of the variable elimination algorithm in Python 3.
Code to read in Bayesian Networks has been provided. We assume you have installed the pandas package.

"""
from read_bayesnet import BayesNet
from variable_elim import VariableElimination

if __name__ == '__main__':
    # The class BayesNet represents a Bayesian network from a .bif file in several variables
    net = BayesNet('earthquake.bif') # Format and other networks can be found on http://www.bnlearn.com/bnrepository/
    
    # These are the variables read from the network that should be used for variable elimination
    # print("Nodes:")
    # print(net.nodes)
    # print("Values:")
    # print(net.values)
    # print("Parents:")
    # print(net.parents)
    # print("Probabilities:")
    # print(net.probabilities)

    # Make your variable elimination code in the seperate file: 'variable_elim'. 
    # You use this file as follows:
    ve = VariableElimination(net)

    # Set the node to be queried as follows:
    query = 'Alarm'

    # The evidence is represented in the following way (can also be empty when there is no evidence): 
    evidence = {'Burglary' : 'True' }  # {, 'Earthquake' : 'True'}

    # Determine your elimination ordering before you call the run function. The elimination ordering   
    # is either specified by a list or a heuristic function that determines the elimination ordering
    # given the network. Experimentation with different heuristics will earn bonus points. The elimination
    # ordering can for example be set as follows:

    elim_order = net.nodes
    elim_order.remove(query)
    for k in evidence.keys():
        elim_order.remove(k)
    print('\nFor queried variable ', query, '\nThe elimination order is:', elim_order)

    #Call the variable elimination function for the queried node given the evidence and the elimination ordering as follows:
    ve.run(query, evidence, elim_order)
