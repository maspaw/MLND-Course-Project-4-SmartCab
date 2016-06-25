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

        self.learningRate = 1.0
        self.epsilon = 1.0
        self.discountFactor = 0.3
        self.actions = [None, 'forward', 'left', 'right']

        self.trip = 0
        self.minusReward = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

        print "last minus reward : {} per {} trip".format(self.minusReward, self.trip)
        
        self.epsilon = self.epsilon - 0.03
        #self.minusReward = 0
        #self.trip = 0
        
        #print self.q

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        

        # TODO: Update state
        self.state = (inputs['light'],inputs['oncoming'],inputs['left'], inputs['right'], self.next_waypoint)

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

            maxQ = max(qValueList)
            best = []
            for i in range(len(actionList)) :
                if qValueList[i] == maxQ :
                    best.append(i)
            action = actionList[random.choice(best)]

        # Execute action and get reward
        reward = self.env.act(self, action)

        self.trip = self.trip + 1
        if reward < 0 :
            self.minusReward = self.minusReward + 1
            #print "agent break traffic rule" + s
            #print self.state
            #print action

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
    #os.chdir('/Users/paw/Documents/MyProject/MLND/P4/smartcab/MLND-Course-Project-4-SmartCab')
    #print os.getcwd()
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.25)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
