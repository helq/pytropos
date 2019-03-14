
# coding: utf-8

# Code taken from personal repository

# # Answers to point 2 - Assignment 1 - ML #

# In[1]:


import numpy as np


# In[2]:


TD = np.array([
    [2, 3, 0, 3, 7],
    [0, 5, 5, 0, 3],
    [5, 0, 7, 3, 3],
    [3, 1, 0, 9, 9],
    [0, 0, 7, 1, 3],
    [6, 9, 4, 6, 0]
])

L = np.array([
    [5],
    [2],
    [3],
    [6],
    [4],
    [3]
])


# In[3]:


n, m = TD.shape
print(n, m)


# (a). $$P(T=j,D=i) = \frac{TD_{i,j}}{\text{total words on all documents}}$$

# In[4]:


total_words = TD.dot(np.ones((m, 1))).T.dot(np.ones((n, 1)))
PTD = TD/total_words

print(PTD)


# (b). $$P(T=j|D=i) = \frac{TD_{i,j}}{\text{total words on document } D_j}$$

# In[5]:


total_words_docs = TD.T.dot(np.ones((n, 1))).T
PTcondD = TD / total_words_docs

print(PTcondD)


# (c). $$P(D=i|T=j) = \frac{TD_{i,j}}{\text{total words } T_i \text{ in all documents}}$$

# In[6]:


total_words_each_word = TD.dot(np.ones((m, 1)))
PDcondT = TD / total_words_each_word

print(PDcondT)


# (d). $$P(D=i) = \frac{ \text{all words in a document } D_i }{ \text{total words in all documents} }$$

# In[7]:


PD = total_words_docs / total_words_docs.dot(np.ones((m, 1)))
#print( total_words_docs.shape )
#print( np.ones((m,1)).shape )
print(PD)


# or alternatively:
# $$P(D=i) = \frac{ P((T=0 \lor T=1 \lor T=2 \lor T=3 \lor T=4 \lor T=5), D=i) }{ P(T=0 \lor T=1 \lor T=2 \lor T=3 \lor T=4 \lor T=5 | D=i) }
# = \frac{ P(\bigvee_j T=j, D=i) }{ P(\bigvee_j T=j | D=i) }
# $$
#
# $$P(D=i) = \frac{ \sum_j{P(T=j, D=i)} }{ \sum_j{P(T=j | D=i)} } = \frac{ \sum_j{P(T=j, D=i)} }{ 1 } = \sum_j{P(T=j, D=i)}$$

# In[8]:


#sum_PTcondD_onD = PTcondD.T.dot( np.ones((n,1)) )
sum_PTD_onD = PTD.T.dot(np.ones((n, 1)))
#PD_ = (sum_PTD_onD / sum_PTcondD_onD).T
PD_ = sum_PTD_onD.T
print(PD_)


# (e). $$P(T=j) = \frac{ \text{total words } T_j \text{ in all documents} }{ \text{total words in all documents} }$$

# In[9]:


PT = total_words_each_word / total_words_each_word.T.dot(np.ones((n, 1)))
print(PT)


# or alternatively:
# $$P(T=j)
# = \frac{ P(\bigvee_i D=i, T=j) }{ P(\bigvee_i D=i | T=j) }
# = \frac{ \sum_i{P(D=i, T=j)} }{ \sum_i{P(D=i|T=j)} } = \frac{ \sum_i{P(D=i, T=j)} }{ 1 } = \sum_j{P(D=i,T=j )}$$

# In[10]:


PT_ = PTD.dot(np.ones((m, 1)))
print(PT_)


# (f). $$E[l] = \sum_{i \in \{1..m\}}{ L_i P(l=i) }$$
#
# where
#
# $$P(l=i) = \frac{ L_i }{ \sum_{i \in \{1..m\}}{L_i} }$$

# In[11]:


def E(X, PX):
    return PX.T.dot(X)


PL = L / L.T.dot(np.ones((L.shape[0], 1)))
El = E(L, PL)
print("PL:")
print(PL, end="\n\n")
print("El:")
print(El, end="\n\n")


# (g). $$Var(l) = E\left[\left(l-E[l]\right)^2\right] = \sum_{i \in \{1..m\}}{ (L_i-E[l])^2 P(l=i) }$$
# or
# $$Var(l) = E\left[l^2\right] - E\left[l\right]^2 = \left(\sum_{i \in \{1..m\}}{ L_i^2 P(l=i) }\right) - E[l]^2$$

# In[12]:


Var_l = E((L - El)**2, PL)
print(Var_l)

# or

Var_l_ = E(L**2, PL) - El**2

print(Var_l_)


# In[ ]:
