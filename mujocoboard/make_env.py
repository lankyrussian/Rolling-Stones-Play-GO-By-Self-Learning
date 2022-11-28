from envs.virtualboard import SpherosEnv as SE
import random as rnd

if __name__=="__main__":
    cell_len = 0.33
    b_len = 5
    board_size = b_len**2
    x_b, y_b = 3, 3
    real_len = b_len * 2 + x_b*2
    sphero_positions = []
    n_on_board = 13
    # generate a robot for each player to have enough to play
    empty_spaces = [i for i in range(board_size)]
    colors = []
    # stones that are outside
    out_idx = (0,0)
    for i in range(board_size - n_on_board):
        x = out_idx[0]
        y = out_idx[1]
        # randomly assign color
        rgba = (0.5,0.5,0.5,0.75)
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
        rgba = (1,1,1,1) if rnd.random() < 0.5 else (0,0,0,1)
        colors.append(rgba)
        sphero_positions.append((x*cell_len - real_len*cell_len/2, y*cell_len-real_len*cell_len/2))
    env = SE.build_env(sphero_positions, [real_len*cell_len, real_len*cell_len], colors)
    with open("board.xml", "w") as f:
        f.write(env)