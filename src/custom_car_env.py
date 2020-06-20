import gym
import rospy
import roslaunch
import time
import numpy as np

from gym import utils, spaces
from gym_gazebo.envs import gazebo_env
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from nav_msgs.msg import Odometry

from sensor_msgs.msg import LaserScan

from gym.utils import seeding

from gym.envs.registration import register

reg = register(
	id='CustomCar-v0',
	entry_point='custom_car_env:CustomCarEnv',
	max_episode_steps = 300,
)

class CustomCarEnv(gazebo_env.GazeboEnv):

    def __init__(self):
        # Launch the simulation with the given launchfile name
        #gazebo_env.GazeboEnv.__init__(self, "GazeboCircuitTurtlebotLidar_v0.launch")
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=5)
        self.unpause = rospy.ServiceProxy('/gazebo/unpause_physics', Empty)
        self.pause = rospy.ServiceProxy('/gazebo/pause_physics', Empty)
        self.reset_proxy = rospy.ServiceProxy('/gazebo/reset_simulation', Empty)

        self.action_space = spaces.Discrete(3) #F,L,R
        self.reward_range = (-np.inf, np.inf)

        self._seed()
	self.flag = False

    def discretize_observation(self,data,laserdata,new_ranges):
	self.flag = False
        discretized_ranges = []
	
	discretized_ranges.append(int(data.pose.pose.position.x*10))
	discretized_ranges.append(int(data.pose.pose.position.y*10))

        min_range = 0.65
        done = False
        mod = len(data.ranges)/new_ranges
        for i, item in enumerate(data.ranges):
            if (i%mod==0):
                if data.ranges[i] == float ('Inf'):
                    discretized_ranges.append(5)
                elif np.isnan(data.ranges[i]):
                    discretized_ranges.append(0)
                else:
                    discretized_ranges.append(int(data.ranges[i]))
            if (min_range > data.ranges[i] > 0):
                done = True
		print("Too close")
	
	if(-71 < discretized_ranges[0] < -53 and -6 < discretized_ranges[1] < 9):
		done = True
		self.flag = True
		print "Goal reached !"

	return discretized_ranges,done

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):

        rospy.wait_for_service('/gazebo/unpause_physics')
        try:
            self.unpause()
        except (rospy.ServiceException) as e:
            print ("/gazebo/unpause_physics service call failed")

        if action == 0: #FORWARD
            vel_cmd = Twist()
            vel_cmd.linear.x = 0.3
            vel_cmd.angular.z = 0.0
            self.vel_pub.publish(vel_cmd)
        elif action == 1: #LEFT
            vel_cmd = Twist()
            vel_cmd.linear.x = 0.08
            vel_cmd.angular.z = 0.8
            self.vel_pub.publish(vel_cmd)
        elif action == 2: #RIGHT
            vel_cmd = Twist()
            vel_cmd.linear.x = 0.08
            vel_cmd.angular.z = -0.8
            self.vel_pub.publish(vel_cmd)

	laserdata = None
	data = None
	
        while data is None:
            try:
                data = rospy.wait_for_message('/odom', Odometry, timeout=5)
            except:
                pass

	while laserdata is None:
            try:
                laserdata = rospy.wait_for_message('/kinect/scan', LaserScan, timeout=5)
            except:
                pass

        rospy.wait_for_service('/gazebo/pause_physics')
        try:
            #resp_pause = pause.call()
            self.pause()
        except (rospy.ServiceException) as e:
            print ("/gazebo/pause_physics service call failed")

        state,done = self.discretize_observation(data,laserdata,5)
	
        if not done:
            if action == 0:
                reward = 5
            else:
                reward = 1
        else:
	    if self.flag:
		reward = 5000
	    else:
            	reward = -200

	reward += -1 #living reward
        return state, reward, done, {}

    def reset(self):

        # Resets the state of the environment and returns an initial observation.
        rospy.wait_for_service('/gazebo/reset_simulation')
        try:
            #reset_proxy.call()
            self.reset_proxy()
        except (rospy.ServiceException) as e:
            print ("/gazebo/reset_simulation service call failed")

        # Unpause simulation to make observation
        rospy.wait_for_service('/gazebo/unpause_physics')
        try:
            #resp_pause = pause.call()
            self.unpause()
        except (rospy.ServiceException) as e:
            print ("/gazebo/unpause_physics service call failed")

        #read laser data
	laserdata = None
	#read position
        data = None
	
        while data is None:
            try:
                data = rospy.wait_for_message('/odom', Odometry, timeout=1)
            except:
                pass

	while laserdata is None:
            try:
                laserdata = rospy.wait_for_message('/kinect/scan', LaserScan, timeout=1)
            except:
                pass
	
        rospy.wait_for_service('/gazebo/pause_physics')
        try:
            #resp_pause = pause.call()
            self.pause()
        except (rospy.ServiceException) as e:
            print ("/gazebo/pause_physics service call failed")

        state = self.discretize_observation(data,laserdata,5)

        return state
