#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

BEAM_PIN = 17

def test_ir_sensor():
    # Set up GPIO in BCM mode.
    GPIO.setmode(GPIO.BCM)
    
    # Configure the IR sensor pin as input with pull-up resistor.
    GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Allow the sensor to settle.
    time.sleep(0.5)
    
    # Read the sensor's initial state.
    initial_state = GPIO.input(BEAM_PIN)
    
    # Simulate a beam break:
    # Change the pin to output and force it LOW.
    GPIO.setup(BEAM_PIN, GPIO.OUT)
    GPIO.output(BEAM_PIN, GPIO.LOW)
    time.sleep(1)  # Duration of the simulated break.
    
    # Restore the pin to input mode.
    GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    time.sleep(0.5)
    
    # Read the sensor's state after simulation.
    final_state = GPIO.input(BEAM_PIN)
    
    # Clean up the GPIO.
    GPIO.cleanup()
    
    # Assuming that a normal state is HIGH and a beam break should register as LOW,
    # the sensor is considered functioning if it changes from HIGH to LOW.
    if initial_state == GPIO.HIGH and final_state == GPIO.LOW:
        print("IR sensor OK")
    else:
        print("IR sensor FAIL")

if __name__ == "__main__":
    test_ir_sensor()
