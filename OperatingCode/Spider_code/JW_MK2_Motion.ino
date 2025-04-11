
#include <Servo.h>

Servo servo1;
Servo servo2;

const int pirPin = 2;     // PIR output pin
const int servoPin1 = 9;  // Servo 1
const int servoPin2 = 10; // Servo 2
bool triggered = false;

void setup() {
  Serial.begin(9600);

  pinMode(pirPin, INPUT);
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);

  servo1.write(0);
  servo2.write(90);  // Assuming mirrored
}

void loop() {
  int motion = digitalRead(pirPin);

  if (motion == HIGH && !triggered) {
    Serial.println("Motion detected!");
    triggered = true;

    for (int angle = 0; angle <= 90; angle++) {
      servo1.write(angle);
      servo2.write(90 - angle);
      delay(15);
    }

    delay(500); // Hold

    for (int angle = 90; angle >= 0; angle--) {
      servo1.write(angle);
      servo2.write(90 - angle);
      delay(15);
    }
  }

  if (motion == LOW) {
    triggered = false; // Reset state when motion ends
  }

  delay(100); // debounce-ish
}
