
# coding: utf-8
# Code taken from solutions to a class assignment

# In[1]:


import numpy as np


# In[2]:


TD = np.array(
    [[2, 3, 0, 3, 7],
     [0, 5, 5, 0, 3],
     [5, 0, 7, 3, 3],
     [3, 1, 0, 9, 9],
     [0, 0, 7, 1, 3],
     [6, 9, 4, 6, 0]]
)

L = np.array([5, 2, 3, 6, 4, 3])


# $P(T,D)$ each position of the matrix, $P(T, D)_{i,j}$, corresponds to the joint
# probability of term $t_i$ and document $d_j$, $P(t_i, d_j)$)

# In[3]:


P_TandD = (TD/TD.sum(axis=0)).dot(1/TD.shape[1])
print(P_TandD)


# $P(T|D)$

# In[4]:


P_TgivenD = (TD/TD.sum(axis=0))
print(P_TgivenD)


# $P(T)$

# In[5]:


P_T = P_TandD.sum(axis=1).reshape((6, 1))
print(P_T)


# $P(D)$

# In[6]:


P_D = np.ones(TD.shape[1]).dot(1/TD.shape[1])
print(P_D)


# $P(D|T)$

# In[7]:


P_DgivenT = P_TandD/(P_T)
print(P_DgivenT)
print(P_DgivenT.sum(axis=1))


# $E[l]$

# In[8]:


EL = L.dot(P_TandD).sum()
print(EL)


# $Var[l] = E[l^2] - (E[l])^2$

# In[9]:


VarL = (L**2).dot(P_TandD).sum() - EL**2
print(VarL)
