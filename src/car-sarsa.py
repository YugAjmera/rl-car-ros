#!/usr/bin/env python
import gym
from gym import wrappers
import custom_car_env
import gym_gazebo
import time
import numpy
import random
import time
import rospy

import liveplot
import sarsa


if __name__ == '__main__':	

    rospy.init_node('car_gym', anonymous=True)
    env = gym.make('CustomCar-v0')
    print "Gym Make Done"

    outdir = '/tmp/gazebo_gym_experiments'
    env = gym.wrappers.Monitor(env, outdir, force=True)
    print "Monitor Wrapper Started"

    plotter = liveplot.LivePlot(outdir)

    last_time_steps = numpy.ndarray(0)

    sarsa = sarsa.Sarsa(actions=range(env.action_space.n),
                    epsilon=0.1, alpha=0.2, gamma=0.9)

    

    start_time = time.time()
    total_episodes = 50
    

    for x in range(total_episodes):
        done = False

        cumulated_reward = 0 
	print("Episode = " +str(x)+ " started")
        observation = env.reset()

        #render() #defined above, not env.render()

        state = ''.join(map(str, observation))

        i = 0
        #for i in range(300):
	while(True):

            # Pick an action based on the current state
            action = sarsa.chooseAction(state)

            # Execute the action and get feedback
            observation, reward, done, info = env.step(action)
            cumulated_reward += reward


            nextState = ''.join(map(str, observation))
            nextAction = sarsa.chooseAction(nextState)

            #sarsa.learn(state, action, reward, nextState)
            sarsa.learn(state, action, reward, nextState, nextAction)

            env._flush(force=True)

            if not(done):
                state = nextState
            else:
		print("Done a episode")
                last_time_steps = numpy.append(last_time_steps, [int(i + 1)])
                break

	    i = i+1

        if x%1==0:
            plotter.plot(env)

        m, s = divmod(int(time.time() - start_time), 60)
        h, m = divmod(m, 60)
        print ("EP: "+str(x+1)+" - [alpha: "+str(round(sarsa.alpha,2))+" - gamma: "+str(round(sarsa.gamma,2))+" - epsilon: "+str(round(sarsa.epsilon,2))+"] - Reward: "+str(cumulated_reward)+"     Time: %d:%02d:%02d" % (h, m, s))

    #Github table content
    print ("\n|"+str(total_episodes)+"|"+str(sarsa.alpha)+"|"+str(sarsa.gamma)+"|"+str(sarsa.epsilon)+"| PICTURE |")

    l = last_time_steps.tolist()
    l.sort()

    #print("Parameters: a="+str)
    print("Overall score: {:0.2f}".format(last_time_steps.mean()))
    print("Best 100 score: {:0.2f}".format(reduce(lambda x, y: x + y, l[-100:]) / len(l[-100:])))

    env.close()
    plotter.show()
