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
    def __init__(self,GUI=True,Play=None,Generate=False):

        self.tlsID = "6317"
        self._seed = 31337

        self.GUI = GUI
        self.Play = Play

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

        self.monitored_edges = ["7552",
        "7553",
        "7554",
        "7556",
        "7558",
        "7560",
        "7562",
        "7563",
        "7565",
        "7574",
        "6043",
        "7593",
        "7594",
        "7621",
        "7623",
        "10324",
        "10339",
        "6124",
        "7665",
        "7542",
        "7673",
        "7547",
        "7548",
        "7549",
        "7550"]

        self.DETECTORS = []
        with open(module_path +"/assets/gharrafa_detectors") as fdet:
            for detname in fdet:
                self.DETECTORS.append(detname[:-1])

        #how many SUMO seconds before next step (observation/action)
        self.OBSERVEDPERIOD = 10
        self.SUMOSTEP = 0.5

        #In this version the observation space is the set of sensors
        self.observation_space = spaces.Box(low=0, high=255, shape=(1,68), dtype=np.uint8)

        #Set action space as the set of possible phases
        self.action_space = spaces.Discrete(11)

        #Generate an alphanumerical code for the run label (to run multiple simulations in parallel)
        self.runcode = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

        self.timestep = 0
        self.rewards = []

        self._configure_environment()



    def _configure_environment(self):

        if self.GUI:
            sumoBinary = set_sumo_home.sumoBinaryGUI
        else:
            sumoBinary = set_sumo_home.sumoBinary

        self.argslist = [sumoBinary, "-c", module_path+"/assets/tl.sumocfg",
                             "--collision.action", "remove",
            "--step-length", str(self.SUMOSTEP), "-S", "--time-to-teleport", "-1",
            "--collision.mingap-factor", "0",
            "--collision.check-junctions", "true", "--no-step-log"]

        if self.Play:
            #self.argslist.append("--game")
            self.argslist.append("--window-size")
            self.argslist.append("1000,1000")

        # if self.GUI:
        #     self.arglist.append("--gui-settings-file")
        #     self.arglist.append(module_path+"/assets/viewsettings.xml")

        traci.start(self.argslist,label=self.runcode)

        self.conn = traci.getConnection(self.runcode)

        time.sleep(5) # Wait for server to startup

    def __del__(self):
        self.conn.close()

    def closeconn(self):
        self.conn.close()

    def _selectPhase(self,target):
        target = self.PHASES[target]
        current_program = self.conn.trafficlight.getProgram(self.tlsID)
        if " to " in current_program:
            source = current_program.split(" to ")[1]
        else:
            #we are in another program like scat or 0... just change from N
            source = "G N"
            if source == target:
                source = "G S"
        if source == target and " to " in current_program:
            #ensure that the phase will not be changed automatically by the
            #program, by adding some time
            self.conn.trafficlight.setPhase(self.tlsID, 1)
            self.conn.trafficlight.setPhaseDuration(self.tlsID,60.0)
            return False
        else:
            transition_program = "from %s to %s" % (source,target)
            self.conn.trafficlight.setProgram(self.tlsID, transition_program)
            return True

    def _observeState(self):
        #selftimestep = self.conn.simulation.getCurrentTime()/1000
        lastVehiclesVector = np.zeros(len(self.DETECTORS),dtype=np.float32)
        reward = 0

        #initialize accumulators for Play mode measures
        ACCgetWaitingTime = 0
        ACCgetTravelTime = 0

        ACCgetLastStepOccupancy = 0
        ACCgetLastStepMeanSpeed = 0
        ACCgetLastStepHaltingNumber = 0

        ACCgetCO2Emission = 0
        ACCgetNOxEmission = 0
        ACCgetHCEmission = 0
        ACCgetNoiseEmission = 0

        ACCgetArrivedNumber = 0
        ACCgetDepartedNumber = 0
        #ACCgetCollidingVehiclesNumber = 0

        measures = {}


        for i in range(int(self.OBSERVEDPERIOD/self.SUMOSTEP)):
            self.conn.simulationStep()
            self.timestep += self.SUMOSTEP #self.conn.simulation.getCurrentTime()/1000
            lastVehiclesVector += np.array([np.float32(self.conn.inductionloop.getLastStepVehicleNumber(detID)) for detID in self.DETECTORS])
            reward += np.sum([self.conn.inductionloop.getLastStepVehicleNumber(detID) for detID in self.DETECTORS if "out_for" in detID])
            if self.Play != None:
                #measure delay,emissions etc. from selected edges
                ACCgetWaitingTime += np.mean([self.conn.edge.getWaitingTime(edgeID) for edgeID in self.monitored_edges])  #must average over micro steps
                ACCgetTravelTime += np.mean([self.conn.edge.getTraveltime(edgeID) for edgeID in self.monitored_edges])  #must average over micro steps

                ACCgetLastStepOccupancy += np.mean([self.conn.edge.getLastStepOccupancy(edgeID) for edgeID in self.monitored_edges])  # must average over micro steps
                ACCgetLastStepMeanSpeed += np.mean([self.conn.edge.getLastStepMeanSpeed(edgeID) for edgeID in self.monitored_edges])  # must average over micro steps
                ACCgetLastStepHaltingNumber += np.mean([self.conn.edge.getLastStepHaltingNumber(edgeID) for edgeID in self.monitored_edges])  # must average over micro steps

                ACCgetCO2Emission += np.sum([self.conn.edge.getCO2Emission(edgeID) for edgeID in self.monitored_edges])  # must sum over micro steps
                ACCgetNOxEmission += np.sum([self.conn.edge.getNOxEmission(edgeID) for edgeID in self.monitored_edges])  # must sum over micro steps
                ACCgetHCEmission += np.sum([self.conn.edge.getHCEmission(edgeID) for edgeID in self.monitored_edges])  # must sum over micro steps
                ACCgetNoiseEmission += np.sum([self.conn.edge.getNoiseEmission(edgeID) for edgeID in self.monitored_edges])  # must sum over micro steps

                ACCgetArrivedNumber += self.conn.simulation.getArrivedNumber()  # must sum over micro steps
                ACCgetDepartedNumber += self.conn.simulation.getDepartedNumber()  # must sum over micro steps
                #ACCgetCollidingVehiclesNumber += self.conn.simulation.getCollidingVehiclesNumber()  # must sum over micro steps

        measures = {
        "WaitingTime" : ACCgetWaitingTime/(i+1),
        "TravelTime" : ACCgetTravelTime/(i+1),

        "Occupancy" : ACCgetLastStepOccupancy/(i+1),
        "MeanSpeed" : ACCgetLastStepMeanSpeed/(i+1),
        "HaltingNumber" : ACCgetLastStepHaltingNumber/(i+1),

        "CO2Emission" : ACCgetCO2Emission,
        "NOxEmission" : ACCgetNOxEmission,
        "HCEmission" : ACCgetHCEmission,
        "NoiseEmission" : ACCgetNoiseEmission,

        "ArrivedNumber" : ACCgetArrivedNumber,
        "DepartedNumber" : ACCgetDepartedNumber,

        "Reward" : reward#,
        #"CollidingVehiclesNumber" : ACCgetCollidingVehiclesNumber
        }

        obs = lastVehiclesVector

        self.rewards.append(reward)
        return obs,reward,measures

    def _step(self, action):
        if self.Play != None and self.Play != "action":
            obs,reward,measures = self._observeState()
            measures["time"] = self.timestep

            #episodic conditions for junction interference
            c1 = self.conn.lane.getLastStepHaltingNumber("7594_2")>10
            c2 = self.conn.lane.getLastStepHaltingNumber("6511_1")>10
            c3 = self.conn.lane.getLastStepHaltingNumber("7673_0")>10
            c4 = self.conn.lane.getLastStepHaltingNumber("6522_1")>10

            #episodic condition of waiting time
            cwait = np.max([self.conn.edge.getWaitingTime(edgeID) for edgeID in self.monitored_edges]) >= 300

            #episodic condition for green idling
            cgreen = len(self.rewards) >= 12 and sum(self.rewards[-6:]) == 0



            return obs, reward, (c1 or c2 or c3 or c4 or cwait or cgreen), measures

        episode_over=False
        self._selectPhase(action)

        #get state and reward
        obs,reward,measures = self._observeState()

        #episodic conditions for junction interference
        c1 = self.conn.lane.getLastStepHaltingNumber("7594_2")>10
        c2 = self.conn.lane.getLastStepHaltingNumber("6511_1")>10
        c3 = self.conn.lane.getLastStepHaltingNumber("7673_0")>10
        c4 = self.conn.lane.getLastStepHaltingNumber("6522_1")>10

        #episodic condition of waiting time
        cwait = np.max([self.conn.edge.getWaitingTime(edgeID) for edgeID in self.monitored_edges]) >= 300

        #episodic condition for green idling
        cgreen = len(self.rewards) >= 12 and sum(self.rewards[-6:]) == 0


        measures["time"] = self.timestep
        #additional = {"time":self.timestep}
        #detect "game over" state
        if self.Play != "action" and (self.timestep >= 3600 or c1 or c2 or c3 or c4 or cwait or cgreen):
        #if self.timestep >= 3600 or c1 or c2 or c3:
            episode_over = True
            self.timestep = 0
            time.sleep(1.0)
            self.conn.load(self.argslist[1:])
            time.sleep(1.0)

        if self.Play == "action" and (self.timestep >= 3600 or c1 or c2 or c3 or c4 or cwait or cgreen):
            episode_over = True

        return obs, reward, episode_over, measures

    def _reset(self):
        self.timestep = 0
        #go back to the first step of the return
        if self.Play != None and self.Play != "action":
            self.conn.trafficlight.setProgram(self.tlsID, self.Play)

        return self._observeState()[0]
