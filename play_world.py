from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import ActorNode
from panda3d.core import WindowProperties, NodePath, LVector3
from panda3d.core import LineSegs, OrthographicLens, CardMaker
from inputs import Inputs
from sys import path
try:
    path.insert(1, '../pydaq')
    import pydaq
except ImportError:
    pydaq = None


class PlayWorld(object):
    def __init__(self, config=None):
        if config is None:
            self.config = {}
            execfile('play_config.py', self.config)
        else:
            self.config = config
        self.reward = None
        print self.config['pydaq']
        if pydaq and self.config.setdefault('pydaq', True) is not None:
            self.reward = pydaq.GiveReward()
        self.reward_count = 0
        # adjustment to speed so corresponds to gobananas task
        # 7 seconds to cross original environment
        # speed needs to be adjusted to both speed in original
        # environment and c_range of colors
        # self.speed = 0.05 * (self.c_range[1] - self.c_range[0])
        # speed is own variable, so can be changed during training.
        self.speed = self.config['speed']

        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 4
        self.max_vel = [500, 500, 0]

        self.base = ShowBase()
        self.base.disableMouse()
        # self.base.setFrameRateMeter(True)
        # assume we are showing windows unless proven otherwise
        if self.config.get('win', True):
            # only need inputs if we have a window
            self.inputs = Inputs(self.base)
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setForeground(True)
            print self.config.get('resolution')
            if self.config.get('resolution'):
                # main window
                props.set_size(int(self.config['resolution'][0]), int(self.config['resolution'][1]))
                # props.set_origin(1920, 0)
                props.set_origin(500, 0)
            else:
                props.set_size(600, 600)
                props.set_origin(400, 50)
            self.base.win.requestProperties(props)
        # print 'background color', self.base.getBackgroundColor()
        # field = self.base.loader.loadModel("../goBananas/models/play_space/field.bam")
        field = self.base.loader.loadModel("../goBananas/models/play_space/round_courtyard.bam")
        field.setPos(0, 0, 0)
        field.reparent_to(self.base.render)
        field_node_path = field.find('**/+CollisionNode')
        field_node_path.node().setIntoCollideMask(0)
        sky = self.base.loader.loadModel("../goBananas/models/sky/sky_kahana2.bam")
        sky.setPos(0, 0, 0)
        sky.setScale(1.6)
        sky.reparentTo(self.base.render)
        windmill = self.base.loader.loadModel("../goBananas/models/windmill/windmill.bam")
        windmill.setPos(-10, 30, -1)
        windmill.setScale(0.03)
        windmill.reparentTo(self.base.render)
        # mountain = self.base.loader.loadModel("../goBananas/models/mountain/mountain.bam")
        # mountain.setScale(0.0005)
        # mountain.setPos(10, 30, -0.5)

        # create the avatar
        self.avatar = NodePath(ActorNode("avatar"))
        self.avatar.reparentTo(self.base.render)
        self.avatar.setPos(0, 0, 1)
        self.avatar.setScale(0.5)
        pl = self.base.cam.node().getLens()
        pl.setFov(60)
        self.base.cam.node().setLens(pl)
        self.base.camera.reparentTo(self.avatar)

        # initialize task variables
        self.frame_task = None
        self.started_game = None
        self.showed_match = None
        self.gave_reward = None

        # initialize and start the game
        self.set_next_trial()

        # print 'end init'

    def start_loop(self):
        # need to get new match
        self.start_play()

    def start_play(self):
        print 'start play'
        # log this
        # print self.base.render.ls()
        self.frame_task = self.base.taskMgr.add(self.game_loop, "game_loop")
        self.frame_task.last = 0  # initiate task time of the last frame

    def game_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        velocity = self.inputs.poll_inputs(LVector3(0))
        self.move_avatar(dt, velocity)
        return task.cont

    def reward_loop(self, task):
        self.reward_count += 1
        if self.reward_count <= self.config['num_beeps']:
            if self.reward:
                # log this
                print 'give a bloody reward already'
                self.reward.pumpOut()
            print 'give reward'
            return task.again
        else:
            self.end_loop()
            return task.done

    def move_avatar(self, dt, velocity):
        # print 'velocity', self.velocity
        self.avatar.setH(self.avatar.getH() - velocity[0] * 1.1)
        move = LVector3(0, velocity[1], 0)
        self.avatar.setPos(self.avatar, move * dt * self.vel_base)

    def give_reward(self):
        # clear the background
        self.base.setBackgroundColor(0.41, 0.41, 0.41)
        print 'give first reward'
        self.reward_count = 1
        if self.reward:
            # log this
            self.reward.pumpOut()
        self.gave_reward = self.base.taskMgr.doMethodLater(self.config['pump_delay'], self.reward_loop, 'reward_loop')

    def end_loop(self):
        print 'end loop'
        # clear avatar map
        # if there is a match set, return to center of color gradient,
        # set new match, if applicable
        self.set_next_trial()

    def set_next_trial(self):
        print 'set next trial'
        # move avatar back to beginning position, only matters for
        # showing card for next color match
        # self.avatar.set_pos(-10, -10, 2)
        # start the game
        self.start_loop()

    def check_key_map(self):
        if self.config['colors'][0]:
            if self.inputs.key_map['r']:
                self.config['match_direction'] = ['right']
            elif self.inputs.key_map['r'] is not None:
                self.config['match_direction'] = ['left']
        elif self.config['colors'][1]:
            if self.inputs.key_map['f']:
                self.config['match_direction'] = ['front']
            elif self.inputs.key_map['f'] is not None:
                self.config['match_direction'] = ['back']

    def setup_display2(self, display_node):
        print 'setup display2'
        props = WindowProperties()
        props.set_cursor_hidden(True)
        props.set_foreground(False)
        if self.config.get('resolution'):
            props.setSize(700, 700)
            props.setOrigin(-int(self.config['resolution'][0] - 5), 5)
        else:
            props.setSize(300, 300)
            props.setOrigin(10, 10)
        window2 = self.base.openWindow(props=props, aspectRatio=1)
        lens = OrthographicLens()
        lens.set_film_size(2, 2)
        lens.setNearFar(-100, 100)
        self.render2d = NodePath('render2d')
        self.render2d.attach_new_node(display_node)
        camera2d = self.base.makeCamera(window2)
        camera2d.setPos(0, -10, 0)
        camera2d.node().setLens(lens)
        camera2d.reparentTo(self.render2d)


if __name__ == "__main__":
    CW = PlayWorld()
    CW.base.run()
