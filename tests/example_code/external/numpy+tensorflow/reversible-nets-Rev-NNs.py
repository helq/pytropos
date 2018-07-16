# coding: utf-8
# Code taken from
# TODO(helq): add reference

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')

import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import tensorflow as tf


# In[3]:


tf.logging.set_verbosity(tf.logging.INFO)


# In[4]:


def cnn_model_fn(features, labels, mode):
  """Model function for CNN."""
  # Input Layer
  # Reshape X to 4-D tensor: [batch_size, width, height, channels]
  # MNIST images are 28x28 pixels, and have one color channel
  input_layer = tf.reshape(features["x"], [-1, 28, 28, 1])

  # Convolutional Layer #1
  # Computes 32 features using a 5x5 filter with ReLU activation.
  # Padding is added to preserve width and height.
  # Input Tensor Shape: [batch_size, 28, 28, 1]
  # Output Tensor Shape: [batch_size, 28, 28, 32]
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.sigmoid)

  # Pooling Layer #1
  # First max pooling layer with a 2x2 filter and stride of 2
  # Input Tensor Shape: [batch_size, 28, 28, 32]
  # Output Tensor Shape: [batch_size, 14, 14, 32]
  # pool1 = tf.layers.average_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
  conv1b = tf.layers.conv2d(
      inputs=conv1,
      filters=32,
      kernel_size=[2, 2],
      strides=2,
      padding="valid",
      activation=None)

  # Convolutional Layer #2
  # Computes 64 features using a 5x5 filter.
  # Padding is added to preserve width and height.
  # Input Tensor Shape: [batch_size, 14, 14, 32]
  # Output Tensor Shape: [batch_size, 14, 14, 64]
  conv2 = tf.layers.conv2d(
      inputs=conv1b,
      filters=64,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.sigmoid)

  # Pooling Layer #2
  # Second max pooling layer with a 2x2 filter and stride of 2
  # Input Tensor Shape: [batch_size, 14, 14, 64]
  # Output Tensor Shape: [batch_size, 7, 7, 64]
  # pool2 = tf.layers.average_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
  conv2b = tf.layers.conv2d(
      inputs=conv2,
      filters=64,
      kernel_size=[2, 2],
      strides=2,
      padding="valid",
      activation=None)

  # Flatten tensor into a batch of vectors
  # Input Tensor Shape: [batch_size, 7, 7, 64]
  # Output Tensor Shape: [batch_size, 7 * 7 * 64]
  pool2_flat = tf.reshape(conv2b, [-1, 7 * 7 * 64])

  # Dense Layer
  # Densely connected layer with 1024 neurons
  # Input Tensor Shape: [batch_size, 7 * 7 * 64]
  # Output Tensor Shape: [batch_size, 1024]
  dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)

  # Add dropout operation; 0.6 probability that element will be kept
  dropout = tf.layers.dropout(
      inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

  # Logits layer
  # Input Tensor Shape: [batch_size, 1024]
  # Output Tensor Shape: [batch_size, 10]
  logits = tf.layers.dense(inputs=dropout, units=10)

  predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor"),
      "first_conv2": conv1,
      "first_conv2_pool": conv1b,
      "second_conv2": conv2,
      "second_conv2_pool": conv2b,
  }
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

  # Calculate Loss (for both TRAIN and EVAL modes)
  loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

  # Configure the Training Op (for TRAIN mode)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

  # Add evaluation metrics (for EVAL mode)
  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


# In[5]:


mnist = tf.contrib.learn.datasets.load_dataset("mnist")
train_data = mnist.train.images  # Returns np.array
train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
eval_data = mnist.test.images  # Returns np.array
eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)


# In[6]:


mnist_classifier = tf.estimator.Estimator(
    model_fn=cnn_model_fn, model_dir="./mnist_convnet_model")


# In[7]:


images = [0, 1, 2, 3, 4]


# In[8]:


from random import randint
import random

def plot_image(X, images=None, seed=3241, kwargs_for_imshow={}, n=None, imshape=(28,28) ):
    random.seed( seed )
    if n is None:
        n = X.shape[0]

    f, axes = plt.subplots(1, 5, sharey=True, figsize=(15,3))
    if images is None:
        for i in range(5):
            axes[i].imshow( X[ randint(0,n-1) ].reshape( imshape ), **kwargs_for_imshow )
    else:
        for i in range(5):
            axes[i].imshow( X[ images[i] ].reshape( imshape ), **kwargs_for_imshow )

    plt.show()

