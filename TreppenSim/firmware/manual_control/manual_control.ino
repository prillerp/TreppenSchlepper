// TreppenSchlepper prototype — manual button control
// Arduino Mega 2560
//
// 2 driven front wheels (L298N dual H-bridge), 2 passive rear casters.
// EC actuator (BTS7960 #1), HC motor (BTS7960 #2).
// Differential steering: left/right buttons run one wheel faster than the other.
//
// Wiring:
//   EC actuator  -> BTS7960 #1 (RPWM=2, LPWM=3, EN=4)
//   HC motor     -> BTS7960 #2 (RPWM=5, LPWM=6, EN=7)
//   Wheel L+R    -> L298N      (IN1=22, IN2=23, ENA=8, IN3=24, IN4=25, ENB=9)
//   Limit switches: EC_TOP=30, EC_BOT=31, HC_EXT=32, HC_RET=33 (NC, pull-up)
//   Buttons: EC_UP=40, EC_DN=41, HC_EXT=42, HC_RET=43,
//            WHL_FWD=44, WHL_BWD=45, STEER_L=47, STEER_R=48
//   E-stop: pin 46 (NC contact, pull-up — LOW = stopped)
//   MPU6050: SDA=20, SCL=21

#include <Wire.h>

// --- Pin assignments ---

// BTS7960 #1 — Elevator Cylinder
static const uint8_t EC_RPWM = 2;
static const uint8_t EC_LPWM = 3;
static const uint8_t EC_EN   = 4;

// BTS7960 #2 — Horizontal Cylinder (rack-and-pinion motor)
static const uint8_t HC_RPWM = 5;
static const uint8_t HC_LPWM = 6;
static const uint8_t HC_EN   = 7;

// L298N — Front wheels (Left, Right)
static const uint8_t WL_IN1 = 22;
static const uint8_t WL_IN2 = 23;
static const uint8_t WL_ENA = 8;
static const uint8_t WR_IN1 = 24;
static const uint8_t WR_IN2 = 25;
static const uint8_t WR_ENB = 9;

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
static const uint8_t BTN_STEER_L = 47;
static const uint8_t BTN_STEER_R = 48;

// --- PWM speed settings (0-255) ---
static const uint8_t EC_SPEED  = 255;
static const uint8_t HC_SPEED  = 200;
static const uint8_t WHL_SPEED = 180;
static const uint8_t WHL_STEER_SLOW = 60;  // inner wheel during turn

// --- Tilt safety ---
static const float TILT_LIMIT_DEG = 15.0;
static const int MPU_ADDR = 0x68;

bool estop_active = false;
bool tilt_fault = false;

void setup() {
    Serial.begin(115200);
    Serial.println(F("TreppenSchlepper manual control v0.2"));

    uint8_t outputs[] = {
        EC_RPWM, EC_LPWM, EC_EN,
        HC_RPWM, HC_LPWM, HC_EN,
        WL_IN1, WL_IN2, WL_ENA,
        WR_IN1, WR_IN2, WR_ENB
    };
    for (uint8_t p : outputs) {
        pinMode(p, OUTPUT);
        digitalWrite(p, LOW);
    }

    uint8_t inputs[] = {
        LS_EC_TOP, LS_EC_BOT, LS_HC_EXT, LS_HC_RET,
        BTN_EC_UP, BTN_EC_DN, BTN_HC_EXT, BTN_HC_RET,
        BTN_WHL_FWD, BTN_WHL_BWD, BTN_ESTOP,
        BTN_STEER_L, BTN_STEER_R
    };
    for (uint8_t p : inputs) {
        pinMode(p, INPUT_PULLUP);
    }

    digitalWrite(EC_EN, HIGH);
    digitalWrite(HC_EN, HIGH);

    Wire.begin();
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x6B);
    Wire.write(0x00);
    Wire.endTransmission();

    Serial.println(F("Ready. Hold buttons to drive."));
}

void allStop() {
    analogWrite(EC_RPWM, 0);
    analogWrite(EC_LPWM, 0);
    analogWrite(HC_RPWM, 0);
    analogWrite(HC_LPWM, 0);
    digitalWrite(WL_IN1, LOW);
    digitalWrite(WL_IN2, LOW);
    analogWrite(WL_ENA, 0);
    digitalWrite(WR_IN1, LOW);
    digitalWrite(WR_IN2, LOW);
    analogWrite(WR_ENB, 0);
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

void driveWheels(int dir, bool steerLeft, bool steerRight) {
    if (dir == 0) {
        if (steerLeft || steerRight) {
            // Pivot turn: one wheel forward, other backward
            uint8_t speed = WHL_STEER_SLOW;
            if (steerLeft) {
                // Left wheel backward, right wheel forward
                digitalWrite(WL_IN1, LOW);  digitalWrite(WL_IN2, HIGH);
                digitalWrite(WR_IN1, HIGH); digitalWrite(WR_IN2, LOW);
            } else {
                // Left wheel forward, right wheel backward
                digitalWrite(WL_IN1, HIGH); digitalWrite(WL_IN2, LOW);
                digitalWrite(WR_IN1, LOW);  digitalWrite(WR_IN2, HIGH);
            }
            analogWrite(WL_ENA, speed);
            analogWrite(WR_ENB, speed);
        } else {
            digitalWrite(WL_IN1, LOW); digitalWrite(WL_IN2, LOW);
            digitalWrite(WR_IN1, LOW); digitalWrite(WR_IN2, LOW);
            analogWrite(WL_ENA, 0);
            analogWrite(WR_ENB, 0);
        }
        return;
    }

    // Straight or arc drive
    uint8_t speedL = WHL_SPEED;
    uint8_t speedR = WHL_SPEED;
    if (steerLeft)  speedL = WHL_STEER_SLOW;
    if (steerRight) speedR = WHL_STEER_SLOW;

    if (dir > 0) {
        digitalWrite(WL_IN1, HIGH); digitalWrite(WL_IN2, LOW);
        digitalWrite(WR_IN1, HIGH); digitalWrite(WR_IN2, LOW);
    } else {
        digitalWrite(WL_IN1, LOW); digitalWrite(WL_IN2, HIGH);
        digitalWrite(WR_IN1, LOW); digitalWrite(WR_IN2, HIGH);
    }
    analogWrite(WL_ENA, speedL);
    analogWrite(WR_ENB, speedR);
}

static unsigned long lastTiltCheck = 0;

void loop() {
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

    bool ec_up   = (digitalRead(BTN_EC_UP)   == LOW);
    bool ec_dn   = (digitalRead(BTN_EC_DN)   == LOW);
    bool hc_ext  = (digitalRead(BTN_HC_EXT)  == LOW);
    bool hc_ret  = (digitalRead(BTN_HC_RET)  == LOW);
    bool w_fwd   = (digitalRead(BTN_WHL_FWD) == LOW);
    bool w_bwd   = (digitalRead(BTN_WHL_BWD) == LOW);
    bool steer_l = (digitalRead(BTN_STEER_L) == LOW);
    bool steer_r = (digitalRead(BTN_STEER_R) == LOW);

    if (ec_up)       driveEC(1);
    else if (ec_dn)  driveEC(-1);
    else             driveEC(0);

    if (hc_ext)      driveHC(1);
    else if (hc_ret) driveHC(-1);
    else             driveHC(0);

    int wDir = 0;
    if (w_fwd) wDir = 1;
    else if (w_bwd) wDir = -1;
    driveWheels(wDir, steer_l, steer_r);

    delay(10);
}
