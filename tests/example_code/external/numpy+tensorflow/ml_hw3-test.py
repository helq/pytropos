# Code taken from personal code, not reseleased

import tensorflow as tf
from models.tensorflow_models.research.slim.nets import mobilenet_v1 as mobilenet
from tensorflow.contrib import slim
import os
from loaddataset import load_set
from tensorflow.python.ops import variables

test_imgs_, test_labels_ = load_set('testing')
valid_imgs   = test_imgs_  [:11700]
valid_labels = test_labels_[:11700]

with tf.Graph().as_default():
    processed_images_train = tf.constant(valid_imgs[:10].reshape( (-1, 96, 96, 2) ))
    processed_images_test  = tf.constant(valid_imgs[10:20].reshape( (-1, 96, 96, 2) ))
    #
    # Create the model, use the default arg scope to configure the batch norm parameters.
    with tf.variable_scope('ConvNetMobile', reuse=False):
        with slim.arg_scope(mobilenet.mobilenet_v1_arg_scope()):
            logits_train, _ = mobilenet.mobilenet_v1(processed_images_train, num_classes=5, depth_multiplier=0.50, is_training=True, reuse=False)
    with tf.variable_scope('ConvNetMobile', reuse=True):
        with slim.arg_scope(mobilenet.mobilenet_v1_arg_scope()):
            logits_test, _  = mobilenet.mobilenet_v1(processed_images_test,  num_classes=5, depth_multiplier=0.50, is_training=False)
    probabilities = tf.nn.softmax(logits_test)
    #
    #init_fn = slim.assign_from_checkpoint_fn(
    #    os.path.join('models-results/mobilenet', 'model.ckpt-1001'),
    #    slim.get_model_variables('ConvNetMobile'))
    #
    print( slim.get_model_variables('ConvNetMobile') )
    one_hot_labels = slim.one_hot_encoding(valid_labels[:10], 5)
    slim.losses.softmax_cross_entropy(logits_train, one_hot_labels)
    total_loss = slim.losses.get_total_loss()
    optimizer = tf.train.AdamOptimizer(learning_rate=0.01)
    train_op = slim.learning.create_train_op(total_loss, optimizer)
    #
    init_op = variables.global_variables_initializer()
    with tf.Session() as sess:
        #init_fn(sess)
        sess.run([init_op])
        probabilities__ = []
        logits_test__ = []
        processed_images_test__ = []
        for i in range(400):
            sess.run([train_op])
            probabilities_, logits_test_, processed_images_test_ = sess.run([probabilities, logits_test, processed_images_test])
            #
            if i%10 == 0:
                probabilities__.append(probabilities_)
                logits_test__.append(logits_test_)
                processed_images_test__.append(processed_images_test_)

        probabilities = probabilities[0, 0:]
        sorted_inds = [i[0] for i in sorted(enumerate(-probabilities), key=lambda x:x[1])]

    plt.figure()
    plt.imshow(np_image.astype(np.uint8))
    plt.axis('off')
    plt.show()

    names = imagenet.create_readable_names_for_imagenet_labels()
    for i in range(5):
        index = sorted_inds[i]
        # Shift the index of a class name by one.
        print('Probability %0.2f%% => [%s]' % (probabilities[index] * 100, names[index+1]))
