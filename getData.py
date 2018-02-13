# -*- coding: utf-8 -*-


from AirSimClient import MultirotorClient, ImageRequest, AirSimImageType, AirSimClientBase
import os


#Initial height of the drone
initialZ=-2

#Queue of 10 images
maximages = 100
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
    #Response contains image data, pose, timestamp, etc
    responses = client.simGetImages([ImageRequest(1, AirSimImageType.Scene)])  

    #Add image to queue
    imagequeue.append(responses[0].image_data_uint8)

    #Dump queue when it gets full
    if len(imagequeue) == maximages:
        for i in range(maximages):
            AirSimClientBase.write_file(os.path.normpath(IMAGEDIR + '/image%03d.png'  % i ), imagequeue[i])
        imagequeue.pop(0)    
    
    
    #Receive info when drone has collided
    collision = client.getCollisionInfo()
    
    if collision.has_collided:
        print("Drone has collided")
        break

client.enableApiControl(False)

