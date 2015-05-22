from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import ActorNode
from panda3d.core import WindowProperties, NodePath, LVector3
from panda3d.core import LineSegs, OrthographicLens, CardMaker
from inputs import Inputs
from sys import path
import square
try:
    path.insert(1, '../pydaq')
    import pydaq
except ImportError:
    pydaq = None


class ColorWorld(object):
    def __init__(self, config=None):
        # keep track of velocity, this allows me to counteract joystick with keyboard
        self.velocity = LVector3(0)
        if config is None:
            self.config = {}
            execfile('config.py', self.config)
        else:
            self.config = config
        self.reward = None
        if pydaq:
            self.reward = pydaq.GiveReward()
        self.reward_count = 0
        # self.color_map always corresponds to (r, g, b)
        # does not change during game, each game uses a particular color space
        self.color_dict = square.make_color_map(self.config['colors'])
        # sets the range of colors for this map
        self.c_range = self.config['c_range']
        # color variables (make dictionary?)
        # color_list is set in beginning, and then after that this is only
        # called again for non-random (training)
        self.color_list = square.set_start_position_colors(self.config)
        self.color_match = [0, 0, 0]
        self.color_tolerance = []
        self.last_avt, self.avt_factor = square.translate_color_map(self.config, self.color_dict, self.color_list)
        print 'starting avt position', self.last_avt
        print 'map avatar factor', self.avt_factor
        self.random = True
        if self.config.get('match_direction'):
            self.random = False
        # adjustment to speed so corresponds to gobananas task
        # 7 seconds to cross original environment
        # speed needs to be adjusted to both speed in original
        # environment and c_range of colors
        # self.speed = 0.05 * (self.c_range[1] - self.c_range[0])
        # speed is own variable, so can be changed during training.
        self.speed = self.config['speed']
        # map avatar variables
        self.render2d = None
        self.match_square = None
        self.map_avt_node = []

        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 3
        self.max_vel = [500, 500, 0]

        self.card = None

        self.base = ShowBase()
        self.base.disableMouse()
        # assume we are showing windows unless proven otherwise
        if self.config.get('win', True):
            # only need inputs if we have a window
            self.inputs = Inputs(self.base)
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setForeground(True)
            print self.config.get('resolution')
            if self.config.get('resolution'):
                props.set_size(int(self.config['resolution'][0]), int(self.config['resolution'][1]))
                props.set_origin(0, 0)
            else:
                props.set_size(600, 600)
                props.set_origin(400, 50)
            self.base.win.requestProperties(props)
            # print self.base.win.get_size()
            # setup color map on second window
            sq_node = square.setup_square(self.config)
            self.setup_display2(sq_node)
        # print 'background color', self.base.getBackgroundColor()
        # create the avatar
        self.avatar = NodePath(ActorNode("avatar"))
        self.avatar.reparentTo(self.base.render)
        self.avatar.setH(self.base.camera.getH())
        self.base.camera.reparentTo(self.avatar)
        self.base.camera.setPos(0, 0, 0)

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
        print 'start loop'
        self.started_game = self.base.taskMgr.doMethodLater(5, self.start_play, 'start_play')
        self.showed_match = self.base.taskMgr.add(self.show_match_sample, 'match_image')

    # Task methods
    def show_match_sample(self, task):
        print 'show match sample'
        print self.color_match[:]
        # match_image.fill(*self.color_match[:])
        card = CardMaker('card')
        color_match = self.color_match[:]
        # add alpha channel
        color_match.append(1)
        print color_match
        card.set_color(*color_match[:])
        card.set_frame(-12, -8, 0, 4)
        # log this
        self.card = self.base.render.attach_new_node(card.generate())
        return task.done

    def start_play(self, task):
        print 'start play'
        # log this
        self.base.taskMgr.remove('match_image')
        self.card.removeNode()
        # print self.base.render.ls()
        self.frame_task = self.base.taskMgr.add(self.game_loop, "game_loop")
        self.frame_task.last = 0  # initiate task time of the last frame
        # log this
        self.base.setBackgroundColor(self.color_list[:])
        return task.done

    def game_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.velocity = self.inputs.poll_inputs(self.velocity)
        move = self.move_avatar(dt)
        stop = self.change_background(move)
        self.move_map_avatar(move, stop)
        match = self.check_color_match()
        if match:
            self.give_reward()
            return task.done
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

    def move_avatar(self, dt):
        # print 'velocity', self.velocity
        # this makes for smooth (correct speed) diagonal movement
        # print 'velocity', self.velocity
        magnitude = max(abs(self.velocity[0]), abs(self.velocity[1]))
        move = None
        if self.velocity.normalize():
            # go left in increasing amount
            # print 'dt', dt
            # print 'normalized'
            # print 'velocity', self.velocity
            # print 'magnitude', magnitude
            self.velocity *= magnitude
            # print 'velocity', self.velocity
            # this makes for smooth movement
            move = self.velocity * self.vel_base * dt
            # print move
            self.avatar.setFluidPos(self.avatar, move)
        return move

    def change_background(self, move):
        stop = [True, True, True]
        if move:
            # print move
            move *= self.speed
            for i in range(3):
                value = self.color_dict[i]
                if value is not None:
                    stop[i] = False
                    # keys correspond to x,y,z
                    # values correspond to r,g,b
                    if i == 2:
                        # z axis is treated differently
                        # need to work on this. z should
                        # be at min when both x and y are at max
                        # taking the average is not quite right...
                        z_move = (move[0] + move[1])/2
                        # print z_move
                        self.color_list[value] -= z_move
                    else:
                        self.color_list[value] += move[i]
                    if self.color_list[value] < self.c_range[0]:
                        self.color_list[value] = self.c_range[0]
                        stop[i] = True
                    elif self.color_list[value] > self.c_range[1]:
                        self.color_list[value] = self.c_range[1]
                        stop[i] = True
            # log this
            self.base.setBackgroundColor(self.color_list[:])
            # print self.base.getBackgroundColor()
        return stop

    def move_map_avatar(self, move, stop):
        # print move
        # avatar is mapped assuming c_range of 0.5. What do I need to
        # change to use a different c_range? c_range of one is twice
        # the
        if move:
            avt = LineSegs()
            avt.setThickness(1)
            avt.setColor(1, 1, 1)
            # print 'last', self.last_avt
            avt.move_to(self.last_avt[0], -5, self.last_avt[1])
            # print 'move', move
            new_move = [i + (j * self.avt_factor) for i, j in zip(self.last_avt, move)]
            # new_move = [i + j for i, j in zip(self.last_avt, move)]
            # would it be better to have a local stop condition?
            if stop[0]:
                new_move[0] = self.last_avt[0]
                # print 'stop x', self.last_avt[0]
            if stop[1]:
                new_move[1] = self.last_avt[1]
                # print 'stop y', self.last_avt[1]
            # print 'new', new_move
            self.last_avt = [new_move[0], new_move[1]]
            avt.draw_to(new_move[0], -5, new_move[1])
            self.map_avt_node.append(self.render2d.attach_new_node(avt.create()))
            # print self.map_avt_node[-1]
            # can't let too many nodes pile up
            if len(self.map_avt_node) > 299:
                # removing the node does not remove the object from the list
                for i, j in enumerate(self.map_avt_node):
                    j.removeNode()
                    if i > 49:
                        break
                del self.map_avt_node[0:50]

    def check_color_match(self):
        # print 'match this', self.color_tolerance
        # print self.color_list
        check_color = [j[0] < self.color_list[i] < j[1] for i, j in enumerate(self.color_tolerance)]
        # print check_color
        if all(check_color):
            return True
        else:
            return False

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
        self.clear_avatar_map()
        # if there is a match set, return to center of color gradient,
        # set new match, if applicable
        self.set_next_trial()

    def clear_avatar_map(self):
        for i, j in enumerate(self.map_avt_node):
            j.removeNode()
        self.map_avt_node = []

    def plot_match_square(self, corners):
        print 'plot match square'
        print corners
        match = LineSegs()
        match.setThickness(1.5)
        match.setColor(0, 0, 0)
        match.move_to(corners[0][0], -5, corners[1][0])
        match.draw_to(corners[0][1], -5, corners[1][0])
        match.draw_to(corners[0][1], -5, corners[1][1])
        match.draw_to(corners[0][0], -5, corners[1][1])
        match.draw_to(corners[0][0], -5, corners[1][0])
        # print self.render2d
        self.match_square = self.render2d.attach_new_node(match.create())

    def create_avatar_map_match_square(self, config=None):
        print 'make new square for map'
        if config is not None:
            config_dict = config
        else:
            config_dict = self.config
        # create square on avatar map for new color match
        map_color_match, factor = square.translate_color_map(config_dict, self.color_dict, self.color_match)
        tolerance = config_dict['tolerance'] * factor
        map_color_tolerance = [(i - tolerance, i + tolerance) for i in map_color_match]
        print map_color_tolerance
        if self.render2d:
            if self.match_square:
                self.match_square.removeNode()
            self.plot_match_square(map_color_tolerance)

    def set_next_trial(self):
        print 'set next trial'
        # move avatar back to beginning position, only matters for
        # showing card for next color match
        self.avatar.set_pos(-10, -10, 2)
        # set color_list with starting color
        # if random, won't use this again, but for manual, will
        # return to center
        # need to update self.config to new direction, if there is one
        if self.config.get('match_direction'):
            self.check_key_map()
            # return to center, otherwise random will start where you left off
            self.color_list = square.set_start_position_colors(self.config)
            # starting position for map avatar, just translate new color_list
            self.last_avt, self.avt_factor = square.translate_color_map(self.config, self.color_dict, self.color_list)
        print 'start color',  self.color_list
        print self.color_dict
        # again need to update self.config for match if using keys
        self.color_match = square.set_match_colors(self.config, self.color_dict)
        # sets the tolerance for how close to a color for reward
        self.color_tolerance = [(i - self.config['tolerance'], i + self.config['tolerance']) for i in self.color_match]
        print 'color match', self.color_match
        print 'color tolerance', self.color_tolerance
        self.create_avatar_map_match_square(self.config)
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
    CW = ColorWorld()
    CW.base.run()
