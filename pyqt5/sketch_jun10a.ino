void setup() {
  Serial.begin(9600);
  // Wait for the serial port to initialize
  delay(1000);
}

void loop() {
  // Clear the serial buffer before reading new data
  clearSerialBuffer();

  // Define variables for Arduino's onboard ADC channels
  int Ain0, Ain1, Ain2, Ain3, Ain4, Ain5;

  // Read analog values
  Ain0 = analogRead(A0);
  Ain1 = analogRead(A1);
  Ain2 = analogRead(A2);
  Ain3 = analogRead(A3);
  Ain4 = analogRead(A4);
  Ain5 = analogRead(A5);

  // Format the string
  char buffer[53];
  sprintf(buffer, "A0_%04d_A1_%04d_A2_%04d_A3_%04d_A4_%04d_A5_%04d", Ain0, Ain1, Ain2, Ain3, Ain4, Ain5);
  
  // Send the formatted string via serial
  Serial.println(buffer);
  
  // Wait for 1 seconds
  delay(1000);
}

void clearSerialBuffer() {
  while (Serial.available() > 0) {
    Serial.read();
  }
}
