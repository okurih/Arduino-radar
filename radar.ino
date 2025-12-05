#include <Servo.h>

Servo servo;

const int servoPin=9;
const int trigPin=10;
const int echoPin=11;

int angle=0;
int direction=1;

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
servo.attach(servoPin);
pinMode(trigPin, OUTPUT);
pinMode(echoPin, INPUT);
} 

void loop() {
  // put your main code here, to run repeatedly:
  servo.write(angle);
  delay(50);

int distance = getDistance();
Serial.print(angle);
Serial.print(",");
Serial.print(distance);
Serial.println();

angle += direction*2;

if(angle >= 180) {
  angle = 180;
  direction = -1;  // reverse direction
} else if(angle <= 0) {
  angle = 0;
  direction = 1;   // reverse direction
}

}


int getDistance(){

digitalWrite(trigPin, LOW);
delayMicroseconds(2);
digitalWrite(trigPin, HIGH);
delayMicroseconds(10);
digitalWrite(trigPin, LOW);

int duration = pulseIn(echoPin, HIGH, 30000);
int distance = (duration/2) * 0.0343; // in cm/us
if(distance > 400) return 999;
  else return distance;
}