plot_image( eval_data, images=images )


# In[9]:


eval_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": eval_data[images]},
      #y=eval_labels,
      num_epochs=1,
      shuffle=False)


# In[10]:


preds = list( mnist_classifier.predict( input_fn=eval_input_fn ) )
[p['classes'] for p in preds]


# In[11]:


for i in range(5):
    plot_image( [p["first_conv2"][:,:,i] for p in preds], images=images, n=5, imshape=(28,28) )


# In[12]:


for i in range(5):
    plot_image( [p["first_conv2_pool"][:,:,i] for p in preds], images=images, n=5, imshape=(14,14) )


# In[13]:


preds[0]["second_conv2_pool"].shape


# In[14]:


for i in range(5):
    plot_image( [p["second_conv2_pool"][:,:,i] for p in preds], images=images, n=5, imshape=(7,7) )


# ---

# In[15]:


mnist_classifier.get_variable_names()


# In[16]:


print( mnist_classifier.get_variable_value( 'conv2d/kernel' ).shape )
print( mnist_classifier.get_variable_value( 'conv2d/bias' ).shape )


# In[17]:


knum = 3


# In[18]:


conv1kern3 = mnist_classifier.get_variable_value( 'conv2d/kernel' )[:,:,0,knum]
print(conv1kern3)
conv1bias3 = mnist_classifier.get_variable_value( 'conv2d/bias' )[knum]
print(conv1bias3)


# In[19]:


def relu(x):
    return np.maximum(0, x)
def sigmoid(x):
    return 1/(1+np.exp(-x))


# In[20]:


padded_image = np.zeros( (5, 28+4,28+4), dtype=eval_data.dtype )
padded_image[:,2:-2,2:-2] = eval_data[0:5].reshape( (5,28,28) )

new_image = np.zeros( (5,28,28), dtype=eval_data.dtype )
for k in range(5):
    for i in range(28):
        for j in range(28):
            new_image[k,i,j] = padded_image[k,i:i+5,j:j+5].flatten().dot( conv1kern3.flatten() )
#new_image = relu( new_image )
new_image = sigmoid( new_image + conv1bias3 )


# In[21]:


fromtensors = [p["first_conv2"][:,:,knum] for p in preds]
plot_image( new_image, images=images, n=5, imshape=(28,28) )
plot_image( fromtensors, images=images, n=5, imshape=(28,28) )


# In[22]:


plot_image( new_image - fromtensors, images=images, n=5, imshape=(28,28) )


# In[23]:


# checking for not so big differences between the calculated values by tensorflow and our own calculations
np.all( abs(new_image - fromtensors) <= 1e-6 )


# In[24]:


def siginv(x):
    return np.log( x / (1-x) )

def siginv2(x):
    return -np.log( (1-x)/x )


# In[25]:


print( siginv(sigmoid(np.array(range(-10,10)))) )
print( siginv2(sigmoid(np.array(range(-10,10)))) )


# In[28]:


"""
def construct_matrix_kernel2(kernel, kershape=5, imgshape=(28,28), outshape=(28,28), internals=False):
    # matrix that produces image padded
    h1,w1 = imgshape
    h2,w2 = h1+kershape-1, h1+kershape-1
    h3,w3 = outshape
    padding_mat = np.zeros( (h2*w2, h1*w1), dtype=eval_data.dtype )
    j = w2*2+2
    padding_mat[j][0] = 1
    for i in range(1, h1*w1):
        if i%w1 == 0:
            j += kershape
        else:
            j += 1
        padding_mat[j][i] = 1

    # creating matrix that operates on already padded image
    app_ker_mat = np.zeros( (h3*w3, h2*w2), dtype=eval_data.dtype )

    for i in range(h3):
        for j in range(w3):
            for k in range(kershape):
                app_ker_mat[i*h3+j, h2*i+w2*k+j:h2*i+kershape+w2*k+j] = kernel[k,:]

    if internals:
        return np.dot( app_ker_mat, padding_mat ), app_ker_mat, padding_mat
    else:
        return np.dot( app_ker_mat, padding_mat )

kern2 = construct_matrix_kernel(conv1kern3)
"""


# In[29]:


