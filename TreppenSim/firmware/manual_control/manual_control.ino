// TreppenSchlepper prototype — manual button control
// Arduino Mega 2560
//
// Wiring:
//   EC actuator  -> BTS7960 #1 (RPWM=2, LPWM=3, EN=4)
//   HC actuator  -> BTS7960 #2 (RPWM=5, LPWM=6, EN=7)
//   Wheel FL+FR  -> L298N #1   (IN1=22, IN2=23, ENA=8, IN3=24, IN4=25, ENB=9)
//   Wheel RL+RR  -> L298N #2   (IN1=26, IN2=27, ENA=10, IN3=28, IN4=29, ENB=11)
//   Limit switches: EC_TOP=30, EC_BOT=31, HC_EXT=32, HC_RET=33 (NC, pull-up)
//   Buttons: EC_UP=40, EC_DN=41, HC_EXT=42, HC_RET=43, WHL_FWD=44, WHL_BWD=45
//   E-stop: pin 46 (NC contact, pull-up — LOW = stopped)
//   MPU6050: SDA=20, SCL=21

#include <Wire.h>

// --- Pin assignments ---

// BTS7960 #1 — Elevator Cylinder
static const uint8_t EC_RPWM = 2;
static const uint8_t EC_LPWM = 3;
static const uint8_t EC_EN   = 4;

// BTS7960 #2 — Horizontal Cylinder
static const uint8_t HC_RPWM = 5;
static const uint8_t HC_LPWM = 6;
static const uint8_t HC_EN   = 7;

// L298N #1 — Front wheels (FL, FR)
static const uint8_t WFL_IN1 = 22;
static const uint8_t WFL_IN2 = 23;
static const uint8_t WFL_ENA = 8;
static const uint8_t WFR_IN1 = 24;
static const uint8_t WFR_IN2 = 25;
static const uint8_t WFR_ENB = 9;

// L298N #2 — Rear wheels (RL, RR)
static const uint8_t WRL_IN1 = 26;
static const uint8_t WRL_IN2 = 27;
static const uint8_t WRL_ENA = 10;
static const uint8_t WRR_IN1 = 28;
static const uint8_t WRR_IN2 = 29;
static const uint8_t WRR_ENB = 11;

// Limit switches (NC — LOW when triggered)
static const uint8_t LS_EC_TOP = 30;
static const uint8_t LS_EC_BOT = 31;
static const uint8_t LS_HC_EXT = 32;
static const uint8_t LS_HC_RET = 33;

// Control buttons (active LOW with pull-up)
static const uint8_t BTN_EC_UP   = 40;
static const uint8_t BTN_EC_DN   = 41;
static const uint8_t BTN_HC_EXT  = 42;
static const uint8_t BTN_HC_RET  = 43;
static const uint8_t BTN_WHL_FWD = 44;
static const uint8_t BTN_WHL_BWD = 45;
static const uint8_t BTN_ESTOP   = 46;

// --- PWM speed settings (0-255) ---
static const uint8_t EC_SPEED  = 255;  // full speed (PWM-limited by TA2 internally)
static const uint8_t HC_SPEED  = 200;  // ~80% for gentler HC motion
static const uint8_t WHL_SPEED = 180;  // ~70% wheel speed

// --- Tilt safety ---
static const float TILT_LIMIT_DEG = 15.0;
static const int MPU_ADDR = 0x68;

bool estop_active = false;
bool tilt_fault = false;

void setup() {
    Serial.begin(115200);
    Serial.println(F("TreppenSchlepper manual control v0.1"));

    // Motor driver outputs
    uint8_t outputs[] = {
        EC_RPWM, EC_LPWM, EC_EN,
        HC_RPWM, HC_LPWM, HC_EN,
        WFL_IN1, WFL_IN2, WFL_ENA,
        WFR_IN1, WFR_IN2, WFR_ENB,
        WRL_IN1, WRL_IN2, WRL_ENA,
        WRR_IN1, WRR_IN2, WRR_ENB
    };
    for (uint8_t p : outputs) {
        pinMode(p, OUTPUT);
        digitalWrite(p, LOW);
    }

    // Limit switches and buttons (internal pull-up)
    uint8_t inputs[] = {
        LS_EC_TOP, LS_EC_BOT, LS_HC_EXT, LS_HC_RET,
        BTN_EC_UP, BTN_EC_DN, BTN_HC_EXT, BTN_HC_RET,
        BTN_WHL_FWD, BTN_WHL_BWD, BTN_ESTOP
    };
    for (uint8_t p : inputs) {
        pinMode(p, INPUT_PULLUP);
    }

    // Enable BTS7960 modules
    digitalWrite(EC_EN, HIGH);
    digitalWrite(HC_EN, HIGH);

    // MPU6050 init
    Wire.begin();
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x6B);  // PWR_MGMT_1
    Wire.write(0x00);  // wake up
    Wire.endTransmission();

    Serial.println(F("Ready. Hold buttons to drive."));
}

void allStop() {
    analogWrite(EC_RPWM, 0);
    analogWrite(EC_LPWM, 0);
    analogWrite(HC_RPWM, 0);
    analogWrite(HC_LPWM, 0);
    digitalWrite(WFL_IN1, LOW);
    digitalWrite(WFL_IN2, LOW);
    analogWrite(WFL_ENA, 0);
    digitalWrite(WFR_IN1, LOW);
    digitalWrite(WFR_IN2, LOW);
    analogWrite(WFR_ENB, 0);
    digitalWrite(WRL_IN1, LOW);
    digitalWrite(WRL_IN2, LOW);
    analogWrite(WRL_ENA, 0);
    digitalWrite(WRR_IN1, LOW);
    digitalWrite(WRR_IN2, LOW);
    analogWrite(WRR_ENB, 0);
}

