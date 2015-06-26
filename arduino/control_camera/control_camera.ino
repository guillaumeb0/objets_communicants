#include <Servo.h>

// Create two servo "object", called servoX and servoY. 
// Each servo object controls one servo.
Servo servoX;
Servo servoY;

//Bound Maximum and minimum value for a given value of angle
int bound_min_max(int value)
{
  if (value > 180) {
    value = 180;
  }
  else if (value < 0) {
    value = 0;
  }
  
  return value;
}

void setup() 
{ 
  
  // Use the serial monitor window to help debug our sketch:
  Serial.begin(9600);

  // Enable control of a servo on pin 9:
  servoX.attach(9);
  // Enable control of a servo on pin 10:
  servoY.attach(10);
      
  //Initialise both servoto 90
  servoX.write(90);
  servoY.write(90);
  
  Serial.println("Ready to read");   
} 

void loop() 
{ 
  if (Serial.available() > 0) {
    int current_x_angle = 0;
    int current_y_angle = 0;
    
    String reader = Serial.readString();    
    reader.toLowerCase();
      
    if (reader == "reset") {         
      servoX.write(90);
      servoY.write(90);
    }
    else {
      //Position of X in the reader string.
      int x_pos = reader.indexOf("x");  

      //Value of X
      String x_value = reader.substring(x_pos+1);    
   
      //Position of Y in the reader string.
      int y_pos = reader.indexOf("y");  
      
      //Value of Y
      String y_value = reader.substring(y_pos+1);    
      
      //Position of Y in the reader string.
      int a_pos = reader.indexOf("a");  
      
      //Value of A
      String a_value = reader.substring(a_pos, a_pos+1);    
      
      if(a_value == "a") {
        if (reader.substring(x_pos, x_pos+1) == "x") {
          //Set current_x_angle
          current_x_angle = x_value.toInt();
          
          //Bound Maximum and minimum value for angle x
          current_x_angle = bound_min_max(current_x_angle);
          
          //Write the angle
          servoX.write(current_x_angle);          
        }        
        if (reader.substring(y_pos, y_pos+1) == "y") {
          //Set current_y_angle
          current_y_angle = y_value.toInt();
            
          //Bound Maximum and minimum value for angle y
          current_y_angle = bound_min_max(current_y_angle);        
          
          //Write the angle
          servoY.write(current_y_angle);      
        }
      }
      else {
        if (x_value.toInt() != 0) {        
          //Add to current_x_angle    
          current_x_angle = servoX.read() + x_value.toInt();
          
          //Bound Maximum and minimum value for angle x
          current_x_angle = bound_min_max(current_x_angle);
          
          //Write the angle
          servoX.write(current_x_angle);  
        }
        if (y_value.toInt() != 0) {                  
          //Add to current_y_angle       
          current_y_angle = servoY.read() + y_value.toInt();
          
          //Bound Maximum and minimum value for angle y
          current_y_angle = bound_min_max(current_y_angle);  
          
          //Write the angle
          servoY.write(current_y_angle);      
        }
      }     
    }
  }   
  else {
    delay(500);
    Serial.print("02:02:X");
    Serial.print(servoX.read());
    Serial.print("Y");
    Serial.println(servoY.read());
  }
} 


