
int DIRECTION_PIN = 3;
int STEPPER_PIN = 4;
int LIMIT_SWITCH_PIN = 10;
int ENABLE_PIN = 9;
int RESET_PIN = 5;

int incoming_byte;

bool IS_CLOCKWISE = true;
bool IS_ACTIVE = false;

int active_counter = 0;
int rotate_amount = 1400;//1600; //steps per revolution for 200 pulses = 360 degree full cycle rotation
int millimeters = 3;
int original_millimeters = millimeters;
int actual_movement = rotate_amount * millimeters;

void setup()
{
  /* 
	@brief   Setup the arduino upon power on.
  */
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  pinMode(STEPPER_PIN, OUTPUT);
  pinMode(LIMIT_SWITCH_PIN, INPUT_PULLUP);
  digitalWrite(DIRECTION_PIN, LOW);
  digitalWrite(STEPPER_PIN, LOW);
  activate();
  Serial.begin(9600);
}


void step(boolean dir,int steps)
 {
  /*
	@brief   This makes the motor move by a set amount. 
  @param dir   Direction the Motor Moves.
  @param stepts   Steps for the motor to turn. Minimum number of steps is 600, add more to go slower.
  */

 digitalWrite(DIRECTION_PIN,dir);

 for(int i=0;i<steps;i++)
 {
   digitalWrite(STEPPER_PIN, HIGH);
   delayMicroseconds(150);//Adjust the speed of motor. Increase the value, motor speed become slower.
   digitalWrite(STEPPER_PIN, LOW);
   delayMicroseconds(150);
 }
}

void activate(){
  /* 
	@brief   Wake up the motor driver.
  */
  if(!IS_ACTIVE){
    active_counter = 0;
    digitalWrite(ENABLE_PIN, LOW);
    digitalWrite(RESET_PIN, LOW);
    IS_ACTIVE = true;
    delayMicroseconds(1000);
  }
}


void deactivate(){
  /* 
	@brief   Put the motor driver to sleep. This saves power and makes the motor not heat up.
  */
  digitalWrite(ENABLE_PIN, HIGH);
  digitalWrite(RESET_PIN, HIGH);
  IS_ACTIVE = false;
}


void loop()
{
  /* 
	@brief   Update loop.
  */
  if(Serial.available()) {
    incoming_byte = Serial.read();
    if(incoming_byte == 72) { // H Set platform to rotate clockwise.
      Serial.write("Clockwise");
      IS_CLOCKWISE = true;
    } 
    if(incoming_byte == 76) { // L Set platform to rotate anticlockwise.
      Serial.write("AntiClockwise");
      IS_CLOCKWISE = false;
    }
    if(incoming_byte == 77) { // M Move the platform.
      activate();
      step(IS_CLOCKWISE, actual_movement);
    }
    if(incoming_byte == 82) { // R Reset Rotation Amount.
      activate();
      millimeters = original_millimeters;
    }
    if(incoming_byte == 43) { // + Increase Rotation Amount.
      millimeters = millimeters + 1;
      Serial.write(millimeters);
    }
    if(incoming_byte == 45) { // - Decrease Rotation amount.
      millimeters = millimeters - 1;
      Serial.write(millimeters);
    }
    if(incoming_byte == 61) { // = Get current Rotation Amount.
      Serial.write(millimeters);
    }
    actual_movement = rotate_amount * millimeters;
  }

  // Put motor to sleep if not in use.
  active_counter++;
  if(active_counter == 6000) {
    deactivate();
  }
}