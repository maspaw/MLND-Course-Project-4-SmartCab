# -*- coding: utf-8 -*-
import random
import os
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import math

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # TODO: Initialize any additional variables here
        self.q = {}

        self.learningRate = 0.5
        self.epsilon = 1.0
        self.discountFactor = 0.2
        self.actions = [None, 'forward', 'left', 'right']

        self.trip = 0


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.epsilon = self.epsilon - 0.03
        #self.learningRate = self.learningRate - 0.01
        self.minusReward = 0
        self.lastReward = 0
        # print "self.epsilon is {}".format(self.epsilon)]
        # print self.q 

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state

        light = inputs['light']
        oncoming = inputs['oncoming']
        left = inputs['left']


        if light == 'green' :
            straight = True
        else :
            straight = False

        if light =='green' and oncoming != 'forward':
            left = True
        else :
            left = False


        if light =='green' or (light == 'red' and (oncoming != 'left' or left == 'straight')) :
            right = True
        else :
            right = False

        self.state = (left,right,straight,self.lastReward)

        # TODO: Select action according to your policy
        s = ""
        if random.random() < self.epsilon : # Exploration
            action = random.choice(self.actions)
        else : # Use from q table
            s = '*'
            qValueList = []
            actionList = []
            for a in self.actions :
                value = self.q.get((self.state,a),1.0)
                if value > 0 :
                    qValueList.append(value)
                    actionList.append(a)

            #Remove None action if there are other way to go
            #if len(actionList) > 1 :
#                idx = actionList.index(None)
#                qValueList.remove(qValueList[idx])
#                actionList.remove(None)
                
                
            maxQ = max(qValueList)
            best = []
            for i in range(len(actionList)) :
                if qValueList[i] == maxQ :
                    best.append(i)
            action = actionList[random.choice(best)]

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.lastReward = reward

        if action != None :
            reward = reward * 2
        if reward < 0 :
            self.minusReward = self.minusReward + 1

        # TODO: Learn policy based on state, action, reward
        oldValue = self.q.get((self.state, action),None) 
        if oldValue == None :
            oldValue = 1.0
            nextQvalue = reward
        else :
            nextQvalue = reward + self.discountFactor * oldValue

        self.q[(self.state, action)] = (1-self.learningRate)*oldValue + self.learningRate * nextQvalue
        #print s + "Reward = {} update from {} to {} {}".format(reward,oldValue,self.q[(self.state, action)],action)
        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""
    #os.chdir('/Users/paw/Documents/MyProject/MLND/P4/smartcab')
    print os.getcwd()
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.5)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
