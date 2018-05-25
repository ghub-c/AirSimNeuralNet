# -*- coding: utf-8 -*-


from AirSimClient import MultirotorClient, ImageRequest, AirSimImageType, AirSimClientBase
import os


#Initial height of the drone
initialZ=-15

#Vx and Vy for flights in m/s
vx = +5
vy = -5

#Queue of 10 images
maximages = 300
#Image directory inside the project
IMAGEDIR = './dataset'
#Array of image
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
z = client.moveToZ(initialZ, 5)
if z == True:
    x1 = client.moveByVelocityZ(vx, vy, initialZ, 100)
        


while True:
    
    #Get uncompressed RGBA array bytes
    responses = client.simGetImages([ImageRequest(3, AirSimImageType.Scene)])  
    
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
        client.reset()
        break

client.enableApiControl(False)

