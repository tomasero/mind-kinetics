void setup() {
   Serial.begin(9600);
   Serial.println("test rotation"); 
}

void loop() {
   Serial.println("tick\n");
   analogWrite(3, 255);
   analogWrite(5, 0);
   delay(1000);
   Serial.println("tock\n");
   analogWrite(3, 0);
   analogWrite(5, 255);
   delay(1000);
}
