import time
import math
import sys
#sys.path.append("Lib")
import json
from java.lang import System
from nu.pattern import OpenCV
from java.io import FileReader
from java.lang import String
OpenCV.loadShared()
from sikuli import *
from org.opencv.core import Mat, Scalar, Core, CvType, Size, MatOfPoint
from org.opencv.imgcodecs import Imgcodecs
from org.opencv.imgproc import Imgproc
from java.awt.image import BufferedImage
from javax.swing import JFrame
from java.awt import Color
print("Loaded Imports")
Settings.MoveMouseDelay = 0.01
Settings.ActionLogs=0
Debug.on(3)
data = None
try:
    with open('PyQt5Version\macro.sikuli\data.json', 'r') as file:
        data = json.load(file)
except Exception as e:
    print("Error:",e)
#How much time you want for the next shake. Ex. how much time you think will take to catch
TimeEachLoop = 5
Latency = data["ShakeSpeed"] # this is if ur computer is very laggy, mine is so it is half a second for each shake
ShakeEnabled = data["ShakeEnabled"] # Enable if you have hasty enchant
ClickShake = True
running = True      
#COLORS FOR FISCH DETECTION (WHITE_BAR, GREY_FISH_BAR)
Sets = {
    "Color_Fish" : {"0x434b5b": 3, "0x4a4a5c": 4, "0x47515d": 4},  
    "Color_White" : {"0xFFFFFF": 15}, 
    "Color_Bar" : {"0x848587": 4, "0x787773": 4, "0x7a7873": 4}
}
isShaking = False
isCatching = False
def runHotKey(event):
    global running
    print("pressedhotkey")
    running = False
#In this case, this is CTRL+X which is if you want to stop the program (stop after any sequence, not in between)
Env.addHotkey("x",KeyModifier.CTRL,runHotKey)    
r = switchApp("Roblox")
ch = App("Roblox")
#SCALING SIZES FOR COMPATIBILITY
RobloxWindowRegion = Region(App("Roblox").focusedWindow())
ReferenceResolution = [1440,875]
UR = [RobloxWindowRegion.w,RobloxWindowRegion.h]
sf = [float(UR[0])/1920.0,float(UR[1])/1200.0]
#REGIONS:
print(UR[0], UR[1])
print(sf[0],sf[1])
#mainfactor = math.sqrt((float(UR[0]) * float(UR[1])) / (1920 * 1200))
#print(mainfactor)

#Settings.AlwaysResize = mainfactor
ReelingRegion = Region(int(561.0*sf[0]),int(1027.0*sf[1]),int(807.0*sf[0]),int(3.0*sf[1]))
print("NOTE***YOUR RESOLUTION MUST BE 1920x1200 FOR THIS TO WORK! IF NOT, SELECT A BIGGER RESOLUTION AND SCALE THE ROBLOX WINDOW TO 1440x900")
#DETERMINE YOUR RESOLUTION HERE:
#NOTE* FOR USERS WITH A 1440x900 RESOLUTION, 1440x875 IS JUST NO FULLSCREEN BUT FILLS ENTIRE SCREEN
#Process
def create_overlay(color, width=20, height=35):
    frame = JFrame()
    frame.setSize(width, height)
    frame.setUndecorated(True)
    frame.setAlwaysOnTop(True)
    frame.getContentPane().setBackground(color)
    frame.setVisible(True)
    return frame
