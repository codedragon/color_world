from direct.showbase.DirectObject import DirectObject
from panda3d.core import KeyboardButton
import sys
try:
    import pygame
except ImportError:
    pygame = False
    print 'PyGame not found, necessary for joystick use'


class Inputs(DirectObject):
    def __init__(self, base):
        self.base = base
        DirectObject.__init__(self)
        # joystick
        js_count = 0
        self.joystick = None
        if pygame:
            pygame.init()
            js_count = pygame.joystick.get_count()
        if js_count > 1:
            raise NotImplementedError("More than one Joystick is connected")
        elif js_count == 1:
            self.joystick = pygame.joystick.Joystick(0)
            print 'using joystick'
            self.joystick.init()
            # print self.joystick.get_numaxes()
            # threshold for joystick
            self.threshold = 0.1
        else:
            print 'Not using a joystick'
        self.key_map = {'r': None, 'f': None}
        self.setup_inputs()

    def poll_inputs(self, velocity):
        if self.joystick:
            velocity = self.poll_joystick(velocity)
        velocity = self.poll_keyboard(velocity)
        return velocity

    def poll_joystick(self, velocity):
        # joystick input -1 to 1,
        # if I get the event, it only has a signal when
        # there is movement, so loop through the events,
        # to collect events into axis call, but call
        # axis after, since it will stay at whatever the
        # last signal was, instead of zeroing out whenever
        # no movement. Much more convenient that way.
        for event in pygame.event.get():
            pass
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)

        # if both are under threshold, assume noise
        # if one is deliberate, noise in the other won't affect much
        if -self.threshold < x < self.threshold and -self.threshold < y < self.threshold:
            # print 'threshold'
            # print 'x', x, 'y', y
            velocity.x = 0
            velocity.y = 0
        else:
            velocity.x = x
            velocity.y = -y
        return velocity

    def poll_keyboard(self, velocity):
        # under normal circumstances, use median of joytick output
        x_speed = 0.5
        y_speed = 0.5
        # checks keyboard, not mouse, in this case
        is_down = self.base.mouseWatcherNode.is_button_down
        # Instead of usual movement, exactly counteract joystick,
        # if using joystick and currently moving
        if self.joystick:
            if abs(velocity.x) > self.threshold:
                if velocity.x > 0:
                    x_speed = velocity.x
                else:
                    x_speed = -velocity.x
            if abs(velocity.y) > self.threshold:
                if velocity.y > 0:
                    y_speed = velocity.y
                else:
                    y_speed = -velocity.y
        else:
            velocity.x = 0
            velocity.y = 0
        if is_down(KeyboardButton.up()):
            velocity.y += y_speed
        if is_down(KeyboardButton.down()):
            velocity.y -= y_speed
        if is_down(KeyboardButton.left()):
            velocity.x -= x_speed
            # print 'keyboard'
        if is_down(KeyboardButton.right()):
            velocity.x += x_speed
        return velocity

    def setup_inputs(self):
        self.accept('q', self.close)
        self.accept('r', self.set_key, ['r', True])
        self.accept('l', self.set_key, ['r', False])
        self.accept('f', self.set_key, ['f', True])
        self.accept('b', self.set_key, ['f', False])

    def set_key(self, key, value):
        self.key_map[key] = value
        return

    def close(self):
        pygame.quit()
        sys.exit()
