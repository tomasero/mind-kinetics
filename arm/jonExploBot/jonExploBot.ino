// Bounce.pde
// -*- mode: C++ -*-
//
// Make a single stepper bounce from one limit to another
//
// Copyright (C) 2012 Mike McCauley
// $Id: Random.pde,v 1.1 2011/01/05 01:51:01 mikem Exp mikem $

#include <AccelStepper.h>
#include <Servo.h>
//#include <Serial.h>
 
Servo myservo;
// Define a stepper and the pins it will use
AccelStepper stepper(1, 26, 28); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

int pos = 0;
int stepPos = 0;
void setup()
{  
  Serial.begin(9600);
  myservo.attach(6);
  //myservo.write(90);
  // Change these to suit your stepper if you want
  pinMode(24,OUTPUT);
  digitalWrite(24,LOW);
  //stepper.setPinsInverted();
  stepper.enableOutputs();
  stepper.setMaxSpeed(800);
  stepper.setAcceleration(100);
  stepper.moveTo(0);
}

void loop()
{  
    char inByte1;
    if (Serial.available() > 0) {
      stepper.setMaxSpeed(random(200,800));
      stepper.setAcceleration(random(50,1800));
      inByte1 = Serial.read();
      //Serial.println(stepPos);
      
    
      if(inByte1 == 'A')
      {
        stepPos+=100;
      }
      if(inByte1 == 'a')
      {
        stepPos-=100;
      }
      stepPos = constrain(stepPos,-1500,1500);
    }
    
    
    
    
    //myservo.write(90+(10*(inByte4==20));
    // If at the end of travel go to the other end
    /*if (stepper.distanceToGo() == 0)
      stepper.moveTo(-stepper.currentPosition());*/
      
    stepper.moveTo(stepPos);

    stepper.run();
    
}
