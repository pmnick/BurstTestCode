import RPi.GPIO as GPIO
from time import sleep
from Tkinter import *
import math
import time
import numpy as np
import spidev
from datetime import datetime, timedelta
import sys

#this is a test web edit

#To Do
## Add diagram with labels (insert image and overlay like Mark did)
## Add label for maxPressure
## Ask for sample name at end and append to file name so data doesn't get overwritten
##      Look at how Mark already implemented this and pull that in
## Check math on flow and pressure sensor (callibrate the pressure sensor
## maybe produce a real time plot of flow vs. pressure (every 1 second take a snapshot of
##      flow and pressure and plot it.  After enough data, we could bake in an expected curve
##      and it would show a quick comparison of actual vs. expected. This could help us see
##      deviations very quickly.
#______________________________________________________________________________________________________________________
#----------------------------------------------------------------------------------------------------------------------

#this is a test for mark                                                                                                                                                                                                                         

print("start")
#Setting up Spi to read ADC
spi_0 = spidev.SpiDev()
spi_0.open(0, 0)  #the second number indicates which SPI pin CE0 or CE1
#to_send = [0x01,0x02,0x03] # speed Hz,Delay, bits per word
#spi_0.xfer(to_send)

#Setting up Global Variables
ForwardFlowCount = 0.0
oldForwardFlowCount= 0.0
forwardflow = 0.0
StartTime = datetime.now()
samplePeriod = 100  #milliseconds, time between data points written to txt file
minimumtime = 1000
destination = "/home/pi/Desktop/Data/AutosavedData.txt"
a=open(destination,'w') #a means append to existing file, w means overwrite old data
a.write("\n\n"+ str(datetime.now()))
Average = 3 # taking 15 samples per second average of 15 will average over one second
flowshow = 0.0
Diffshow= 0.0
maxPressure = 1.0


