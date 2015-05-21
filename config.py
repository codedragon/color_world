# configuration for color space

# possible list items: 'r': red, 'g': green, 'b': blue.
# list corresponds to x, y first index is what varies with x,
# second index varies with y, use None if you don't want an
# color to vary with that axis, this means moving in that
# direction will do nothing.

colors = ['r']

# if training, set this to determine which direction to use for first color match
# right, left, front, back or None
# this must match up with the axis. if using x axis, use right or left. if using y axis,
# use front or back. None for random
# if match_direction is used, always starts in center, otherwise, start position is random.
match_direction = ['right']
# match_direction = None

# Not implemented yet:
# if using x and y axis, can be ['front', 'right']. order irrelevant,
# but number of match directions must match number of colors used.
# high numbers are very bright, low numbers very dark
# c_range = [0.2, 0.7]
c_range = [0.2, 0.7]
# if there is a color that does not vary,
# this is its value
static = 0.1
# all blue: if static low, dark blue, static high, yellow/white
# all red:  if static low, dark red, static high, teal/white
# all green: if static low, dark green, static high, lavender/white

# speed
speed = 0.05

# how close to a color to get reward
tolerance = 0.01

num_beeps = 3

pump_delay = 0.2

resolution = [1024, 768]