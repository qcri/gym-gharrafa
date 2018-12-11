from assets import set_sumo_home

import logging
import os
from time import sleep
import string
import random

import numpy as np

import gym
from gym import spaces,error


import set_sumo_home
import traci

class GharrafaBasicEnv(gym.Env):
    def __init__(self):

        self.tlsID = "6317"

        self.PHASES = {
        0: "G E",
        1: "G N",
        2: "G W",
        3: "G S",
        4: "ALL RED",
        5: "G EW",
        6: "G NS",
        7: "G E BY W"
        8: "G N BY S"
        9: "G S BY N"
        10: "G W BY E"
        }

        self.DETECTORS = []
        with open("./assets/gharrafa_detectors") as fdet:
            for detname in fdet:
                self.DETECTORS.append(detname)

        #how many SUMO seconds before next step (observation/action)
        self.OBSERVEDPERIOD = 5
        self.SUMOSTEP=1

        #In this version the observation space is the set of sensors
        self.observation_space = spaces.Box(low=0, high=1, shape=(1,8), dtype=np.float32)

        #Set action space as the set of possible phases
        self.action_space = spaces.Discrete(4)

        #Generate an alphanumerical code for the run label (to run multiple simulations in parallel)
        self.runcode = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))



    def _configure_environment(self):
        sumoBinary = set_sumo_home.sumoBinary

        traci.start([sumoBinary, "-c", "./asset/tl.sumocfg",
                             "--log", "simul_log",
            "--step-length", str(self.SUMOSTEP), "-S", "--time-to-teleport", "-1", "--window-size", "1034,1766"],label=self.runcode)

        self.conn = traci.getConnection(self.runcode)

        time.sleep(5) # Wait for server to startup

    def __del__(self):
        self.conn.close()

    def _selectPhase(self,target):
        current_program = self.conn.trafficlight.getProgram(self.tlsID)
        source = current_program.split(" to ")[1]
        if source == target:
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
        for i in range(self.OBSERVATIONPERIOD):
            self.conn.simulationStep()
            timestep = self.conn.simulation.getCurrentTime()/1000

        lastMeanSpeedVector = [self.conn.getLastStepVehicleNumber(detID) for detID in self.DETECTORS]:

        obs = ()

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

        return _observeState(self)
