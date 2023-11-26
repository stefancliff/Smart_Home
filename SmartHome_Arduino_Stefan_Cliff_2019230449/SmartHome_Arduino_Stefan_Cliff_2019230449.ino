#include <TimerOne.h> // Needed for the timer which is used in a few different places inside this code

//Setting up the pins
#define PhotoresisterSensorPin  A0
#define TemperatureSensorPin    A1

#define Relay_Diode     13
#define Relay_Heater    12
#define Relay_Cooler    11
#define Master_Relay    10

#define Button_Pin      2

// Setting up the variables I will call later on
int RelayDiodeStatus  = LOW;
int RelayHeaterStatus = LOW;
int RelayCoolerStatus = LOW;
int RelayMasterStatus = HIGH;  

float CurrentTemperature;
int temperature;
bool heating = false;
bool cooling = false;

int CurrentButtonState;
int PreviousButtonState;

void setup() {
  
  // Initializing the Serial Monitor
  Serial.begin(9600);

  // Diode Setup
  pinMode(Relay_Diode, OUTPUT);
  digitalWrite(Relay_Diode,   RelayDiodeStatus);

  // Heater Setup
  pinMode(Relay_Heater, OUTPUT);
  digitalWrite(Relay_Heater,  RelayHeaterStatus);

  // Cooler Setup
  pinMode(Relay_Cooler, OUTPUT);
  digitalWrite(Relay_Cooler,  RelayCoolerStatus);

  // Master Relay Setup
  pinMode(Master_Relay, OUTPUT);
  digitalWrite(Master_Relay,   RelayMasterStatus);
  
  temperature = (analogRead(TemperatureSensorPin) * 500.0) / 1023;
  Timer1.initialize(1000000);
  Timer1.attachInterrupt(autoTemp);
  

}

void loop() {
  // Adding my three functions into the loop as to constantly check and be ready for user inputs/sensor detections
  AutomaticTemperature();
  AutomaticLights();
  HomeSecure();

  // Setting up the Serial monitor to react to certain commands the user would enter
  // The Serial.println outputs I left are there on purpose as to better show the idea of what
  // Each command would do in-case of confusion
  if(Serial.available() > 0){
   String SERIAL_INPUT = Serial.readString();
     if(SERIAL_INPUT == "Master On"){
       RelayMasterStatus = HIGH;
       digitalWrite(RelayMaster, RelayMasterStatus);
       //Serial.println("Master Relay turned on!");
       
     } else if (SERIAL_INPUT == "Master Off") {
       RelayMasterStatus = LOW;
       digitalWrite(RelayMaster, RelayMasterStatus);
       //Serial.println("Master Relay turned off!");
        
     } else if (SERIAL_INPUT == "Lights On"){      
       if(RelayMasterStatus == HIGH){
         digitalWrite(RelayDiode, HIGH);
         //Serial.println("Relay Diode turned on!");          
       }
       
       
     } else if (SERIAL_INPUT == "Lights Off"){     
       digitalWrite(RelayDiode, LOW);
       //Serial.println("Relay Diode turned off!");
        
     } else if (SERIAL_INPUT == "Heater On"){      
       if(RelayMasterStatus == HIGH){
         digitalWrite(RelayHeater, HIGH);
         //Serial.println("Relay Heater turned on!");
       }
        
     } else if (SERIAL_INPUT == "Heater off"){      
        digitalWrite(RelayHeater, LOW);
        //Serial.println("Relay Heater turned off!");
        
     } else if (SERIAL_INPUT == "Cooler On") {      
       if(RelayMasterStatus == HIGH){
         digitalWrite(RelayMotorCooler, HIGH);
         //Serial.println("Relay Cooler/Motor turned on!");
       } 
        
     } else if (SERIAL_INPUT == "Cooler Off"){
        digitalWrite(RelayMotorCooler, LOW);
        //Serial.println("Relay Cooler/Motor turned off!");
     }
}


// The idea for the AutomaticTemperature function is to get a reading from the LM35 and based on its readings either:
// a) Turn on the heater if it's cooler than 17C, while turning the cooler(DC motor in this case) off
// b) Turn on the cooler if it's hotter than 23C while turning off the heater

void AutomaticTemperature(){
  CurrentTemperature = (analogRead(TemperatureSensorPin) * 500.0 / 1023); // Setting up the CurrentTemperature
  
  if(CurrentTemperature < 17)
  {
    cooling = false;
    RelayCoolerStatus = LOW;
    digitalWrite(RelayMotorCooler, RelayCoolerStatus);
    
    heating = true;
    RelayHeaterStatus = HIGH;
    digitalWrite(RelayHeater, RelayHeaterStatus);
  }
  else{
    if(CurrentTemperature > 23)
    {
      cooling = true;
      RelayCoolerStatus = HIGH;
      digitalWrite(RelayMotorCooler, RelayCoolerStatus);
      
      heating = false;
      RelayHeaterStatus = LOW;
      digitalWrite(RelayHeater, RelayHeaterStatus);
    }
  }
  Timer1.initialize(5000000);                   // Adding about a 5 second delay between readings as to avoid overloading, 
  Serial.println(CurrentTemperature);           // the system with readings which would likely lead to missreadings and missed readings otherwise
}


// The idea with the HomeSecurity function is that when motion is detected (or a button is pressed in this case), that the light
// turns on for ten seconds. After which the button turns off again, if no more movemenet is detected. 
void HomeSecurity() {
 CurrentButtonState  = digitalRead(ButtonPin);  // Setting up the button to give value to our current state variable
  if(CurrentButtonState == LOW){                // If the button has been pressed then it tells the Relay Diode to turn on for 10 seconds
    digitalWrite(RelayDiode, HIGH);             // Active the diode and its relay
    Timer1.initialize(10000000);                // Work for 10 seconds
    digitalWrite(RelayDiode, LOW);              // Deactive the diode and its relay
  }
   
  PreviousButtonState = CurrentButtonState;     // Storing the old state 
  Timer1.initialize(5000000);                   // Similar to the Automatic Temp, having a 5 second delay leads to better and cleaner value reports
  Serial.println(CurrentButtonState);           // This will actually be what the python script will later on send to ThingSpeak
 }


// The point of this function is to take in the ambient light of its surroundings via the photo-resistor and,
// based on our own ratio, if the value of the ambient light falls bellow 30% than the diode turns on and stays on so long as 
// the photo-resistor still reads less than 30%
void AutomaticLights(){
 int i = map(analogRead(PhotoresisterSensorPin), 0, 1023, 0, 100);
 if(i < 30) {
   digitalWrite(RelayDiode, HIGH);
 } else {
   digitalWrite(RelayDiode, LOW);
 }
 Timer1.initialize(5000000);
 Serial.println(i);
 }
}
