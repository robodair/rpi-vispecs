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
#define TIME_INTERVAL_SECONDS    0
#define TIME_INTERVAL_MINUTES    0   
#define TIME_INTERVAL_HOURS      24
#define TIME_INTERVAL_DAYS       0

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
}

void setup()
{ 
  // Configure "Standard" LED pin
  pinMode(LED_PIN, OUTPUT);		
  digitalWrite(LED_PIN,LOW);		// Switch off LED

  SleepyPi.enablePiPower(false); 
  SleepyPi.enableExtPower(false);

  // initialize serial communication: In Arduino IDE use "Serial Monitor"
  Serial.begin(9600);
  Serial.println("Starting Vispecs SleepyPiWakeup");

  // Interval that will be used in loop to set up wakeup time
  powerUpTime.Hour = TIME_INTERVAL_HOURS; // 24 Hours from the wakeup time
  
  // Set the alarm for next UTC 2AM (Australian solar noon) then sleep
  SleepyPi.enableWakeupAlarm();
  SleepyPi.ackAlarm();
  setUTC2amAlarm();
  attachInterrupt(0, alarm_isr, FALLING);    // Alarm pin
   // Allow wake up triggered by button press
  attachInterrupt(1, button_isr, LOW);    // button pin 
}

void loop() 
{
    unsigned long timeNowMs, timeStartMs;
    tmElements_t  currentTime; 
    bool pi_running;
  
    // Allow wake up alarm to trigger interrupt on falling edge.
    attachInterrupt(0, alarm_isr, FALLING);    // Alarm pin
    if (buttonPressed){
      // Reset alarm & button variable if button was pressed
      buttonPressed = false;
      SleepyPi.ackAlarm();
      setUTC2amAlarm();
    }
    
    // +++++++++ Test +++++++++++++
    SleepyPi.readTime(currentTime);
    Serial.print("Going To Sleep:\n");
    Serial.print("Current Time = ");
    printTime(currentTime,false); 
    SleepyPi.readAlarm(currentTime);
    Serial.print("Alarm Time = ");
    printTime(currentTime,false); 
    delay(1000);
    // ++++++++++++++++++++++++++++++
    
    // Enter power down state with ADC and BOD module disabled.
    // Wake up when wake up pin is low.
    SleepyPi.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF); 
    
    // Disable external pin interrupt on wake up pin.
    detachInterrupt(0);
    // Ack old and set a new alarm as soon as the pi wakes up
    SleepyPi.ackAlarm();
    SleepyPi.setAlarm(powerUpTime); 
    
    SleepyPi.enablePiPower(true);   
    Serial.print("\n\nI've Just woken up: ");
    SleepyPi.readTime(currentTime);
    printTime(currentTime,false); 
    
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
            printTime(currentTime,false); 
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
          break;
         }
      }
    }
    
    SleepyPi.piShutdown(true);      
    SleepyPi.enableExtPower(false); 
    
}

void setUTC2amAlarm() {
  tmElements_t  currentTime, firstAlarm;
  // Grab the time from the RTC
  SleepyPi.readTime(currentTime);
  Serial.print("Read Time = ");
    printTime(currentTime,false); 

  // Calculate number of hours to add
  int hours = 0;
  if (currentTime.Hour){
    
    hours = (24-currentTime.Hour + 2)%24;
  }

  // Calculate number of mins to add
  int minutes = 0;
  if (currentTime.Minute){
    
    minutes = 60-currentTime.Minute;
    hours--;
  }

  // Calculate the number of seconds to add
  int seconds = 0;
  if (currentTime.Second){
    seconds = 60-currentTime.Second;
    minutes--;
  }

  firstAlarm.Second = seconds;
  firstAlarm.Minute = minutes;
  firstAlarm.Hour = hours;

  Serial.print("Time for first alarm: ");
  printTime(firstAlarm, false);

  // Set an alarm for this duration
  SleepyPi.setAlarm(firstAlarm);
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
