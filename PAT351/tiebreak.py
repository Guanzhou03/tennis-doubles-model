import numpy as np
import random
import tqdm

pa, pb = 0.67, 0.66
e = 0.05
gt = 0.5953507207538664
tb_diff, match_diff = [], []
for _ in range(100):
    PA = pa + random.uniform(-e, e)
    PB = pb + random.uniform(-e, e)
    num_sets = 3

    def tb(A_score, B_score, turn):
        if (A_score >= 7 and A_score - B_score >= 2) or (A_score >= 13):
            return 1
        elif (B_score >= 7 and B_score - A_score >= 2) or (B_score >= 13):
            return 0
        elif turn == 0:
            if (A_score + B_score + 1) % 2:
                turn = abs(turn - 1)
            return PA * tb(A_score + 1, B_score, turn) + (1 - PA) * tb(A_score, B_score + 1, turn)
        else:
            if (A_score + B_score + 1) % 2:
                turn = abs(turn - 1)
            return (1 - PB) * tb(A_score + 1, B_score, turn) + PB * tb(A_score, B_score + 1, turn)

    PA_tb = np.mean([tb(0, 0, 0), tb(0, 0, 1)])
    PB_tb = 1 - PA_tb


    def game(A_score, B_score, turn):
        if (A_score >= 4 and A_score - B_score >= 2) or A_score >= 6:
            return 1
        elif (B_score >= 4 and B_score - A_score >= 2) or B_score >= 6:
            return 0
        elif turn == 0:
            return PA * game(A_score + 1, B_score, turn) + (1 - PA) * game(A_score, B_score + 1, turn)
        else:
            return (1 - PB) * game(A_score + 1, B_score, turn) + PB * game(A_score, B_score + 1, turn)

    def Set(A_game, B_game, turn):
        if (A_game >= 6 and A_game - B_game >= 2) or A_game >= 7:
            return 1
        elif (B_game >= 6 and B_game - A_game >= 2) or B_game >= 7:
            return 0
        else:
            PA_game = PA_tb if A_game == 6 and B_game == 6  else game(0, 0, turn)
            turn = abs(turn - 1)
            return PA_game * Set(A_game + 1, B_game, turn) + (1 - PA_game) * Set(A_game, B_game + 1, turn)

    def Match(A_set, B_set, turn):
        if (A_set >= 2 and num_sets == 3) or (A_set >= 3 and num_sets == 5):
            return 1
        elif (B_set >= 2 and num_sets == 3) or (B_set >= 3 and num_sets == 5):
            return 0
        else:
            PA_set = Set(0, 0, turn)
            turn = abs(turn - 1)
            return PA_set * Match(A_set + 1, B_set, turn) + (1 - PA_set) * Match(A_set, B_set + 1, turn)

    tb_pred = np.mean([tb(0, 0, 0), tb(0, 0, 1)])
    match_pred = np.mean([Match(0, 0, 0), Match(0, 0, 1)])

    tb_diff.append(abs(tb_pred - gt))
    match_diff.append(abs(match_pred - gt))

    # print(np.mean([tb(0, 0, 0), tb(0, 0, 1)]))
    # print(np.mean([Match(0, 0, 0), Match(0, 0, 1)]))
    # print(gt)
    print(np.mean(tb_diff))
    print(np.mean(match_diff))
    print()


