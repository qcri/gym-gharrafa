import os
import sys
import optparse
import subprocess
import random
#import pdb; pdb.set_trace()

import set_sumo_home
from sumolib import checkBinary
sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, "-c", "tl.sumocfg", "--start",  "--log", "simul_log"]

import traci

#traci.connect()

traci.start(sumoCmd)

step = 1
start=25200
stop= 33000
for step in range (start,stop,step):
     
      traci.simulationStep()
      #filename="/home/gvantini/Pictures/sumo"+str(step)+".png"
      #traci.gui.screenshot("View #0","/home/gvantini/Pictures/sumo"+str(step)+".png" ,1,1)
  

traci.close()
sys.stdout.flush()

