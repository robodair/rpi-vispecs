// wakeUTC_HOUR.ino
// Author: alisdairrobertson | alisdairrobertson.com
// ============
// What this does:
// During setup the arduino sets an alarm for the next UTC 0200 (~UTC+10 solar noon)
// At that 2 AM the RTC wakes the arduino which wakes the rpi then waits for it to perform it's tasks.
// After 90 seconds the arduino times out the rpi and makes it issue a shutdown command.

// TODO
// + At the moment the RTC alarm is set again in every loop function (because of the way the alarm has to initially be set for not 24hours)
//   This wastes power so there should be a check/flag to see if the alarm has already been set up after the first cycle.
//    Note that this might introduce the potential for the wakeup time to steadily drift into the afternoon. (minutely, but still)
//    However over only a 3-month deployment before arduino would be reset again that doesn't really matter


// +++++ Configuration ++++++++++
// The time of day to wake in UTC (used when calculating alarm times)
#define UTC_HOUR  2                       // integer 0-23 - so 2 is UTC 2am (Canberra solar noon)
// rpi timeout allowance
#define RPI_POWER_TIMEOUT_MS     90000    // in ms - so this is 90 seconds
// +++++ End Configuration +++++++

// ***** INCLUDES *****
#include "SleepyPi.h"
#include <Time.h>
#include <LowPower.h>
#include <DS1374RTC.h>
#include <Wire.h>

typedef enum {
   ePI_OFF = 0,
   ePI_BOOTING,
   ePI_ON,
   ePI_SHUTTING_DOWN,
   ePI_SHUTDOWN
}ePISTATE;

ePISTATE  rpiState;
const int LED_PIN = 13;

void alarm_isr()
{
    // Just a handler for the alarm interrupt.
}

void setup()
{ 
  

  pinMode(LED_PIN, OUTPUT);       // Configure "Standard" LED pin
  digitalWrite(LED_PIN,LOW);      // Switch on LED when we run setup

  SleepyPi.enablePiPower(false);  // Make sure the pi is switched off
  SleepyPi.enableExtPower(false); // We never use external power so switch it off
  
  rpiState = ePI_OFF;             // Set the recorded state of the rpi to OFF

  // We do not set the time on the RTC because we don't want to muck up the time when we restart the arduino
  // The correct time will be set by the rpi while we have a power bypass installed (remember to set it as UTC, the RTC is only in UTC)

//  Serial.begin(9600);                                                   // Initialise Serial comms
//  Serial.print("setup() | RTC Time: "); printTime(currentTime,true);    // Send the time to the serial (for debugging)

  delay(1000);                    // Pause for a second
}

void loop() 
{
//    digitalWrite(LED_PIN,HIGH);    // Switch on LED when we start loop
//    Serial.println("loop() | Sleeping NOW!");

    unsigned long timeNowMs, timeStartMs;
    tmElements_t  currentTime; 
    bool pi_running;

    SleepyPi.readTime(currentTime); // Get the current time off the RTC
    setNoonAlarm(currentTime);      // Set an alarm for the next noon
  
    
    attachInterrupt(0, alarm_isr, FALLING);		// Allow wake up alarm to trigger interrupt on falling edge.
    SleepyPi.ackAlarm();
   
//    digitalWrite(LED_PIN,LOW);    // Switch off LED when we sleep
    SleepyPi.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF); // Enter power down state with ADC and BOD module disabled.
    
    detachInterrupt(0);   // Just woke up, Disable external pin interrupt on wake up pin.
    
    SleepyPi.enablePiPower(true);   
//    Serial.print("I've just woken up at: "); SleepyPi.readTime(currentTime); printTime(currentTime,true); // Debugging to serial
    