#Setting up GUI
class popupWindow(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.l=Label(top,text="Set Value")
        self.l.pack()
        self.e=Entry(top)
        self.e.pack()
        self.b=Button(top,text='Done',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()

class mainWindow(object):
    def __init__(self,master):
        self.master=master

root = Tk()
root.title("Backwash Control")

#----initializing GUI------------------
##background_image = PhotoImage(file='/home/pi/Desktop/Code/background.gif')
##w=background_image.width()
##h=background_image.height() 
C = Canvas(root, bg='#333',height=400,width=1200) #<------- i changed heigt and width... need updating
C.focus_set() # Sets the keyboard focus to the canvas
DL= StringVar()
DL.set('0')
differential_label = Label(C, textvariable=DL, padx=5)
differential_label.place(x=400,y=200)
Flowrate_text = Label(C, text='Flow Rate:', padx=5,pady=3)
Flowrate_text.place(x=418,y=89)
##Flowrate_text2 = Label(C, text='Flow Rate:', padx=5,pady=3)
##Flowrate_text2.place(x=418,y=274)
FRL= StringVar()
FRL.set('0')
Flowrate_label = Label(C, textvariable=FRL,pady=3)
Flowrate_label.place(x=489,y=89)
Filtrate_text = Label(C,text='Liters:', padx=5)
Filtrate_text.place(x=760,y=320)
FL= StringVar()
FL.set('0')
Filtrate_label = Label(C, textvariable=FL, padx=5)
Filtrate_label.place(x=805,y=320)
frame=Frame(root)
frame.pack(anchor=NW)


#--- Graph settings
screenWidth = 450
resolution = 1 #number of pixels between data points, for visual purposes only
timeRange = .5 #minutes
baseTime = int(timeRange*60*1000/screenWidth)
x0Coords = []
y0Coords = []
xy0Coords = []
FlowrateAvg = []
##BackflowAvg = []
##FPumpAvg = []
##BPumpAvg = []
DiffAvg = []

coordLength = int(screenWidth/resolution)
#---initiation of lists
for i in range(0,coordLength):
    x0Coords.append(i*resolution)
    y0Coords.append(249)
    xy0Coords.append(0)
    xy0Coords.append(0)
for i in range(0,Average):
    FlowrateAvg.append(0.0)
##    BackflowAvg.append(0)
##    FPumpAvg.append(ForwardPumpTarget)
##    BPumpAvg.append(BackwashPumpTarget)
    DiffAvg.append(0)
    
#putting X and Y corrdinites in a list
def coordinate():
    global x0Coords, y0Coords, xy0Coords
    for i in range(0,coordLength*2,2):
        xy0Coords[i] = x0Coords[i/2]
        xy0Coords[i+1] = y0Coords[i/2]
#---End initiation of lists

Graph= LabelFrame(root, text="Flow Graph",height=250,width=screenWidth)
Graph.pack()
GraphC=Canvas(Graph, bg = "gray", height = 249, width = screenWidth-1)
maxP = GraphC.create_rectangle(0,0,20,50)
cl0 = GraphC.create_line(xy0Coords,smooth=True)
##ctar = GraphC.create_line(0,(249-FlowTarget*20),450,(249-FlowTarget*20), fill='red')
scale5 = Label(GraphC, text=' 100-', bg = "gray")
scale5.place(x=0,y=(240-20*12))
scale7 = Label(GraphC, text=' 90-', bg = "gray")
scale7.place(x=0,y=(240-18*12))
scale9 = Label(GraphC, text=' 80-', bg = "gray")
scale9.place(x=0,y=(240-16*12))
scale11 = Label(GraphC, text=' 70-', bg = "gray")
scale11.place(x=0,y=(240-14*12))
scale12 = Label(GraphC, text=' 60-', bg = "gray")
scale12.place(x=0,y=(240-12*12))
scale10 = Label(GraphC, text=' 50-', bg = "gray")
scale10.place(x=0,y=(240-10*12))
scale8 = Label(GraphC, text=' 40-', bg = "gray")
scale8.place(x=0,y=(240-8*12))
scale6 = Label(GraphC, text=' 30-', bg = "gray")
scale6.place(x=0,y=(240-6*12))
scale4 = Label(GraphC, text=' 20-', bg = "gray")
scale4.place(x=0,y=(240-4*12))
scale2 = Label(GraphC, text=' 10-', bg = "gray")
scale2.place(x=0,y=(240-2*12))
scale0 = Label(GraphC, text=' 0-', bg = "gray")
scale0.place(x=0,y=(240-0*20))

#setting up GPIO pins                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
ForwardFlow = 21
on = GPIO.LOW
off = GPIO.HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ForwardFlow, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Generally reads LOW


#----------------------Function Definitons--------------------------------

def readadc_0(adcnum_0): #this fucntion can be used to find out the ADC value on ADC 0
    if adcnum_0 > 7 or adcnum_0 < 0:
        return -1

    r_0 = spi_0.xfer2([1, 8 + adcnum_0 << 4, 0]) #start bit, Single/Differential mode, Don't care bit OR
    adcout_0 = ((r_0[1] & 3) << 8) + r_0[2]
    return adcout_0

##def readadc_0diff(adcnum_0): #this fucntion can be used to find out the differential ADC value between two chanels on ADC 0
##    if adcnum_0 > 7 or adcnum_0 < 0:
##        return -1
##    r_0 = spi_0.xfer2([1, adcnum_0 << 4, 0]) #start bit, Single/Differential mode, Don't care bit OR
##    adcout_0 = ((r_0[1] & 3) << 8) + r_0[2]
##    return adcout_0

def callback_fflow(ForwardFlow):
    global ForwardFlowCount
    ForwardFlowCount+=1

#shifts y values down in index in array to represent time moved forward
def shiftCoords(nextValue):

    global y0Coords, xy0Coords
    y0Coords.pop(0)
    y0Coords.append(int(nextValue))
    coordinate()

#updates the GUI based on the new time
def move_time():
    global maxP,cl0,xy0Coords,resolution,baseTime,forwardflow,Diffshow,maxPressure
    GraphC.delete(maxP)
    GraphC.delete(cl0)
    if maxPressure < Diffshow:
        maxPressure = Diffshow
    maxP = GraphC.create_rectangle(0,250,480,249-int(maxPressure*250/100), outline="red") #why dividing backwashflow?? <--------------------------
    shiftCoords(249-(Diffshow*250/100))
    cl0 = GraphC.create_line(xy0Coords)
    #print(float(readadc_0(0))/1023*250)
    #title="V= " , str(round(3.3*float(readadc_0(2)-readadc_0(0))/1023,2)) , str(round(3.3*float(readadc_0(2))/1023,2)), str(round(3.3*float(readadc_0(0))/1023,2))
    #root.title(title)
    root.after(baseTime*resolution,move_time)

       
def writeData(): 
    global destination,Diffshow,samplePeriod,ForwardFlowCount,oldForwardFlowCount,forwardflow,FlowrateAvg,flowshow

    ##Calibration of sensor: Real Pressure = reading-(-1.06+.1007xreading)

    Reading = (3.3*float(readadc_0(1)-readadc_0(0))/1023)*100
    DifferentialPressure=round(Reading-(-1.06+.1007*Reading),1)
    DiffAvg.pop(0)
    DiffAvg.append(DifferentialPressure)
    Diffshow=np.mean(DiffAvg)
    DL.set(str(round(Diffshow,1)))
    
     
    forwardflow=((ForwardFlowCount-oldForwardFlowCount)/samplePeriod)*60 #60 is a conversion factor to convert the flowrate from pulses per 100miliseconds to liters per minute
    FlowrateAvg.pop(0)
    FlowrateAvg.append(forwardflow)
    flowshow = np.mean(FlowrateAvg)
    FRL.set(str(round(flowshow,1)))
    FL.set(str(round(ForwardFlowCount/1000,1)))
    data = str(round(Diffshow,1)) + "\t" + str(round(flowshow,1))
    a.write("\n"+ str(datetime.now()) + ", " + str(data))
    oldForwardFlowCount=ForwardFlowCount
##    oldBackwashFlowCount=BackwashFlowCount
    root.after(samplePeriod,writeData)

def callback_end(event):
    global FlowCount, StartTime
    # GPIO.cleanup()#i think this would get get rid of the draining process
    print("max pressure was: " + str(maxPressure))
    a.write("\n" + str("Max Pressure was: ") + str(maxPressure))
    spi_0.close()
    a.close()
    quit()

#Setting up event detection
GPIO.add_event_detect(ForwardFlow, GPIO.RISING, callback=callback_fflow)

#----------------------------------Main loop----------------------------------------


C.bind("<End>",callback_end)
C.pack()
GraphC.pack(anchor=CENTER)
root.after(baseTime,move_time)
root.after(samplePeriod,writeData)
m=mainWindow(root)
root.mainloop()
