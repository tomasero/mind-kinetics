//  Demo function:The application method to drive the DC motor.
//  Author:Frankie.Chu
//  Date:20 November, 2012

#include "MotorDriver.h"

void setup()
{
	/*Configure the motor A to control the wheel at the left side.*/
	/*Configure the motor B to control the wheel at the right side.*/
	motordriver.init();
//	motordriver.setSpeed(200,MOTORB);
	motordriver.setSpeed(200,MOTORA);
}
 
void loop()
{
	motordriver.goForward();
	delay(2000);
	motordriver.stop();
	delay(1000);
	motordriver.goBackward();
	delay(2000);
	motordriver.stop();
	delay(1000);
	motordriver.goLeft();
	delay(2000);
	motordriver.stop();
	delay(1000);
	motordriver.goRight();
	delay(2000);
	motordriver.stop();
	delay(1000);
	
}
