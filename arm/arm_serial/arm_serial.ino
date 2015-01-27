//  Demo function:The application method to drive the DC motor.
//  Author:Frankie.Chu
//  Date:20 November, 2012

#include "MotorDriver.h"

void setup()
{
          Serial.begin(115200);

	/*Configure the motor A to control the wheel at the left side.*/
	/*Configure the motor B to control the wheel at the right side.*/
	motordriver.init();
	motordriver.setSpeed(200,MOTORB);
	motordriver.setSpeed(200,MOTORA);

}
 
//void loop()
//{
//  
//	motordriver.goForward();
//	delay(2000);
//	motordriver.stop();
//	delay(1000);
//	motordriver.goBackward();
//	delay(2000);
//	motordriver.stop();
//	delay(1000);

//	motordriver.goLeft();
//	delay(2000);
//	motordriver.stop();
//	delay(1000);
//	motordriver.goRight();
//	delay(2000);
//	motordriver.stop();
//	delay(1000);
	
//}

void loop() {
}

void serialEvent() {
while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
 
    if (inChar == 'a') {
      motordriver.setSpeed(0,MOTORB);
      motordriver.setSpeed(200,MOTORA);
      motordriver.goForward();
    } else if (inChar == 'A') {
      motordriver.setSpeed(0,MOTORB);
      motordriver.setSpeed(200,MOTORA);
      motordriver.goBackward();
    } else if (inChar == 'b') {
      motordriver.setSpeed(200,MOTORB);
      motordriver.setSpeed(0,MOTORA);
      motordriver.goForward();
    } else if (inChar == 'B') {
      motordriver.setSpeed(200,MOTORB);
      motordriver.setSpeed(0,MOTORA);
      motordriver.goBackward();
    } else {
      continue;
    }
    Serial.println('moving motor');
    delay(100);
    motordriver.stop();

  }
}
