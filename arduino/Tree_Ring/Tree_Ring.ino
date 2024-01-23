
int dirPin = 3;
int stepperPin = 4;
int limitSwitch = 5;
int enablePin = 6;
int resetPin = 7;

int incomingByte;

bool isClockwise = true;
bool isActive = false;

int active_counter = 0;
int rotateAmount = 200;

void setup()
{
  pinMode(dirPin, OUTPUT);
  pinMode(stepperPin, OUTPUT);
  pinMode(limitSwitch, INPUT_PULLUP);
  digitalWrite(dirPin, LOW);
  digitalWrite(stepperPin, LOW);
  activate();
  Serial.begin(9600);
}

void step(boolean dir,int steps)
 {
 digitalWrite(dirPin,dir);

 for(int i=0;i<steps;i++)
 {
   digitalWrite(stepperPin, HIGH);
   delayMicroseconds(600);//Adjust the speed of motor. Increase the value, motor speed become slower.
   digitalWrite(stepperPin, LOW);
   delayMicroseconds(600);
 }
}

void Zero(){
  Serial.write("Zeroing");
  while(digitalRead(limitSwitch) != 0){
    step(true,20);
  }
  step(false,rotateAmount);
  Serial.write("Zeroed");
}

void activate(){
  if(!isActive){
    active_counter = 0;
    digitalWrite(enablePin, HIGH);
    digitalWrite(resetPin, LOW);
    isActive = true;
    delayMicroseconds(1000);
  }
}

void deactivate(){
  digitalWrite(enablePin, LOW);
  digitalWrite(resetPin, HIGH);
  isActive = false;
}

void loop()
{
 //steps per revolution for 200 pulses = 360 degree full cycle rotation
 if(Serial.available()){
  incomingByte = Serial.read();
  if(incomingByte == 72){ // H
    Serial.write("Clockwise");
    isClockwise = true;
  } 
  if(incomingByte == 76){ // L
    Serial.write("AntiClockwise");
    isClockwise = false;
  }
  if(incomingByte == 82){ // R
    activate();
    step(isClockwise, rotateAmount * 3);//(direction ,steps per revolution). This is clockwise rotation.
  }
  if(incomingByte == 90){ // Z
    activate();
    Zero();
  }
    if(incomingByte == 43){ // + Increase Rotation Amount
    rotateAmount = rotateAmount + 20;
    Serial.write(rotateAmount);
  }
  if(incomingByte == 45){ // - Decrease Rotation amount
    rotateAmount = rotateAmount - 20;
    Serial.write(rotateAmount);
  }
  if(incomingByte == 61){ // = Get current Rotation Amount
    Serial.write(rotateAmount);
  }
 }

  active_counter++;
 if(active_counter == 6000){
  deactivate();
 }
 //step(false,1000);//Turn (direction ,steps per revolution). This is anticlockwise rotation.
 //delay(500);
}