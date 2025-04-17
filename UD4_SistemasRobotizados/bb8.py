from controller import Robot, Keyboard, Camera, Motor
import math

# Constants
MAX_SPEED = 10.0
ATTENUATION = 0.9
SPEED_BOOST = 1.5  # 50% más rápido

def usage():
    print("Sample controller of the Sphero's BB-8 robot.\n")
    print("You can pilot the robot using the computer keyboard:")
    print("- 'W': move forward.")
    print("- 'S': move backward.")
    print("- 'A': spin left.")
    print("- 'D': spin right.")
    print("- 'Shift + W': move forward with increased speed.")
    print("- 'space': stop the motors.")

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

# Initialization
robot = Robot()
usage()

time_step = int(robot.getBasicTimeStep())

# Motors
body_yaw_motor = robot.getDevice("body yaw motor")
body_yaw_motor.setPosition(float('inf'))  # Infinite position control (no limit)
body_yaw_motor.setVelocity(0.0)  # Set velocity to 0 to stop movement at the start

body_pitch_motor = robot.getDevice("body pitch motor")
body_pitch_motor.setPosition(float('inf'))  # Infinite position control (no limit)
body_pitch_motor.setVelocity(0.0)  # Set velocity to 0 to stop movement at the start

head_yaw_motor = robot.getDevice("head yaw motor")
head_yaw_motor.setPosition(float('inf'))  # Infinite position control (no limit)
head_yaw_motor.setVelocity(0.0)  # Set velocity to 0 to stop movement at the start

# Enable cameras
camera = robot.getDevice("camera")  # Assuming the camera is called "camera"
camera.enable(time_step)

# Enable keyboard
keyboard = Keyboard()
keyboard.enable(time_step)

# State variables
yaw_speed = 0.0
pitch_speed = 0.0
speed_multiplier = 1.0  # Normal speed multiplier

# Main loop
while robot.step(time_step) != -1:
    # Keyboard control
    key = keyboard.getKey()
    while key != -1:
        if key == ord('W'):
            pitch_speed += ATTENUATION * speed_multiplier
        elif key == ord('S'):
            pitch_speed -= ATTENUATION * speed_multiplier
        elif key == ord('D'):
            yaw_speed -= ATTENUATION
        elif key == ord('A'):
            yaw_speed += ATTENUATION
        elif key == ord(' '):
            yaw_speed = 0.0
            pitch_speed = 0.0
        elif key == 16:  # 'Shift' key (key code 16)
            # If Shift is pressed while W is pressed, increase speed
            if keyboard.is_pressed(ord('W')):
                speed_multiplier = SPEED_BOOST
        key = keyboard.getKey()

    # Reset speed multiplier when Shift is not pressed
    if not keyboard.is_pressed(16):
        speed_multiplier = 1.0

    # Attenuate speed
    pitch_speed = clamp(pitch_speed * ATTENUATION, -MAX_SPEED, MAX_SPEED)
    yaw_speed = clamp(yaw_speed * ATTENUATION, -MAX_SPEED, MAX_SPEED)

    # Apply speeds only when control keys are pressed
    body_yaw_motor.setVelocity(yaw_speed)
    head_yaw_motor.setVelocity(yaw_speed)
    body_pitch_motor.setVelocity(pitch_speed)

    # Camera follow the robot from behind
    robot_position = robot.getPosition()
    camera_position = [robot_position[0], robot_position[1] + 2, robot_position[2] - 5]
    camera.getField("translation").setSFVec3f(camera_position)
