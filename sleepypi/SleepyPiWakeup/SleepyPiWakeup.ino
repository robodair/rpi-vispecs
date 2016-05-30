// 
// Simple example showing how to set the RTC alarm pin to wake up the Arduino
// and then power up the Raspberry Pi
//

// **** INCLUDES *****
#include "SleepyPi.h"
#include <Time.h>
#include <LowPower.h>
#include <DS1374RTC.h>
#include <Wire.h>

#define RPI_POWER_TIMEOUT_MS     300000    // in ms - so this is 5 minutes
#define SECONDS_IN_DAY           86400
#define UTC_HOUR                 2
#define UTC_MINUTE               00
#define UTC_SECOND               00

tmElements_t powerUpTime;
volatile bool  buttonPressed = false;

const int LED_PIN = 13;
const char *monthName[12] = {
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
};

void alarm_isr()
{
    // Just a handler for the alarm interrupt.
    // You could do something here

}

void button_isr()
{
    // A handler for the Button interrupt.
    buttonPressed = true;
    delay(500);
}

void setup()
{ 
  pinMode(17, OUTPUT); // set maintenence pin
  // Configure "Standard" LED pin
  pinMode(LED_PIN, OUTPUT);		
  digitalWrite(LED_PIN,LOW);		// Switch off LED

  SleepyPi.enablePiPower(false); 
  SleepyPi.enableExtPower(false);

  // initialize serial communication: In Arduino IDE use "Serial Monitor"
  Serial.begin(9600);
  Serial.println("\n\nStarting Vispecs SleepyPiWakeup");
  
  // Set the alarm for next UTC 2AM (Australian solar noon) then sleep
  SleepyPi.enableWakeupAlarm();
  
   // Allow wake up triggered by button press
  
}

void loop() 
{
    unsigned long timeNowMs, timeStartMs;
    tmElements_t  currentTime; 
    bool pi_running;

    // Button interrupt
    attachInterrupt(1, button_isr, LOW);    // button pin 
    // Alarm interrupt
    attachInterrupt(0, alarm_isr, FALLING);    // Alarm pin
    
    buttonPressed = false;

    SleepyPi.ackAlarm();
    setUTC2amAlarm();
    
    // +++++++++ Test +++++++++++++
    SleepyPi.readTime(currentTime);
    Serial.print("\nGoing Low Power @: ");
    printTime(currentTime,true); 
    time_t alarm;
    SleepyPi.readAlarm(alarm);
    Serial.print(alarm);
    Serial.print(" seconds until next alarm");
    delay(1000);
    // ++++++++++++++++++++++++++++++
    
    // Enter power down state with ADC and BOD module disabled.
    // Wake up when wake up pin is low.
    SleepyPi.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF); 
    
    // Disable external pin interrupts on wake up pins.
    detachInterrupt(0);
    detachInterrupt(1);

    SleepyPi.ackAlarm();
    
    SleepyPi.enablePiPower(true);   
    Serial.print("\n\nPower Up @: ");
    SleepyPi.readTime(currentTime);
    printTime(currentTime,true); 

    if (buttonPressed){
      Serial.println("Set Maintenence Pin High");
      digitalWrite(17,HIGH);    // Set pin high to tell Pi that we are in maintenence
    }
    
    // The RPi is now awake. Wait for it to shutdown or
    // Force it off after a set timeout.  
    timeStartMs = timeNowMs = millis();
    // Wait for pi to boot
    while ((timeNowMs - timeStartMs) < RPI_POWER_TIMEOUT_MS)
    {
         pi_running = SleepyPi.checkPiStatus(true);
         if(pi_running == true)
         {
            break;  
         }
         Serial.print(".");
         delay(1000);
         timeNowMs = millis();
    }
    while ((timeNowMs - timeStartMs) < RPI_POWER_TIMEOUT_MS)
    {
         pi_running = SleepyPi.checkPiStatus(true);
         if(pi_running == true)
         {
            Serial.print("+");
            delay(1000);      // milliseconds   
         } else {
          break;
         }
         timeNowMs = millis();
    }
    // Only allow timeout if the button was not pressed
    if (!buttonPressed){
      // Did a timeout occur?
      if((timeNowMs - timeStartMs) >= RPI_POWER_TIMEOUT_MS)
      {
         Serial.print("TimeOut!:");
         if (SleepyPi.readTime(currentTime)) 
         {
            printTime(currentTime,true); 
         } else {
            Serial.println("RPi Shutdown Itself");     
         } 
      }
    } else {
      while (pi_running){
        pi_running = SleepyPi.checkPiStatus(true);
         if(pi_running == true)
         {
            Serial.print("o");
            delay(1000);      // milliseconds   
         } else {
          Serial.print("Shutdown after button maintenence");
          SleepyPi.readTime(currentTime);
          printTime(currentTime,true); 
          break;
         }
      }
    }
    
    SleepyPi.piShutdown(true);      
    SleepyPi.enableExtPower(false); 
    
}

void setUTC2amAlarm() {

  // Set the system time from the RTC
  time_t timeRTC;
  RTC.readTime(timeRTC);
  setTime(timeRTC);

  time_t secondsInToToday = now() % (SECONDS_IN_DAY);
  // Find seconds fromUTC midnight a 2 AM alarm should be
  time_t baseAlarm = UTC_HOUR*3600 + UTC_MINUTE*60 + UTC_SECOND;
  
  // Calculate time to next base alarm
  time_t secsToNextAlarm = (baseAlarm + SECONDS_IN_DAY - secondsInToToday) % SECONDS_IN_DAY;

  //Set an alarm for this time
  SleepyPi.setAlarm(secsToNextAlarm);
}



bool printTime(tmElements_t tm, bool printDate)
{
    print2digits(tm.Hour);
    Serial.write(':');
    print2digits(tm.Minute);
    Serial.write(':');
    print2digits(tm.Second);
    if(printDate == true)
    {
      Serial.print(", Date (D/M/Y) = ");
      Serial.print(tm.Day);
      Serial.write('/');
      Serial.print(tm.Month);
      Serial.write('/');
      Serial.print(tmYearToCalendar(tm.Year));
    }
    Serial.println();   
}

void print2digits(int number) {
  if (number >= 0 && number < 10) {
    Serial.write('0');
  }
  Serial.print(number);
}
