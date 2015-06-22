#include <Servo.h>

// Create two servo "object", called servoX and servoY. 
// Each servo object controls one servo.
Servo servoX;
Servo servoY;

//Global variable
int current_x_angle;
int current_y_angle;

void setup() 
{ 
  
  // Use the serial monitor window to help debug our sketch:
  Serial.begin(9600);

  // Enable control of a servo on pin 9:
  servoX.attach(9);
  // Enable control of a servo on pin 10:
  servoY.attach(10);

  //Init
  current_x_angle = 90; 
  current_y_angle = 90;    
      
  //Initialise both servoto 90
  servoX.write(90);
  servoY.write(90);
  
  Serial.println("Ready to read");   
} 

void loop() 
{ 
  if (Serial.available() > 0) {
    String reader = Serial.readString();
      
    if (reader == "reset") {      
      servoX.write(90);
      servoY.write(90);
    }
    else {
      //Position of X in the reader string.
      int x_pos = reader.indexOf("X");      
      
      //Position of Y in the reader string.
      int y_pos = reader.indexOf("Y");     
      
      //Value of X
      String x_value = reader.substring(x_pos+1,y_pos);  
      
      //Value of Y
      String y_value = reader.substring(y_pos+1);    
      
      //Move x servo     
      current_x_angle += x_value.toInt();
      servoX.write(current_x_angle);      
      
      //Move y servo      
      current_y_angle += y_value.toInt();
      servoY.write(current_y_angle);      
    }
  }   
  else {
    delay(500);
    Serial.print("02:02:X");
    Serial.print(current_x_angle);
    Serial.print("Y");
    Serial.println(current_y_angle);
  }
} 


