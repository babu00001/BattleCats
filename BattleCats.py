import tkinter
import numpy
import threading
import time
import RPi.GPIO as GPIO
import cv2

from PIL import Image
from PIL import ImageTk

MainWindow = tkinter.Tk()
MainWindow.title('Battle Cats')

MainWindow.geometry("1280x1024+0+0")
MainWindow.resizable(False, False)

BattleStop = True;
print('Program Start---------------------------------');

#------------------------------------------------
# Just 1Phase Control
#------------------------------------------------
GPIO.setmode(GPIO.BCM)
STEP_MOTOR_1PHASE_SEQ =[
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]
PHASE_SEQ_COUNT = len(STEP_MOTOR_1PHASE_SEQ);
ONE_TURN_DEGREE = 360;
ONE_TURN_PULSE = 2048;

    
def InitMotor(aMotorPin) :
    for PinNum in aMotorPin:
        GPIO.setup(PinNum, GPIO.OUT)
        GPIO.output(PinNum, False)

def RelMoveMotor(RealRelPos, TargetFreq, aMotorPin, rCurrentPos):
    global BattleStop;
    BattleStop = False;
    PinCount = len(aMotorPin);
    Dir = 1 if 0 < RealRelPos else -1;
    AbsDist = int(abs(RealRelPos) * ONE_TURN_PULSE / ONE_TURN_DEGREE);
    
    while False == BattleStop and 0 < AbsDist :
        for pin in range(0, PinCount):
            GPIO.output(aMotorPin[pin], (True if 0 != STEP_MOTOR_1PHASE_SEQ[rCurrentPos[0]%PHASE_SEQ_COUNT][pin] else False))
        rCurrentPos[0] = (rCurrentPos[0] + Dir);
        AbsDist = AbsDist - 1;
        time.sleep(TargetFreq)   

#------------------------------------------------
# Convey Init Setting
#------------------------------------------------
ConveyPos = [0];
CONVEY_FREQ = 0.003;
aCONVEY_MOTOR_PIN = [12, 16, 20, 21];
MAX_DIST = 2147483647;

InitMotor(aCONVEY_MOTOR_PIN);

def ConveyMotorStart():
    global ConveyPos, CONVEY_FREQ, aCONVEY_MOTOR_PIN;
    RelMoveMotor(MAX_DIST, CONVEY_FREQ, aCONVEY_MOTOR_PIN, ConveyPos);
    
#------------------------------------------------
# Tongue Init Setting
#------------------------------------------------
TonguePos = [0];
TONGUE_FREQ = 0.003;
aTONGUE_MOTOR_PIN = [14, 15, 23, 24];
TONGUE_SWING_ANGLE = 30.0; #+/-15 Degree Angle

InitMotor(aTONGUE_MOTOR_PIN);
 
def TongueMotorStart():
    SwingDir = 0;
    global TonguePos, aTONGUE_MOTOR_PIN;
    RelMoveMotor(TONGUE_SWING_ANGLE - ONE_TURN_DEGREE*TonguePos[0]/ONE_TURN_PULSE, TONGUE_FREQ, aTONGUE_MOTOR_PIN, TonguePos);
    while False == BattleStop:
        time.sleep(0.2);
        RelMoveMotor((-2 if 0 == SwingDir%2 else 2)*TONGUE_SWING_ANGLE, TONGUE_FREQ, aTONGUE_MOTOR_PIN, TonguePos);
        SwingDir += 1;

TongueThread = threading.Thread(target=TongueMotorStart, daemon=True);
ConveyThread = threading.Thread(target=ConveyMotorStart, daemon=True);

def BattleButtonClick():
    global BattleStop, TongueThread, ConveyThread;
    TongueThread.start();
    ConveyThread.start();
    
def StopButtonClick():
    global BattleStop, TongueThread, ConveyThread;
    BattleStop = True;
    TongueThread.join();
    ConveyThread.join();
    
def InitButtonClick():
    global TonguePos, ONE_TURN_PULSEONE_TURN_DEGREE, PosEditBox;
    TonguePos[0] = int(ONE_TURN_PULSE*float(PosEditBox.get())/ONE_TURN_DEGREE);

CameraImage = tkinter.PhotoImage(file="NoCamera.png");
BattleButton = tkinter.Button(MainWindow, text="Battle Start", command=BattleButtonClick)
StopButton = tkinter.Button(MainWindow, text="Battle Stop", command=StopButtonClick)
InitButton = tkinter.Button(MainWindow, text="Init Tongue Position", command=InitButtonClick)
PosEditBox = tkinter.Entry(MainWindow, width=12, textvariable="0.0");
CameraLabel = tkinter.Label(MainWindow, image=CameraImage)

CameraLabel.place(x=0, y=0, width=1280, height=960)
BattleButton.place(x=0, y=965, width=300, height=50)
StopButton.place(x=350, y=965, width=300, height=50)
InitButton.place(x=750, y=965, width=300, height=50)
PosEditBox.place(x=1050, y=965, width=200, height=50)

def update_data():
    global CameraLabel, CameraImage;
    Capture = cv2.VideoCapture(0);
    Capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
    Capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 960);
    
    Result, Frame = Capture.read();
    if Result :
        RgbImage = Image.fromarray(cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB));
        CameraImage = ImageTk.PhotoImage(image=RgbImage);
        CameraLabel.configure(image=CameraImage);
    Capture.release();
    MainWindow.after(10, update_data)

MainWindow.after(10, update_data)
MainWindow.mainloop();

BattleStop = True;
time.sleep(1);