def construct_matrix_kernel(kernel, internals=False):
    # matrix that produces image padded
    padding_mat = np.zeros( (32*32, 28*28), dtype=eval_data.dtype )
    j = 32*2+2
    padding_mat[j][0] = 1
    for i in range(1, 28*28):
        if i%28 == 0:
            j += 5
        else:
            j += 1
        padding_mat[j][i] = 1

    # creating matrix that operates on already padded image
    app_ker_mat = np.zeros( (28*28, 32*32), dtype=eval_data.dtype )

    for i in range(28):
        for j in range(28):
            for k in range(5):
                app_ker_mat[i*28+j, 32*i+32*k+j:32*i+5+32*k+j] = kernel[k,:]

    if internals:
        return np.dot( app_ker_mat, padding_mat ), app_ker_mat, padding_mat
    else:
        return np.dot( app_ker_mat, padding_mat )

kern1, part2, part1 = construct_matrix_kernel(conv1kern3, True)


# In[30]:


img_orig = eval_data[0].reshape((28,28))
img_part1 = np.dot( part1, eval_data[0] ).reshape((32,32))
img_part2 = np.dot( part2, img_part1.flatten() ).reshape((28,28))
output_conv = sigmoid(img_part2+conv1bias3)


# In[31]:


f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( img_orig )
axes[1].imshow( img_part1[2:-2,2:-2] ) # chopping borders to compare only with the original
plt.plot()

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( preds[0]["first_conv2"][:,:,knum] )
axes[1].imshow( output_conv ) # chopping borders to compare only with the original
plt.plot()

# np.all(np.abs(img_orig - img_part1[2:-2,2:-2]) == 0 )


# In[32]:


img_part2_ = np.dot( kern1, eval_data[0] ).reshape((28,28))
output_conv_ = sigmoid(img_part2_+conv1bias3)

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( preds[0]["first_conv2"][:,:,knum] )
axes[1].imshow( output_conv_ )
plt.plot()


# In[33]:


kern1inv = np.linalg.pinv( kern1 )


# In[118]:


orig_ = np.dot( kern1inv, siginv(output_conv_.flatten())-conv1bias3 )

f, axes = plt.subplots(1, 3, sharey=True, figsize=(9,3))
axes[0].imshow( img_orig )
axes[1].imshow( output_conv_ )
axes[2].imshow( orig_.reshape((28,28)) )
plt.plot()


# In[35]:


print("How similar is the original image to the one we get now? (using only a kernel output)")
print( "A difference smaller than 1e-2:", np.all( abs( img_orig.reshape(-1) - orig_ ) < 1e-2 ) )
print( "A difference smaller than 1e-5:", np.all( abs( img_orig.reshape(-1) - orig_ ) < 1e-5 ) )


# In[36]:


def createconvkern(kernels, imgshape=(28,28), limit_n = None):
    _,_,_,n = kernels.shape
    h, w = imgshape

    if limit_n is not None:
        n = limit_n

    kern_mats = np.zeros( (h*w*n, h*w) )
    print( kern_mats.shape )

    for i in range(n):
        kern_mats[i*h*w:(i+1)*h*w] = construct_matrix_kernel( kernels[:,:,0,i] )
    return kern_mats


# In[37]:


limit_m = 10
conv1kerns = createconvkern( mnist_classifier.get_variable_value( 'conv2d/kernel' ), limit_n = limit_m)
conv1biases = mnist_classifier.get_variable_value( 'conv2d/bias' ).reshape((-1,1,1))[:limit_m]


# In[38]:


def create_conv1(conv_kerns, conv_biases):
    def conv(data):
        mul = np.dot( conv_kerns, data ).reshape((-1,28,28)) + conv_biases
        return sigmoid(mul)
    return conv

conv1 = create_conv1(conv1kerns, conv1biases)


# In[78]:


def create_invconv1(conv_kerns, conv_biases):
    kinv = np.linalg.pinv( conv_kerns )
    def convinv(data):
        lineal = siginv(data) - conv_biases
        return np.dot( kinv, lineal.flatten() ).reshape((28,28))
    return convinv

conv1inv = create_invconv1(conv1kerns, conv1biases)


# In[125]:


data_orig = eval_data[0].reshape((28,28))
img_conv1 = conv1( eval_data[0] )
print( img_conv1.shape )
#img_conv1[0,0] += 0.1
data_orig_ = conv1inv(img_conv1)