def find_bar_by_length(region, expected_width, tolerance=10):
    screen = Screen()
    try:
        captured_image = screen.capture(region)
        buffered_image = captured_image.getImage()
        height = buffered_image.getHeight()
        width = buffered_image.getWidth()

        mat_image = Mat(height, width, CvType.CV_8UC3)
        raster = buffered_image.getRaster()
        for x in range(width):
            for y in range(height):
                r, g, b = raster.getPixel(x, y, None)[:3]
                data = [float(b), float(g), float(r)]
                mat_image.put(y, x, data)

        gray = Mat()
        Imgproc.cvtColor(mat_image, gray, Imgproc.COLOR_BGR2GRAY)


        thresh = Mat()
        Imgproc.threshold(gray, thresh, 200, 255, Imgproc.THRESH_BINARY)

        contours = java.util.ArrayList()
        hierarchy = Mat()
        Imgproc.findContours(thresh, contours, hierarchy, Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE)

        best_bar = None
        min_diff = float("inf")


        for contour in contours:
            rect = Imgproc.boundingRect(contour)
            rect_width = rect.width

            if abs(rect_width - expected_width) <= tolerance:
                diff = abs(rect_width - expected_width)
                if diff < min_diff:
                    min_diff = diff
                    best_bar = rect

        if best_bar:
            absolute_x = region.x + best_bar.x + (best_bar.width // 2)  # Get center X
            absolute_y = region.y + best_bar.y + (best_bar.height // 2)  # Get center Y
            return absolute_x, absolute_y, best_bar.width  # Returning the width to confirm detection

        print("No matching bar found!")
        return 0, 0, 0

    except Exception as e:
        print("Error in bar detection: ",e)
        return 0, 0, 0
def find_color(color_lower, color_upper, region, isBar_X=False): 
    screen = Screen()
    try:
        captured_image = screen.capture(region)
        buffered_image = captured_image.getImage()   
        height = buffered_image.getHeight() 
        width = buffered_image.getWidth()
        
        mat_image = Mat(height, width, CvType.CV_8UC3)
        raster = buffered_image.getRaster()
        for x in range(width):
            for y in range(height):
                r,g,b = raster.getPixel(x,y,None)[:3]
                data = [float(b),float(g),float(r)]
                mat_image.put(y,x,data)
        lower_bound = Scalar(color_lower[0], color_lower[1], color_lower[2])
        upper_bound = Scalar(color_upper[0], color_upper[1], color_upper[2])
        mask = Mat()
        Core.inRange(mat_image, lower_bound, upper_bound, mask)
        pts = MatOfPoint()
        Core.findNonZero(mask, pts)
        detectedlocation = []
        if isBar_X:
            if pts.rows()>0:
                point = pts.toList()[0]
                x, y = float(point.x), float(point.y)   
                absolute_x = region.x + x
                absolute_y = region.y + y          
                return int(absolute_x), int(absolute_y)
            else:
                print("No pixel of color in range!")
        if pts.rows()>0:
            point = pts.toList()[0]
            x, y = float(point.x), float(point.y)   
            absolute_x = region.x + x
            absolute_y = region.y + y          
            return int(absolute_x), int(absolute_y)
        else:
            print("No pixel of color in range!")
            #i have to make my own function and meanwhile ahk has this already
            
    except Exception as e:
        print("it did NOT work: {}".format(e))
    return 0,0
def search(target, region, isBar_x=False):
    timeNow = time.time()
    for color_hex, variation in target.items():
        color_rgb = (
            int(color_hex[2:4], 16),  # R
            int(color_hex[4:6], 16),  # G
            int(color_hex[6:], 16)   # B
        )
        
        lower_bound = (
            max(0, color_rgb[2] - variation),
            max(0, color_rgb[1] - variation),
            max(0, color_rgb[0] - variation)
        )
        upper_bound = (
            min(255, color_rgb[2] + variation),
            min(255, color_rgb[1] + variation),
            min(255, color_rgb[0] + variation)
        )
        if not isBar_x:
            x,y = find_color(lower_bound, upper_bound, region)
        else:
            x,y = find_color(lower_bound, upper_bound, region, True)
        if x != 0:
            print("TIME ELAPSED: {:.2f} ms".format((time.time()-timeNow)*1000))
            print("----------------- FOUND PIXEL! -------------------")
            return x,y
    return 0,0

def timeToHold(pixel,scale_factor):
    data = [
        [0, 0], [16, 0], [54, 75], [132, 125], [217, 180], [365, 280], [450, 320], 
        [534, 375], [632, 440], [736, 500], [817, 600], [900, 700], 
        [997, 770], [1081, 835], [1164, 900], [1250, 2200], 
        [1347, 2400], [1448, 2600], [1531, 2800], [1531, 9999]
    ]
    
    for pair in data:
        pair[0] = int(pair[0] * scale_factor)
    
    lower = None
    upper = None
    for i in range(len(data)):
        if pixel < data[i][0]:
            lower = data[i - 1]
            upper = data[i]
            break

    if lower is None or upper is None:
        raise ValueError("Pixel value out of range.")

    hold = lower[1] + (pixel - lower[0]) * (upper[1] - lower[1]) / (upper[0] - lower[0])

    print("Hold: {:.2f} ms".format(hold))

    return hold
def Catch():
    start_time = time.time()
    #MaxHold calculation:
    prev_target_x = None
    stationary_start_time = None
    three_quarter_mark = ReelingRegion.x + (ReelingRegion.w * 0.58)
    
    timeout = 1.75
    control = data["Control"]
    result = round((UR[1] / 247.03) * (control * 100) + (UR[1] / 8.2759), 0)
    i = 0
    print("Iteration",i) 
    #Maxhold is to hold until the fish is beyond the control range
    #
    last_valid_target_x = None
    last_valid_bar_x = None
    frame_bar = create_overlay(Color.BLACK)      # Tracks bar_x
    frame_target = create_overlay(Color.WHITE)  
    bar_x = None
    target_x = None
    while True:
        i += 1
        
        print("-----------------TEST-----------------")
        targetbarColor = Sets["Color_Fish"]
        userbarColor = Sets["Color_White"]
        target_x,target_y = search(targetbarColor, ReelingRegion)
        bar_x,bar_y = search(userbarColor, ReelingRegion) 
        #bar_x,bar_y = find_bar_by_length(ReelingRegion, result)

        if target_x != 0:
            frame_target.setLocation(target_x, target_y)
            start_time = time.time()
            last_valid_target_x = target_x 
        if target_x == 0 and last_valid_target_x is not None:
            target_x = last_valid_target_x
        
        if bar_x == 0 and last_valid_bar_x is not None:
            bar_x = last_valid_bar_x
        if target_x > three_quarter_mark:
            if prev_target_x is not None:
                # Check if the target is stationary (small movement over time)
                if abs(target_x - prev_target_x) < 30:  # Small movement threshold
                    if stationary_start_time is None:
                        stationary_start_time = time.time()
                    # Hold the mouse if stationary for 1 second
                    if time.time() - stationary_start_time >= 1:
                        mouseDown(Button.LEFT)
                        print("Mouse held at 3/4 mark until target moves...")
                else:
                    stationary_start_time = None  # Reset if it's not stationary
            prev_target_x = target_x
        else:
            stationary_start_time = None  # Reset if target moves before 3/4 mark
            mouseUp(Button.LEFT)    
        if bar_x != 0:
            frame_bar.setLocation(int(bar_x),int(bar_y))
            bar_x,bar_y = search(Sets["Color_Bar"], ReelingRegion)
            #bar_x += round(result * 0.5) 
            last_valid_bar_x = bar_x 
        if time.time() - start_time > timeout:
            print("Loop timed out. Exiting...")
            break
        if target_x != 0:
            if target_x > bar_x:
                dist = target_x - bar_x
                print(dist, target_x, bar_x)
                skibidirizz = timeToHold(dist,sf[0])
                mouseDown(Button.LEFT)
                wait(skibidirizz/1000)
                mouseUp(Button.LEFT)
        else:
            print("Target value not found")
    frame_bar.dispose() 
    frame_target.dispose()
    return  
def ClickShake():
    global Latency
    screen = Screen()
    while True: 
        userbarColor = Sets["Color_Fish"]
        x,y = search(userbarColor, ReelingRegion)
        shake = Pattern("better_shake.png").similar(0.50)
        if exists(shake):
            try:  
                click(shake)
            except:         
                wait(Latency)
        elif x != 0:
            print("CATCHING")
            isShaking = False
            return True
        else:
            print("FAILED")
            isShaking = False
            return True
    return True
def NavigationShake():
    global Latency
    userbarColor = Sets["Color_Fish"]
    x,y = search(userbarColor, ReelingRegion)
    screen = Screen()
    while True:
        type(Key.PAGE_DOWN)
        shake = Pattern("better_shake.png").similar(0.50)
        if exists(shake):
            type(Key.ENTER) 
            wait(Latency)
        elif x != 0:
            print("CATCHING")
            return True
        else:
            print("FAILED")
            isShaking = False
            return True
while(running):
    App.focus("Roblox")
    mouseDown(Button.LEFT)
    wait(data["CastDuration"])
    mouseUp(Button.LEFT)
    wait(0.5)
    isShaking = True
    #WARNING: SHAKE ONLY WORKS WITH RESOLUTIONS 1920x1200 AS OF NOW. DONT USE SHAKE UNLESS YOU HAVE THIS RESOLUTION!
    if not ShakeEnabled and ClickShake:
        hasFinishedShake = ClickShake()
    elif not ShakeEnabled and not ClickShake:
        hasFinishedShake = NavigationShake()
    else:
        hasFinishedShake = True
    if hasFinishedShake == True:
        wait(1.5)
        print("User Is Catching...")
        DetectionConsistency = Catch()