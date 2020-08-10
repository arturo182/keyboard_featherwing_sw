#include <Adafruit_GFX.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_ILI9341.h>
#include <Adafruit_STMPE610.h>
#include <Adafruit_NeoPixel.h>
#include <BBQ10Keyboard.h>
#include <SD.h>

#define STMPE_CS 6
#define TFT_CS 9
#define TFT_DC 10
#define SD_CS 5
#define NEOPIXEL_PIN 11

#define TS_MINX 150
#define TS_MINY 130
#define TS_MAXX 3800
#define TS_MAXY 4000

Adafruit_STMPE610 ts(STMPE_CS);
Adafruit_ILI9341 tft(TFT_CS, TFT_DC);
Adafruit_NeoPixel pixels(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
BBQ10Keyboard keyboard;
File root;

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  const bool sd = SD.begin(SD_CS);
  
  tft.begin();
  ts.begin();
  
  pixels.begin();
  pixels.setBrightness(30);
  
  keyboard.begin();
  keyboard.setBacklight(0.5f);

  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);

  tft.print("Hello FeatherWing!\n");
  tft.print("Touch to paint, type to... type\n");

  // List SD card files if available
  if (sd) {
    tft.print("SD Card contents:\n");
    root = SD.open("/");
    
    while (true) {
      File entry =  root.openNextFile();
      if (!entry)
        break;

      tft.println(entry.name());
      entry.close();
    }
  }
}

void loop()
{
  // Paint touch
  if (!ts.bufferEmpty()) {
    TS_Point p = ts.getPoint();
    p.x = map(p.x, TS_MINY, TS_MAXY, tft.height(), 0);
    p.y = map(p.y, TS_MINX, TS_MAXX, 0, tft.width());
    
    pixels.setPixelColor(0, pixels.Color(255, 0, 255));
    pixels.show(); 
    
    tft.fillCircle(p.y, p.x, 3, ILI9341_MAGENTA);
    
    pixels.clear();
    pixels.show(); 
  }

  // Print keys to screen
  if (keyboard.keyCount()) {
    const BBQ10Keyboard::KeyEvent key = keyboard.keyEvent();
    if (key.state == BBQ10Keyboard::StateRelease) {
      pixels.setPixelColor(0, pixels.Color(0, 255, 0));
      pixels.show(); 
    
      tft.print(key.key);
      
      pixels.clear();
      pixels.show(); 
    }
  }
}
