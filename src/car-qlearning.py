#!/usr/bin/env python
import gym
import rospy
import custom_car_env
from gym import wrappers
import gym_gazebo
import time
import numpy
import random
import time
import liveplot
import qlearn

def render():
    render_skip = 0 #Skip first X episodes.
    render_interval = 50 #Show render Every Y episodes.
    render_episodes = 10 #Show Z episodes every rendering.

    if (x%render_interval == 0) and (x != 0) and (x > render_skip):
        env.render()
    elif ((x-render_episodes)%render_interval == 0) and (x != 0) and (x > render_skip) and (render_episodes < x):
        env.render(close=True)

if __name__ == '__main__':

    rospy.init_node('car_gym', anonymous=True)
    env = gym.make('CustomCar-v0')
    print "Gym Make Done"


    outdir = '/tmp/gazebo_gym_experiments'
    env = gym.wrappers.Monitor(env, outdir, force=True)

    plotter = liveplot.LivePlot(outdir)

    print "Monitor Wrapper Started"
    last_time_steps = numpy.ndarray(0)

    qlearn = qlearn.QLearn(actions=range(env.action_space.n),
                    alpha=0.1, gamma=0.8, epsilon=0.9)

    initial_epsilon = qlearn.epsilon

    epsilon_discount = 0.999 # 1098 eps to reach 0.1

    start_time = time.time()
    total_episodes = 10
    highest_reward = 0

    for x in range(total_episodes):
        done = False

        cumulated_reward = 0 #Should going forward give more reward then L/R ?
        print("Episode = " +str(x))
        observation = env.reset()

        if qlearn.epsilon > 0.05:
            qlearn.epsilon *= epsilon_discount

        state = ''.join(map(str, observation))

        for i in range(100):

            # Pick an action based on the current state
            action = qlearn.chooseAction(state)
            if(action == 0):
		print("Action : Forward")
	    elif(action == 1):
		print("Action : Left")
	    elif(action == 2):
		print("Action : Right")

            # Execute the action and get feedback
            observation, reward, done, info = env.step(action)
            cumulated_reward += reward
            #print("Reward: "+str(reward))

            if highest_reward < cumulated_reward:
                highest_reward = cumulated_reward

            nextState = ''.join(map(str, observation))

            qlearn.learn(state, action, reward, nextState)

            env._flush(force=True)

            if not(done):
                state = nextState
            else:
            	print("Done a episode")
                last_time_steps = numpy.append(last_time_steps, [int(i + 1)])
                break

	if x%1==0:
		plotter.plot(env)


        m, s = divmod(int(time.time() - start_time), 60)
        h, m = divmod(m, 60)
        print ("EP: "+str(x+1)+" - [alpha: "+str(round(qlearn.alpha,2))+" - gamma: "+str(round(qlearn.gamma,2))+" - epsilon: "+str(round(qlearn.epsilon,2))+"] - Reward: "+str(cumulated_reward)+"     Time: %d:%02d:%02d" % (h, m, s))

    #Github table content
    print ("\n|"+str(total_episodes)+"|"+str(qlearn.alpha)+"|"+str(qlearn.gamma)+"|"+str(initial_epsilon)+"*"+str(epsilon_discount)+"|"+str(highest_reward)+"| PICTURE |")

    l = last_time_steps.tolist()
    l.sort()

    #print("Parameters: a="+str)
    print("Overall score: {:0.2f}".format(last_time_steps.mean()))
    print("Best 100 score: {:0.2f}".format(reduce(lambda x, y: x + y, l[-100:]) / len(l[-100:])))
    env.close()
    plotter.show()
