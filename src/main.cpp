#include <Arduino.h>
#include <FastLED.h>

#define LED_PIN_R 4
#define LED_PIN_L 5
#define NUM_LEDS_R 147
#define NUM_LEDS_L 149
CRGB ledR[NUM_LEDS_R];
CRGB ledL[NUM_LEDS_L];
int right_brightness = 50;
int left_brightness = 50;

// arduino substring is (startIndex, endIndex)

void setup() {
    Serial.begin(115200);
    
    FastLED.addLeds<WS2812, LED_PIN_L, GRB>(ledL, NUM_LEDS_L);
    FastLED.addLeds<WS2812, LED_PIN_R, GRB>(ledR, NUM_LEDS_R);

    // FastLED.setBrightness(50);
    FastLED.show();
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');

        int thing_end = command.indexOf("L");
        right_brightness = command.substring(1, 4).toInt();
        left_brightness = command.substring(thing_end +1, thing_end +4).toInt();
        String right = command.substring(4, thing_end);
        String left = command.substring(thing_end +4);

        for (int r = 0; r < right.length() /11; r++) { //red,green,blue,brightness, all have to be 3 digits on a 0-255 scale
            ledR[r] = CRGB(right.substring(r*11, r*11 +3).toInt(), right.substring(r*11 +4, r*11 +7).toInt(), right.substring(r*11 +8, r*11 +11).toInt());
        }
        for (int l = 0; l < left.length() /11; l++) {
            ledL[l] = CRGB(left.substring(l*11, l*11 +3).toInt(), left.substring(l*11 +4, l*11 +7).toInt(), left.substring(l*11 +8, l*11 +11).toInt());
        }
        FastLED[0].showLeds(left_brightness);
        FastLED[1].showLeds(right_brightness);
    }
    else {
        CRGB prev_r = CRGB(0,0,0);
        for (int r = 0; r < sizeof(ledR) / sizeof(ledR[0]); r++) {
            CRGB temp_r = ledR[r];
            ledR[r] = prev_r;
            prev_r = temp_r;
        }
        CRGB prev_l = CRGB(0,0,0);
        for (int r = 0; r < sizeof(ledL) / sizeof(ledL[0]); r++) {
            CRGB temp_l = ledL[r];
            ledL[r] = prev_l;
            prev_l = temp_l;
        }
        delay(4);
        FastLED[0].showLeds(left_brightness);
        FastLED[1].showLeds(right_brightness);
    }
}