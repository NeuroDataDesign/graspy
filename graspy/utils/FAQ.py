#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize
from sinkhorn_knopp import sinkhorn_knopp as skp
sk = skp.SinkhornKnopp()

class FAQ():
    '''
    Fast Approximate QAP Algorithm (FAQ)
    The FAQ algorithm solves the Quadratic Assignment Problem (QAP) finding an alignment of the
    vertices of two graphs which minimizes the number of induced edge disagreements
    
    Parameters
    ----------
    
    n_init : int
        Number of random initializations of the starting permutation matrix that the FAQ algorithm will undergo
        
    init_method : string
        The intial position chosen
        "barycenter" : he noninformative “flat doubly stochastic matrix,” J=1*1^T/n, i.e the barycenter of 
        the feasible region
        "rand" : some random point near J, (J+K)/2, where K is some random doubly stochastic matrix
        
    Attributes
    ----------
    
    perm_inds_ : array, size (n,1) where n is the number of vertices in the graphs fitted
        The indices of the optimal permutation found via FAQ
        
    ofv_ : float
        The objective function value of for the optimal permuation found
        
        
    ''' 
    def __init__(self, n_init, init_method, ):
        '''
        
        '''
        if n_init > 0 and type(n_init) is int:
            self.n_init = n_init
        else:
            msg = '"n_init" must be a positive integer'
            raise TypeError(msg)
        if init_method == 'rand':
            self.init_method = 'rand'
        elif init_method == "barycenter":
            self.init_method = 'barycenter'
            n_init = 1
        else: 
            msg = 'Invalid "init_method" parameter string'
            raise ValueError(msg)
    def fit(self, A, B):
        '''
        Fits the model with two assigned adjacency matrices
        
        Parameters
        ---------
        A : 2d-array, square
            A square adjacency matrix
            
        B : 2d-array, square
            A square adjacency matrix
        
        Returns
        -------
        
        self : returns an instance of self
        '''
        if A.shape[0] != B.shape[0]:
            msg = "Matrix entries must be of equal size"
            raise ValueError(msg)
        elif (all(A>=0) and all(B>=0)) == False:
            msg = "Matrix entries must be greater than or equal to zero"
            raise ValueError(msg)
        else:
        
            n = A.shape[0] #number of vertices in graphs
            At = np.transpose(A)  # A transpose
            Bt = np.transpose(B)  # B transpose
            ofv_ = math.inf 
            perm_inds_ = np.zeros(n)

            for i in range(self.n_init):

                #setting initialization matrix
                if self.init_method == 'rand': 
                    #P = self.get_Pinit_rand(n)
                    sk = skp.SinkhornKnopp() 
                    K = np.random.rand(n,n) #generate a nxn matrix where each entry is a random integer [0,1]
                    for i in range(10): #perform 10 iterations of Sinkhorn balancing
                        K = sk.fit(K)
                    J = np.ones((n,n))/float(n) # initialize J, a doubly stochastic barycenter
                    P = (K+J)/2
                elif self.init_method == 'barycenter':
                    P = np.ones((n,n))/float(n)

                #OPTIMIZATION WHILE LOOP BEGINS
                for i in range(30):

                    delfp = A@P@Bt+At@P@B  # computing the gradient of f(P) = -tr(APB^tP^t)
                    rows, cols = linear_sum_assignment(-delfp) # run hungarian algorithm on gradient(f(P))
                    Q = np.zeros((n,n))  
                    Q[rows,cols] = 1   # initialize search direction matrix Q

                    def f(x):  #computing the original optimization function
                        return np.trace(At@(x*P+(1-x)*Q)@B@np.transpose(x*P+(1-x)*Q))

                    alpha = minimize_scalar(f, bounds=(0,1), method='bounded').x #computing the step size
                    P = alpha*P + (1-alpha)*Q  # Update P
                #end of FW optimization loop

                row, perm_inds_new = linear_sum_assignment(-P) #Project onto the set of permutation matrices
                perm_mat_new = np.zeros((n,n)) #initiate a nxn matrix of zeros
                perm_mat_new[row,perm_inds_new] = 1 # set indices of permutation to 1
                ofv_new = np.trace(np.transpose(A)@perm_mat_new@B@np.transpose(perm_mat_new)) #computing objective function value

                if ofv_new < ofv_: #minimizing
                    ofv_ = ofv_new
                    perm_inds_ = perm_inds_new

            self.perm_inds_ = perm_inds_
            self.ofv_ = ofv_
            return self

