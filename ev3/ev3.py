# This file control the EV3
# Author: Finn G., Jan-Luca D.

import ev3dev.ev3 as ev3
import ev3.ev3Communication as communication
import ev3.MPU9250 as MPU9250
from message import Message
from constants import *
from logger import *
import queue
import time

class EV3:
    """Controls the EV3"""

    def __init__(self):

        # Init screen...
        self.screen = ev3.Screen()

        # Init all snesors...
        self.touchSensor = ev3.TouchSensor()
        self.infraredSensor = ev3.InfraredSensor()
        self.colorSensor = ev3.ColorSensor()
        #self.mpu9250 = MPU9250.MPU9250()

        # Init all motors...
        self.motorR = ev3.LargeMotor('outC')
        self.motorL = ev3.LargeMotor('outA')

        # Create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()

        # Start the Thread for the bluetooth connection...
        self.bluetooth = communication.BluetoothThread(self.receivedData)
        self.bluetooth.setName("BluetoothThread")
        self.bluetooth.start()

        # Add bluetooth listener...
        self.bluetooth.addListener("touchSensor", self.sendTouchValue)
        self.bluetooth.addListener("infraredSensor", self.sendInfraredValue)
        self.bluetooth.addListener("colorSensor", self.sendColorValue)
        self.bluetooth.addListener("screen", self.drawScreen)
        self.bluetooth.addListener("motorR", self.turnRight)
        self.bluetooth.addListener("motorL", self.turnLeft)
        self.bluetooth.addListener("accel", self.sendAccelData)
        self.bluetooth.addListener("gyro", self.sendGyroData)
        self.bluetooth.addListener("mag", self.sendMagData)
        self.bluetooth.addListener("close", self.close)
        
    def receivedData(self, function, value):
        """Execute the listener for the channel"""
        
        # Check if the mode is updating...
        updating = value.split(":")[0] == "update"
        
        # Notice the old value...
        oldValue = None
        
        while self.bluetooth.connected:
            # Get the value...
            channel, value = function(value)
            
            # If the value is not the same like the last time, send the value to the remote...
            if value != oldValue:
                oldValue = Value
                self.bluetooth.send(Message(channel = channel,  value = value))
            
            # If the mode is not updating, send the data only once...
            if not updating:
                break
            
            # Wait for 0.1 seconds (TODO: Set interval from the remote)
            time.sleep(0.1)

    def close(self, *args):
        """Close the bluetooth server"""
        
        # Close the bluetooth server...
        self.bluetooth.closeServer()
        
        # Close all running threads...
        global alive
        alive = False
        
        return ("close", "Closed server")

    def drawScreen(self, *args):
        """Draw point on the screen"""
        value = "".join(args)
        points = value.split(":")
        for point in points:
            try:
                x = int(point.split("|")[0])
                y = int(point.split("|")[1])
            except:
                return ("screen",  "Value has wrong format (x|y:x|y:...)")
            self.screen.draw.point((x, y))
        self.screen.update()
        return ("screen",  value)

    def turnRight(self, *args):
        """Turn the right motor"""
        value = "".join(args)
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp = time, speed_sp = speed)
            return ("motorR", "%d:%d" % (time, speed))
        except:
            return ("motorR",  "Device not connected")

    def turnLeft(self, *args):
        """Turn the left motor"""
        value = "".join(args)
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed=int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorL.run_timed(time_sp = time, speed_sp = speed)
            return ("motorL", "%d:%d" % (time, speed))
        except:
            return ("motorL", "Device not connected")

    def sendColorValue(self, *args):
        value = "".join(args)
        if value == "color":
            try:
                color = self.colorSensor.COLORS[self.colorSensor.color]
                return ("colorSensor", color)
            except:
                return ("colorSensor", "Device not connected")
        else:
            try:
                red = self.colorSensor.red
                green = self.colorSensor.green
                blue = self.colorSensor.blue
                return ("colorSensor", "%d:%d:%d" % (red, green, blue))
            except:
                return ("colorSensor", "Device not connected")

    def sendInfraredValue(self, *args):
        """Send the value of the infrared sensor"""
        try:
            value = self.infraredSensor.value()
            return ("infraredSensor",  value)
        except:
            return ("infraredSensor",  "Device not connected")

    def sendTouchValue(self, *args):
        """Send the value of the touch sensor"""
        try:
            value = self.touchSensor.value()
            return ("touchSensor",  value)
        except:
            return ("touchSensor",  "Device not connected")

    def sendAccelData(self, value):
        """Send the values of the accelometer"""
        accel = mpu9250.readAccel()
        return ("accel", "%f:%f:%f" % (accel["x"], accel["y"], accel["z"]))

    def sendGyroData(self, *args):
        """Send the values of the gyroscope"""
        gyro = mpu9250.readGyro()
        return ("gyro", "%f:%f:%f" % (gyro["x"], gyro["y"], gyro["z"]))
        
    def sendMagData(self, *args):
        """Send the values of the magnetometer"""
        mag = mpu9250.readMagnet()
        return ("mag", "%f:%f:%f" % (mag["x"], mag["y"], mag["z"]))
        
        
