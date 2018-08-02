# taken (and adapted) from: https://blog.piekniewski.info/2018/07/14/autopsy-dl-paper/

import scipy.signal as sp
import numpy as np
# Fix some image dimensions
I_width = 100
I_height = 70
# Generate input image
A=np.zeros((I_height,I_width))
# Generate random test position
pos_x = np.random.randint(0, I_width-1)
pos_y = np.random.randint(0, I_height-1)
# Put a pixel in a random test position
A[pos_y, pos_x]=1
# Create what will be the coordinate features
X=np.zeros_like(A)
Y=np.zeros_like(A)
# Fill the X-coordinate value
for x in range(I_width):
   X[:,x] = x
# Fill the Y-coordinate value
for y in range(I_height):
   Y[y,:] = y
# Define the convolutional operators
op1 = np.array([[0, 0, 0],
                [0, -1, 0],
                [0, 0, 0]])
opx = np.array([[0, 0, 0],
                [0, I_width, 0],
                [0, 0, 0]])
opy = np.array([[0, 0, 0],
                [0, I_height, 0],
                [0, 0, 0]])
# Convolve to get the first feature map DY
CA0 = sp.convolve2d(A, opy, mode='same')
CY0 = sp.convolve2d(Y, op1, mode='same')
DY=CA0+CY0
# Convolve to get the second feature map DX
CA1 = sp.convolve2d(A, opx, mode='same')
CX0 = sp.convolve2d(X, op1, mode='same')
DX=CA1+CX0
# Apply half rectifying nonlinearity
DX[np.where(DX<0)]=0
DY[np.where(DY<0)]=0
# Subtract from a constant (extra layer with a bias unit)
result_y=I_height-DY.sum()
result_x=I_width-DX.sum()
# Check the result
assert(pos_x == int(result_x))
assert(pos_y == int(result_y))
print(result_x)
print(result_y)
