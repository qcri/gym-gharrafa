import logging
import os
from time import sleep
import numpy as np

import gym
from gym import spaces,error


import set_sumo_home
import traci

class GharrafaBasicEnv(gym.Env):
    def __init__(self):
        self.JUNCTION = "JUNCTIONNAME"

        #how many SUMO seconds before next step (observation/action)
        self.OBSERVEDPERIOD = 5

        #In this version the observation space is the set of sensors
        self.observation_space = spaces.Box(low=0, high=1, shape=(1,8), dtype=np.float32)

        #Set action space as the set of possible phases
        self.action_space = spaces.Discrete(4)

    def __del__(self):
        traci.close()

    def _selectPhase(self,phase):
        current_phase = traci.trafficlight.getPhase(self.JUNCTION)
        if current_phase == phase:
            return False
        else:
            traci.trafficlight.setPhase(self.JUNCTION, phase)
            return True

    def _observeState(self):
        timestep = traci.simulation.getCurrentTime()/1000
        for i in range(self.OBSERVATIONPERIOD):
            traci.simulationStep()
            timestep = traci.simulation.getCurrentTime()/1000

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
