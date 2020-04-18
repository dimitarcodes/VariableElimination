# Bayesian Inference. Variable Elimination
This is my implementation of the Variable Elimination algorithm.

## Factor
Each factor has:
  * a list of variables
  * a list of possible outcomes

### Outcome
The list of outcomes is all the combinations of the states of the variables in a factor.
As such an outcome is a list with a single state from each variable and the probability of that outcome occuring.
For example one possible outcome of a factor with 3 binary variables would look like this : `['True', 'False', 'True', '0.99']`

### Instance
An instance in my code refers to a set of outcomes, where a few particular variables are mutating and a few are stationary.
For example one possible instance of 3 binary variables `{'Burglary', 'Earthquake', 'Alarm'}` over mutating variable 'Alarm' would look like this:

```
[ 
  ['False', 'True', 'True', '0.99']
  ['False', 'True', 'False', '0.01']
]
```

## Bayesian Inference Networks
Bayesian inference networks (.bif extension) can be found at https://www.bnlearn.com/bnrepository/

This assignment called for the implementation to work with the Earthquake network from [bnlearn](https://www.bnlearn.com/bnrepository/) but it also works with networks that have non-binary variables (tested with [earthquake](https://www.bnlearn.com/bnrepository/discrete-small.html#earthquake), [alarm](https://www.bnlearn.com/bnrepository/discrete-medium.html#alarm), [asia](https://www.bnlearn.com/bnrepository/discrete-small.html#asia) and [sachs](https://www.bnlearn.com/bnrepository/discrete-small.html#sachs))
