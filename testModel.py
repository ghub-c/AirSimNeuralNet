# -*- coding: utf-8 -*-


from AirSimClient import MultirotorClient, ImageRequest, AirSimImageType, AirSimClientBase
import os
import tensorflow as tf
import pickle
import sys
from skimage import color
from skimage import io


#Initial height of the drone
initialZ=-2


#Image directory inside the project
IMAGEDIR = './dataset'
#TMP file with active images
TMPFILE = IMAGEDIR + '/active.png'
#Image pixels
imgpixels = 36864
#Parameters file
PARAMFILE = 'model.pkl'

# Load saved training params as ordinary NumPy
W,b = pickle.load(open(PARAMFILE, 'rb'))

def inference(x, xsize, ysize, W_vals=0, b_vals=0):
    
    '''
    Softmax inference layer implementation (Logistic regression)
    Obtained from Fundamentals of Deep Learning Book
    '''
    
    W_init = tf.constant_initializer(value=W_vals)
    b_init = tf.constant_initializer(value=b_vals)
    W = tf.get_variable('W', [xsize, ysize], initializer=W_init)
    b = tf.get_variable('b', [ysize],        initializer=b_init)
    output = tf.nn.softmax(tf.matmul(x, W) + b)
    return output


    
#Connection to the AirSim simulator
client = MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Connected")

#Move drone forward
client.moveToZ(initialZ, 3)
client.moveByVelocity(10,0,0.3,18)

with tf.Graph().as_default():

    # Placeholder for an image
    x = tf.placeholder('float', [None, imgpixels])

    # Our inference engine, intialized with weights we just loaded
    output = inference(x, imgpixels, 2, W, b)

    # TensorFlow initialization boilerplate
    sess = tf.Session()
    init_op = tf.global_variables_initializer()
    sess.run(init_op)



    #Searching for a potential collision
    while True:

        # Get RGBA camera images from the car
        responses = client.simGetImages([ImageRequest(2, AirSimImageType.Scene)])

        # Save it to a temporary file
        image = responses[0].image_data_uint8
        AirSimClientBase.write_file(os.path.normpath(TMPFILE), image)

        # Read-load the image as a grayscale array
        image = color.rgb2gray(io.imread(TMPFILE))
        image = image.flatten()
        
        # Run the image through our inference engine.
        # Engine returns a softmax output inside a list, so we grab the first
        # element of the list (the actual softmax vector), whose second element
        # is the absence of an obstacle.
        safety = sess.run(output, feed_dict={x:[image]})[0][1]

        # Slam on the brakes if it ain't safe!
        if safety < 0.5:
            print('Collision detected')
            client.moveByVelocity(0,10,0.3,18)
            

client.enableApiControl(False)