//    digitalWrite(LED_PIN,HIGH); delay(250); digitalWrite(LED_PIN,LOW);  // Blink LED when we wake up
   
    rpiState = ePI_BOOTING;   // Set rpi state to BOOTING
    
    // The RPi is now awake. Wait for it to shutdown or force it off after set timeout.  
    timeStartMs = timeNowMs = millis();
    while (((timeNowMs - timeStartMs) < RPI_POWER_TIMEOUT_MS) && rpiState != ePI_SHUTDOWN)  // While we haven't reached the timeout
    {
         pi_running = SleepyPi.checkPiStatus(false);  // Get the status of the rpi (checking the handshake pin)
         
         if(pi_running == true)           // if rpi is running
         {
//            digitalWrite(LED_PIN,HIGH);   // debugging, Led on if we detect the pi running
//            Serial.print("+");            // debugging
            rpiState = ePI_ON;            // Set rpi state to ON
            delay(500);                   // 1/2 sec pause before checking again
         }
         else
         {
           if(rpiState == ePI_BOOTING)    // if rpi is still booting
           { 
//              Serial.print(".");        // debugging
              delay(500);                 // 1/2 sec pause before checking again 
           }
           else {
//              Serial.println(); Serial.println("RPi not running..."); // debugging
              rpiState = ePI_SHUTDOWN;    // set the rpi state to SHUTDOWN
           }
         }
         timeNowMs = millis();
    }

    if((timeNowMs - timeStartMs) >= RPI_POWER_TIMEOUT_MS)   // if we timed out the rpi
    {
//       Serial.println(); Serial.print("TimeOut! At: "); // debugging
//       if (SleepyPi.readTime(currentTime)) 
//       {
//          printTime(currentTime,false); 
//       }
       SleepyPi.piShutdown(true);         // Shut down the rpi using handshake pins
//       SleepyPi.enableExtPower(false);  // ext power was never enabled
       rpiState = ePI_OFF;                // Set rpi state as OFF
    }
    else
    {
//       Serial.println(); 
//       Serial.println("RPi Shutdown, I'm going back to sleep..."); 
       SleepyPi.piShutdown(true);      
       SleepyPi.enableExtPower(false);
       rpiState = ePI_OFF;       
    } 
    
    setNoonAlarm(currentTime); // Set an alarm for the next noon, means less potential for drifting wakeup time
//    digitalWrite(LED_PIN,LOW); // ensure led off before arduino sleeps again
}


//
// printTime() takes a tmElements_t and prints a nicely formatted time to serial comms
//
//bool printTime(tmElements_t tm, bool printDate)
//{
//    print2digits(tm.Hour);
//    Serial.write(':');
//    print2digits(tm.Minute);
//    Serial.write(':');
//    print2digits(tm.Second);
//    if(printDate == true)
//    {
//      Serial.print(", Date (D/M/Y) = ");
//      Serial.print(tm.Day);
//      Serial.write('/');
//      Serial.print(tm.Month);
//      Serial.write('/');
//      Serial.print(tmYearToCalendar(tm.Year));
//    }
//    Serial.println();   
//}


//
// Print a single digit with a leading 0 (for formatting time)
//
//void print2digits(int number) {
//  if (number >= 0 && number < 10) {
//    Serial.write('0');
//  }
//  Serial.print(number);
//}

//
// set the UTC alarm for the nearest UTC o'clocl as specified by UTC_HOUR (needs to be UTC 2 am for UTC+10 solar noon)
//
void setNoonAlarm(tmElements_t currentTime) {
  tmElements_t powerUpInterval;           // Declare a time element that will be used to set the power up interval
  
  int seconds = 60 - currentTime.Second;  // get seconds till the next minute
  int minutes = 60 - currentTime.Minute;  // get minutes till the next hour
  int hours = 23 - currentTime.Hour;      // get hours till the next UTC midnight

//  Serial.print("Hr to UTC midnight: "); Serial.println(hours);    // debugging
//  Serial.print("Min to UTC midnight: "); Serial.println(minutes);
//  Serial.print("Sec to UTC midnight: "); Serial.println(seconds);

  if (seconds >= 60) {                    // if seconds are a full minute
    seconds = 0;                              // set seconds to 0
    minutes=minutes+1;                        // add a minute
  }
  
  if (minutes >= 60){                     // if minutes are a full hour
    minutes = 0;                              // set minutes to 0
    hours=hours+1;                            // add an hour
  }
  
  // we have times till the next UTC midnight here
  // we want times until the next UTC_HOUR
  if (hours >= (24 - UTC_HOUR) && (minutes > 0 || seconds > 0)) {   // check to see if the time is still to come in this day
    hours = hours-(24 - UTC_HOUR);                                  // Adjust the time so we get the one today
  }
  else {                                                            // If the target time has already past for today, 
    hours = hours + UTC_HOUR;                                       // correct for the target time tomorrow
  }
  
  // assign values for setting the alarm
  powerUpInterval.Hour = hours;
  powerUpInterval.Minute = minutes;
  powerUpInterval.Second = seconds;
  powerUpInterval.Day = 0;

//  Serial.print("Hr to alarm: ");                                    // debugging
//  Serial.println(powerUpInterval.Hour);
//  Serial.print("Min to alarm: ");
//  Serial.println(powerUpInterval.Minute);
//  Serial.print("Sec to seconds: ");
//  Serial.println(powerUpInterval.Second);
//  Serial.print("Next Alarm Interval: ");
//  printTime(powerUpInterval,false);

  SleepyPi.setAlarm(powerUpInterval);                               // Set the alarm
  SleepyPi.enableWakeupAlarm();
}