float readTilt() {
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, 6);
    int16_t ax = (Wire.read() << 8) | Wire.read();
    int16_t ay = (Wire.read() << 8) | Wire.read();
    int16_t az = (Wire.read() << 8) | Wire.read();
    float pitch = atan2(ax, sqrt((long)ay * ay + (long)az * az)) * 180.0 / PI;
    return abs(pitch);
}

void driveEC(int dir) {
    if (dir > 0 && digitalRead(LS_EC_TOP) == LOW) return;
    if (dir < 0 && digitalRead(LS_EC_BOT) == LOW) return;
    if (dir > 0) {
        analogWrite(EC_RPWM, EC_SPEED);
        analogWrite(EC_LPWM, 0);
    } else if (dir < 0) {
        analogWrite(EC_RPWM, 0);
        analogWrite(EC_LPWM, EC_SPEED);
    } else {
        analogWrite(EC_RPWM, 0);
        analogWrite(EC_LPWM, 0);
    }
}

void driveHC(int dir) {
    if (dir > 0 && digitalRead(LS_HC_EXT) == LOW) return;
    if (dir < 0 && digitalRead(LS_HC_RET) == LOW) return;
    if (dir > 0) {
        analogWrite(HC_RPWM, HC_SPEED);
        analogWrite(HC_LPWM, 0);
    } else if (dir < 0) {
        analogWrite(HC_RPWM, 0);
        analogWrite(HC_LPWM, HC_SPEED);
    } else {
        analogWrite(HC_RPWM, 0);
        analogWrite(HC_LPWM, 0);
    }
}

void driveWheels(int dir) {
    uint8_t speed = (dir != 0) ? WHL_SPEED : 0;
    // All wheels same direction for forward/backward
    if (dir > 0) {
        digitalWrite(WFL_IN1, HIGH); digitalWrite(WFL_IN2, LOW);
        digitalWrite(WFR_IN1, HIGH); digitalWrite(WFR_IN2, LOW);
        digitalWrite(WRL_IN1, HIGH); digitalWrite(WRL_IN2, LOW);
        digitalWrite(WRR_IN1, HIGH); digitalWrite(WRR_IN2, LOW);
    } else if (dir < 0) {
        digitalWrite(WFL_IN1, LOW); digitalWrite(WFL_IN2, HIGH);
        digitalWrite(WFR_IN1, LOW); digitalWrite(WFR_IN2, HIGH);
        digitalWrite(WRL_IN1, LOW); digitalWrite(WRL_IN2, HIGH);
        digitalWrite(WRR_IN1, LOW); digitalWrite(WRR_IN2, HIGH);
    } else {
        digitalWrite(WFL_IN1, LOW); digitalWrite(WFL_IN2, LOW);
        digitalWrite(WFR_IN1, LOW); digitalWrite(WFR_IN2, LOW);
        digitalWrite(WRL_IN1, LOW); digitalWrite(WRL_IN2, LOW);
        digitalWrite(WRR_IN1, LOW); digitalWrite(WRR_IN2, LOW);
    }
    analogWrite(WFL_ENA, speed);
    analogWrite(WFR_ENB, speed);
    analogWrite(WRL_ENA, speed);
    analogWrite(WRR_ENB, speed);
}

static unsigned long lastTiltCheck = 0;

void loop() {
    // E-stop check (NC contact: HIGH = OK, LOW = stopped)
    if (digitalRead(BTN_ESTOP) == LOW) {
        if (!estop_active) {
            Serial.println(F("*** E-STOP ACTIVE ***"));
            estop_active = true;
        }
        allStop();
        return;
    }
    if (estop_active) {
        Serial.println(F("E-stop released"));
        estop_active = false;
    }

    // Tilt check every 200 ms
    if (millis() - lastTiltCheck > 200) {
        lastTiltCheck = millis();
        float tilt = readTilt();
        if (tilt > TILT_LIMIT_DEG) {
            if (!tilt_fault) {
                Serial.print(F("*** TILT FAULT: "));
                Serial.print(tilt, 1);
                Serial.println(F(" deg ***"));
                tilt_fault = true;
            }
            allStop();
            return;
        }
        tilt_fault = false;
    }
    if (tilt_fault) {
        allStop();
        return;
    }

    // Button-driven control (active LOW)
    bool ec_up  = (digitalRead(BTN_EC_UP)   == LOW);
    bool ec_dn  = (digitalRead(BTN_EC_DN)   == LOW);
    bool hc_ext = (digitalRead(BTN_HC_EXT)  == LOW);
    bool hc_ret = (digitalRead(BTN_HC_RET)  == LOW);
    bool w_fwd  = (digitalRead(BTN_WHL_FWD) == LOW);
    bool w_bwd  = (digitalRead(BTN_WHL_BWD) == LOW);

    if (ec_up)       driveEC(1);
    else if (ec_dn)  driveEC(-1);
    else             driveEC(0);

    if (hc_ext)      driveHC(1);
    else if (hc_ret) driveHC(-1);
    else             driveHC(0);

    if (w_fwd)       driveWheels(1);
    else if (w_bwd)  driveWheels(-1);
    else             driveWheels(0);

    delay(10);
}
