# -*- coding: utf-8 -*-


from AirSimClient import MultirotorClient, ImageRequest, AirSimImageType, AirSimClientBase
import pprint
import os


#Initial height of the drone
initialZ=-2

#Queue of 10 images
QUEUESIZE = 100
#Image directory inside the project
IMAGEDIR = './images'
#Array of images
imagequeue = []

#We check if image directory exists in project, if not, we create it
try:
    os.stat(IMAGEDIR)
except:
    os.mkdir(IMAGEDIR)
    
    
#Connection to the AirSim simulator
client = MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Connected")

#Move drone forward until it collides
client.moveToZ(initialZ, 3)
client.moveByVelocity(10,0,0.3,18)


while True:
   
    #Get uncompressed RGBA array bytes
    #So response contains image data, pose, timestamp, etc
    responses = client.simGetImages([ImageRequest(1, AirSimImageType.Scene)])  

    #Add image to queue
    imagequeue.append(responses[0].image_data_uint8)

    #Dum queue when it gets full
    if len(imagequeue) == QUEUESIZE:
        for i in range(QUEUESIZE):
            AirSimClientBase.write_file(os.path.normpath(IMAGEDIR + '/image%03d.png'  % i ), imagequeue[i])
        imagequeue.pop(0)    
    
    
    #Print collision info
    collision = client.getCollisionInfo()
    
    if collision.has_collided:
        print("Collision at pos %s, normal %s, impact pt %s, penetration %f, name %s, obj id %d" % (
            pprint.pformat(collision.position), 
            pprint.pformat(collision.normal), 
            pprint.pformat(collision.impact_point), 
            collision.penetration_depth, collision.object_name, collision.object_id))
        break

client.enableApiControl(False)

