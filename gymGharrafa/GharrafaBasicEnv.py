from .assets import set_sumo_home

import logging
import os
from time import sleep
import string
import random
import time

import numpy as np

import gym
from gym import spaces,error

import traci

module_path = os.path.dirname(__file__)

class GharrafaBasicEnv(gym.Env):
    def __init__(self):

        self.tlsID = "6317"
        self._seed = 31337

        self.PHASES = {
        0: "G E",
        1: "G N",
        2: "G W",
        3: "G S",
        4: "ALL RED",
        5: "G EW",
        6: "G NS",
        7: "G E BY W",
        8: "G N BY S",
        9: "G S BY N",
        10: "G W BY E"
        }

        self.DETECTORS = []
        with open(module_path +"/assets/gharrafa_detectors") as fdet:
            for detname in fdet:
                self.DETECTORS.append(detname[:-1])

        #how many SUMO seconds before next step (observation/action)
        self.OBSERVEDPERIOD = 5
        self.SUMOSTEP=1

        #In this version the observation space is the set of sensors
        self.observation_space = spaces.Box(low=0, high=255, shape=(1,68), dtype=np.float32)

        #Set action space as the set of possible phases
        self.action_space = spaces.Discrete(11)

        #Generate an alphanumerical code for the run label (to run multiple simulations in parallel)
        self.runcode = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

        self._configure_environment()



    def _configure_environment(self):
        sumoBinary = set_sumo_home.sumoBinary

        traci.start([sumoBinary, "-c", module_path+"/assets/tl.sumocfg",
                             "--log", "simul_log",
            "--step-length", str(self.SUMOSTEP), "-S", "--time-to-teleport", "-1", "--window-size", "1034,1766"],label=self.runcode)

        self.conn = traci.getConnection(self.runcode)

        time.sleep(5) # Wait for server to startup

    def __del__(self):
        self.conn.close()

    def _selectPhase(self,target):
        target = self.PHASES[target]
        current_program = self.conn.trafficlight.getProgram(self.tlsID)
        if " to " in current_program:
            source = current_program.split(" to ")[1]
        else:
            #we are in another program like scat or 0... just change from N
            source = "G N"
        if source == target and " to " in current_program:
            #ensure that the phase will not be changed automatically by the
            #program, by adding some time
            self.conn.trafficlight.setPhaseDuration(self.tlsID,60.0)
            return False
        else:
            transition_program = "from %s to %s" % (source,target)
            self.conn.trafficlight.setProgram(self.tlsID, transition_program)
            return True

    def _observeState(self):
        timestep = self.conn.simulation.getCurrentTime()/1000
        for i in range(self.OBSERVEDPERIOD):
            self.conn.simulationStep()
            timestep = self.conn.simulation.getCurrentTime()/1000

        lastVehiclesVector = [self.conn.inductionloop.getLastStepVehicleNumber(detID) for detID in self.DETECTORS]

        obs = lastVehiclesVector

        #TODO: build observation
        return obs

    def _step(self, action):
        self._selectPhase(action)

        #get state
        obs = self._observeState()

        #build reward
        reward = 0

        #detect game over state
        episode_over = True

        return obs, reward, episode_over, {}

    def _reset(self):
        #go back to the first step of the return

        return self._observeState()