img_conv1_tensorflow = preds[0]["first_conv2"][:,:,1] # from tensorflow

f, axes = plt.subplots(1, 4, sharey=True, figsize=(12,3))
axes[0].imshow( data_orig )
axes[1].imshow( img_conv1[1] )
axes[2].imshow( img_conv1_tensorflow )
axes[3].imshow( data_orig_ )
plt.plot()

#output_conv_ = sigmoid(img_part2_+conv1bias3)


# In[80]:


print("How similar is the original image to the one we get now? (using only a kernel output)")
print( "A difference smaller than 1e-5:", np.all( abs( data_orig - data_orig_ ) < 1e-5 ) )
print( "A difference smaller than 1e-12:", np.all( abs( data_orig - data_orig_ ) < 1e-12 ) )


# In[42]:


def construct_matrix_kernel2(kernel, limit_m = None):
    if limit_m is None:
        m = 32
    else:
        m = limit_m

    # no padding
    app_ker_mat = np.zeros( (14*14, 28*28*m), dtype=eval_data.dtype )

    for i in range(14):
        for j in range(14):
            for l in range(m):
                for k in range(2):
                    posinrow = 28*k + 28*28*l + 2*j + 2*28*i
                    app_ker_mat[14*i+j, posinrow:posinrow+2] = kernel[k,:,l]
    return app_ker_mat

kern0conv2 = construct_matrix_kernel2(mnist_classifier.get_variable_value( 'conv2d_1/kernel' )[:,:,:,0], limit_m)


# In[43]:


nextlayer = np.dot( kern0conv2, img_conv1.flatten() ).reshape( (14,14) )
nexbiases = mnist_classifier.get_variable_value( 'conv2d_1/bias' )[0]
#nextlayer = np.dot( app_ker_mat, preds[0]["first_conv2"].transpose((2,0,1)).flatten() ).reshape( (14,14) )

fromtensorflow = preds[0]["first_conv2_pool"][:,:,0]

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( sigmoid(nextlayer+nexbiases) )
axes[1].imshow( fromtensorflow )
#axes[2].imshow( data_orig_ )
plt.plot()


# In[44]:


def createconv2kern(kernels, imgshape=(28,28), outshape=(14,14), limit_n=None, limit_m=None):
    _,_,m,n = kernels.shape
    h, w = imgshape
    ho, wo = outshape

    if limit_n is not None:
        n = limit_n

    if limit_m is not None:
        m = limit_m

    kern_mats = np.zeros( (ho*wo*n, h*w*m) )
    print( kern_mats.shape )

    for i in range(n):
        kern_mats[i*ho*wo:(i+1)*ho*wo] = construct_matrix_kernel2( kernels[:,:,:,i], limit_m )
    return kern_mats


# In[45]:


limit_n = 10
conv2kerns = createconv2kern( mnist_classifier.get_variable_value( 'conv2d_1/kernel' ), limit_n = limit_n, limit_m = limit_m)
conv2biases = mnist_classifier.get_variable_value( 'conv2d_1/bias' ).reshape((-1,1,1))


# In[46]:


nextlayertotal = np.dot( conv2kerns, img_conv1.flatten() ).reshape( (-1,14,14) )


# In[47]:


knum = 4

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( sigmoid(nextlayertotal[knum]+conv2biases[knum]) )
axes[1].imshow( preds[0]["first_conv2_pool"][:,:,knum] )
#axes[2].imshow( data_orig_ )
plt.plot()


# In[49]:


def create_conv2(conv_kerns, conv_biases, limit_n = None, limit_m = None):
    if limit_n is not None:
        n = limit_n
    else:
        n = 32 # takes a fuck tone of memory

    if limit_m is not None:
        m = limit_m
    else:
        m = 32 # takes a fuck tone of memory

    w = 28*28*m
    h = 14*14*n
    g = w-h

    test = np.random.random((g,w))
    #test = np.zeros((g,w), dtype=eval_data.dtype)
    #for i in range(g):
    #    for j in np.random.choice(h, 90):
    #        test[i,j] = np.random.random()
    theconvkern = np.concatenate( [conv_kerns, test], axis=0 )

    def conv(data):
        yeah = np.dot( theconvkern, data ).reshape((-1,14,14))

         # result of performing operations, plus garbage and the matrix used to create the garbage
        return (yeah[:n] + conv_biases[:n], yeah[n:])
    return conv, theconvkern

