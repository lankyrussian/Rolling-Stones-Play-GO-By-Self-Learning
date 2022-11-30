from envs.virtualboard import build_env
import random as rnd

cell_len = 0.34
b_len = 5
board_size = b_len**2
x_b, y_b = 3, 3
real_len = b_len * 2 + x_b*2

def make_random_env(n_on_board=13):
    sphero_positions = []
    # generate a robot for each player to have enough to play
    empty_spaces = [i for i in range(board_size)]
    colors = []
    # stones that are outside
    out_idx = (0, 0)
    for i in range(board_size - n_on_board):
        x = out_idx[0]
        y = out_idx[1]
        # randomly assign color
        rgba = (0.5, 0.5, 0.5, 0.75)
        colors.append(rgba)
        sphero_positions.append((x * cell_len - real_len * cell_len / 2, y * cell_len - real_len * cell_len / 2))
        nx = i % real_len
        ny = i // real_len
        out_idx = (nx, ny)
    # stones that are on the board
    for i in range(n_on_board):
        i = rnd.choice(empty_spaces)
        empty_spaces.remove(i)
        x = (i % b_len) * 2 + x_b
        y = (i // b_len) * 2 + y_b
        # randomly assign color
        rgba = (1, 1, 1, 1) if rnd.random() < 0.5 else (0, 0, 0, 1)
        colors.append(rgba)
        sphero_positions.append((x * cell_len - real_len * cell_len / 2, y * cell_len - real_len * cell_len / 2))
    env = build_env(sphero_positions, [real_len * cell_len, real_len * cell_len], colors)
    return env

def make_empty_env():
    return make_random_env(0)


if __name__=="__main__":
    # env = make_random_env(13)
    env = make_empty_env()
    with open("board.xml", "w") as f:
        f.write(env)