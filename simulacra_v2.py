  GNU nano 8.4                                                                                   simulacra_v2.py                                                                                            
import os
import glob
import numpy as np
import matplotlib.pyplot as plt


def run_simulation(edge_penalty=0.0):
    print("EDGE PENALTY RECEIVED:", edge_penalty)

    size = 120
    n_agents = 50
    n_frames = 300

    pickup = np.array([15.0, 85.0])
    drop = np.array([85.0, 85.0])

    terrain = np.ones((size, size), dtype=float)

    terrain[15:85, 18:28] = 999.0
    terrain[15:55, 36:46] = 999.0
    terrain[65:85, 36:46] = 999.0
    terrain[15:85, 54:64] = 999.0

    agents = np.zeros((n_agents, 4), dtype=float)
    agents[:, 0] = drop[0] + np.random.uniform(-8, 8, size=n_agents)
    agents[:, 1] = drop[1] + np.random.uniform(-8, 8, size=n_agents)
    agents[:, 2] = np.random.uniform(0, 2 * np.pi, size=n_agents)
    agents[:, 3] = 0.0

    field = np.zeros((size, size), dtype=float)
    histories = [[] for _ in range(n_agents)]
    distances = np.zeros(n_agents)
    border_time = np.zeros(n_agents)
    congestion_delay = 0
    tasks_completed = 0
    conflict_events = 0
    for f in glob.glob("frame_*.png"):
        try:
            os.remove(f)
        except OSError:
            pass

    def clip_pos(x, y):
        return np.clip(x, 0, size - 1), np.clip(y, 0, size - 1)

    for t in range(n_frames):
        new_field = field.copy()

        for i in range(n_agents):
            x, y, angle, carrying = agents[i]
                                                                                             [ Read 210 lines ]
^G Help          ^O Write Out     ^F Where Is      ^K Cut           ^T Execute       ^C Location      M-U Undo         M-A Set Mark     M-] To Bracket   M-B Previous     ◂ Back           ^◂ Prev Word
^X Exit          ^R Read File     ^\ Replace       ^U Paste         ^J Justify       ^/ Go To Line    M-E Redo         M-6 Copy         ^B Where Was     M-F Next         ▸ Forward        ^▸ Next Word
