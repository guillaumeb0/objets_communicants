const int flexpin = 0; 
const String prefix = "00:00:";

void setup() {
  // Use the serial monitor window to help debug our sketch:
  Serial.begin(9600);
}

void loop() {
  int flexposition;    // Input value from the analog pin.

  // Read the position of the flex sensor :
  flexposition = analogRead(flexpin);
  //write the value with rigth format on the serial:
  Serial.println(prefix + String(flexposition));
  delay(800);
}
