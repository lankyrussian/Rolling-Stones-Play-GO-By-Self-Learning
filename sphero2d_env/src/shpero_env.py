
from brax.io import html
import brax
import numpy as np


class Sphero2dEnv():
    def __init__(self):
        bouncy_ball = brax.Config(dt=0.05, substeps=20, dynamics_mode='pbd')

        # ground is a frozen (immovable) infinite plane
        ground = bouncy_ball.bodies.add(name='ground')
        ground.frozen.all = True
        plane = ground.colliders.add().plane
        plane.SetInParent()  # for setting an empty oneof

        # ball weighs 1kg, has equal rotational inertia along all axes, is 1m long, and
        # has an initial rotation of identity (w=1,x=0,y=0,z=0) quaternion
        ball = bouncy_ball.bodies.add(name='ball', mass=1)
        cap = ball.colliders.add().capsule
        cap.radius, cap.length = 0.5, 1

        # gravity is -9.8 m/s^2 in z dimension
        bouncy_ball.gravity.z = -9.8

        qp = brax.QP(
            # position of each body in 3d (z is up, right-hand coordinates)
            pos=np.array([[0., 0., 0.],  # ground
                          [0., 0., 3.]]),  # ball is 3m up in the air
            # velocity of each body in 3d
            vel=np.array([[0., 0., 0.],  # ground
                          [0., 0., 0.]]),  # ball
            # rotation about center of body, as a quaternion (w, x, y, z)
            rot=np.array([[1., 0., 0., 0.],  # ground
                          [1., 0., 0., 0.]]),  # ball
            # angular velocity about center of body in 3d
            ang=np.array([[0., 0., 0.],  # ground
                          [0., 0., 0.]])  # ball
        )

        bouncy_ball.elasticity = 0.85  # @param { type:"slider", min: 0, max: 1.0, step:0.05 }
        ball_velocity = -0.5  # @param { type:"slider", min:-5, max:5, step: 0.5 }

        self.sys = brax.System(bouncy_ball)

        # provide an initial velocity to the ball
        qp.vel[1, 0] = ball_velocity
        self.qp = qp

        # _, ax = plt.subplots()
        # self.ax = ax
        # plt.xlim([-3, 3])
        # plt.ylim([0, 4])
        # plt.ion()


    def render(self):
        # ax = self.ax
        # pos, alpha=1
        # for i, p in enumerate(pos):
        #     ax.add_patch(Circle(xy=(p[0], p[2]), radius=cap.radius, fill=False, color=(0, 0, 0, alpha)))
        #     if i < len(pos) - 1:
        #         pn = pos[i + 1]
        #         ax.add_line(Line2D([p[0], pn[0]], [p[2], pn[2]], color=(1, 0, 0, alpha)))
        # plt.show()
        html.render(self.sys, [self.qp])

    def step(self, action):
        assert len(action) == 2
        self.qp.ang[1, 0] += action[0]
        self.qp.ang[1, 1] += action[1]
        # for i in range(10):
        self.qp, _ = self.sys.step(self.qp, [])


if __name__ == "__main__":
    env = Sphero2dEnv()
    for _ in range(100):
        rnd_action = np.random.rand([2])