import matplotlib
matplotlib.use('TKAgg')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation

x = [0, 1, 2]
y = [0, 1, 2]
x2 = [0, 1, 2]
y2 = [0, 1, 2]

yaw = [0.0, 0.5, 1.3]
fig = plt.figure()
plt.axis('equal')
plt.grid()
ax = fig.add_subplot(111)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

patch = patches.Rectangle((0, 0), 0, 0, fc='y')
patch2 = patches.Rectangle((1, 1), 0, 0, fc='b')

def init():
    ax.add_patch(patch)
    ax.add_patch(patch2)
    return patch,

def animate(i):
    patch.set_width(1.2)
    patch.set_height(1.0)
    patch2.set_width(1.2)
    patch2.set_height(1.0)
    patch.set_xy([x[i], y[i]])
    patch._angle = -np.rad2deg(yaw[i])
    patch2.set_xy([x2[i], y2[i]])
    return patch, patch2

anim = animation.FuncAnimation(fig, animate,
                               init_func=init,
                               frames=len(x),
                               interval=500,
                               blit=True)
plt.show()