conv2, conv2kernstotal = create_conv2(conv2kerns, conv2biases, limit_n = limit_n, limit_m = limit_m)


# In[51]:


kinv = np.linalg.inv( conv2kernstotal )


# In[85]:


def create_invconv2(conv_kerns, conv_biases, limit_n = None, kinv = None):
    if limit_n is not None:
        n = limit_n
    else:
        n = 32

    if kinv is None:
        kinv = np.linalg.pinv( conv_kerns )

    def convinv(data, garbage):
        data_ = np.concatenate([data - conv_biases[:n], garbage], axis=0)
        return np.dot( kinv, data_.flatten() ).reshape((-1,28,28))
    return convinv

conv2inv = create_invconv2(conv2kernstotal, conv2biases, limit_n=limit_n, kinv=kinv)


# In[56]:


resulconv2, garbage = conv2( img_conv1.flatten() )


# In[58]:


print( resulconv2.shape )
print( garbage.shape )
print( conv2kernstotal.shape )


# In[59]:


f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( resulconv2[0] )
axes[1].imshow( garbage[1] )
plt.plot()


# In[76]:


knum = 2

reversing1 = conv2inv(resulconv2, garbage)
img_conv1_tensorflow_ = preds[0]["first_conv2"][:,:,knum] # from tensorflow

f, axes = plt.subplots(1, 3, sharey=True, figsize=(9,3))
axes[0].imshow( reversing1[knum] )
axes[1].imshow( img_conv1_tensorflow_ )
axes[2].imshow( reversing1[knum] - img_conv1_tensorflow_ )
plt.plot()


# In[73]:


print("How similar is the original image to the one we get now? (using only a kernel output)")
print( "A difference smaller than 1e-5:", np.all( abs( reversing1 - img_conv1_tensorflow_ ) < 1e-5 ) )
print( "A difference smaller than 1e-12:", np.all( abs( reversing1 - img_conv1_tensorflow_ ) < 1e-12 ) )


# :S, I isn't working as perfectly as expected T_T

# In[83]:


data_orig = eval_data[0].reshape((28,28))
data_orig_2 = conv1inv(reversing1)

img_conv1_tensorflow = preds[0]["first_conv2"][:,:,1] # from tensorflow

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( data_orig )
axes[1].imshow( data_orig_2 )
plt.plot()


# Here, all the calculations for another number.

# In[147]:


image_i = 546

data_orig_b = eval_data[image_i].reshape((28,28))

img_conv1_b = conv1( eval_data[image_i] )
resulconv2_b, garbage_b = conv2( img_conv1_b.flatten() )

reversing1_b = conv2inv(resulconv2_b, garbage_b)
data_orig_2_b = conv1inv(reversing1_b)

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( data_orig_b )
axes[1].imshow( data_orig_2_b )
plt.plot()


# In[148]:


image_i = 233

data_orig_a = eval_data[image_i].reshape((28,28))

img_conv1_a = conv1( eval_data[image_i] )
resulconv2_a, garbage_a = conv2( img_conv1_a.flatten() )

reversing1_a = conv2inv(resulconv2_a, garbage_a)
data_orig_2_a = conv1inv(reversing1_a)

f, axes = plt.subplots(1, 2, sharey=True, figsize=(6,3))
axes[0].imshow( data_orig_a )
axes[1].imshow( data_orig_2_a )
plt.plot()


# In[153]:


similarity = .5
similarity2 = .02

#data_orig_2_c1 = conv1inv(  conv2inv(resulconv2_b, garbage_b )  )
data_orig_2_c2 = conv1inv(  conv2inv(resulconv2_b*(1-similarity) + resulconv2_a*similarity, garbage_b*(1-similarity) + garbage_a*similarity)  )
data_orig_2_c3 = conv1inv(  conv2inv(resulconv2_b, garbage_b*(1-similarity2) + garbage_a*similarity2)  )
data_orig_2_c4 = conv1inv(  conv2inv(resulconv2_a, garbage_a)  )

f, axes = plt.subplots(1, 4, sharey=True, figsize=(12,3))
#axes[0].imshow( data_orig_2_c1 )
axes[0].imshow( data_orig_b )
axes[1].imshow( data_orig_2_c2 )
axes[2].imshow( data_orig_2_c3 )
axes[3].imshow( data_orig_2_c4 )
plt.plot()

