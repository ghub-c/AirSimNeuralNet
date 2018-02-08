# -*- coding: utf-8 -*-


from AirSimClient import *
import pprint


initialZ=-2

# connect to the AirSim simulator
client = MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Connected")


client.moveToZ(initialZ, 3)
client.moveByVelocity(10,0,0.3,18)


while True:
   
    collision = client.getCollisionInfo()
    
    if collision.has_collided:
        print("Collision at pos %s, normal %s, impact pt %s, penetration %f, name %s, obj id %d" % (
            pprint.pformat(collision.position), 
            pprint.pformat(collision.normal), 
            pprint.pformat(collision.impact_point), 
            collision.penetration_depth, collision.object_name, collision.object_id))
        break

client.enableApiControl(False)

