import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from PIL import Image

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
            old_x, old_y = x, y

            target = drop if carrying == 1 else pickup

            candidate_angles = [
                angle - 0.6,
                angle - 0.3,
                angle,
                angle + 0.3,
                angle + 0.6,
            ]

            best_score = -1e9
            best_angle = angle

            for a in candidate_angles:
                nx = x + 2.0 * np.cos(a)
                ny = y + 2.0 * np.sin(a)
                nx, ny = clip_pos(nx, ny)

                tx, ty = int(nx), int(ny)

                if terrain[ty, tx] > 900:
                    score = -1e9
                else:
                    dist_to_target = np.sqrt((nx - target[0]) ** 2 + (ny - target[1]) ** 2)
                    score = -dist_to_target

                    if tx < 8 or tx > size - 8 or ty < 8 or ty > size - 8:
                        score -= edge_penalty * 20

                    score += np.random.uniform(-1.0, 1.0)

                if score > best_score:
                    best_score = score
                    best_angle = a

            angle = best_angle + np.random.uniform(-0.08, 0.08)

            speed = 1.2
            new_x = x + speed * np.cos(angle)
            new_y = y + speed * np.sin(angle)
            new_x, new_y = clip_pos(new_x, new_y)

            cx, cy = int(new_x), int(new_y)

            if terrain[cy, cx] > 900:
                new_x, new_y = x, y
                angle += np.pi / 2

            x, y = new_x, new_y
            xi, yi = int(x), int(y)

            # conflict detection
            for j in range(i + 1, n_agents):
                ox, oy = agents[j][0], agents[j][1]

                d = np.sqrt((x - ox)**2 + (y - oy)**2)

                if d < 1.2:
                    if np.random.random() < 0.03:
                        conflict_events += 1

            # congestio detection
            nearby_robots = 0

            for j in range(n_agents):
                if j == i:
                    continue

                ox, oy = agents[j][0], agents[j][1]

                d2 = (x - ox) ** 2 + (y - oy) ** 2

                if d2 < 36:
                    nearby_robots += 1

            if nearby_robots >= 4:
                congestion_delay += 0.01


            distances[i] += np.sqrt((x - old_x) ** 2 + (y - old_y) ** 2)

            if carrying == 0:
                if (x - pickup[0]) ** 2 + (y - pickup[1]) ** 2 < 25:
                    carrying = 1

            if carrying == 1:
                if (x - drop[0]) ** 2 + (y - drop[1]) ** 2 < 25:
                    carrying = 0
                    tasks_completed += 1

            deposit = 2.2 if carrying == 1 else 0.9
            new_field[yi, xi] = new_field[yi, xi] * 0.95 + deposit

            agents[i] = np.array([x, y, angle, carrying], dtype=float)
            histories[i].append((x, y))

        field = (
            0.78 * new_field
            + 0.055 * np.roll(new_field, 1, axis=0)
            + 0.055 * np.roll(new_field, -1, axis=0)
            + 0.055 * np.roll(new_field, 1, axis=1)
            + 0.055 * np.roll(new_field, -1, axis=1)
        )
        field *= 0.992

        plt.figure(figsize=(6, 6))
        plt.gca().set_facecolor("#121216")

        terrain_rgb = np.zeros((size, size, 3), dtype=float)
        terrain_rgb[:, :] = [0.08, 0.08, 0.10]
        terrain_rgb[terrain > 900] = [0.60, 0.60, 0.60]

        plt.imshow(terrain_rgb, origin="upper")

        plt.imshow(
            field,
            cmap="magma",
            alpha=0.78,
            origin="upper",
            vmin=0,
            vmax=max(0.25, field.max() * 0.45)
        )

        plt.scatter([pickup[0]], [pickup[1]], c="cyan", s=180, marker="s", edgecolors="white")
        plt.scatter([drop[0]], [drop[1]], c="lime", s=180, marker="s", edgecolors="white")

        exploring = agents[:, 3] < 0.5
        carrying_mask = agents[:, 3] > 0.5

        plt.scatter(agents[exploring, 0], agents[exploring, 1], c="white", s=30)
        plt.scatter(agents[carrying_mask, 0], agents[carrying_mask, 1], c="red", s=42, edgecolors="white", linewidths=0.3)

        for i in range(n_agents):
            if len(histories[i]) > 1:
                hx, hy = zip(*histories[i])
                plt.plot(hx, hy, linewidth=0.45, alpha=0.25, color="white")

        plt.text(5, 85, "PICK STATION", color="white", fontsize=8)
        plt.text(76, 85, "DROP ZONE", color="white", fontsize=8)
        plt.text(3, 6, f"Simulacra Warehouse | frame {t}", color="white", fontsize=9)

        plt.xlim(0, size - 1)
        plt.ylim(size - 1, 0)
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.savefig(f"frame_{t:03d}.png", dpi=120, facecolor="#121216")
        plt.close()

    gif_path = os.path.join(os.getcwd(), f"simulacra_edge_{edge_penalty}.gif")

    

frames = []
first_size = None

for filename in sorted(glob.glob("frame_*.png")):
    img = Image.open(filename).convert("RGB")

    if first_size is None:
        first_size = img.size
    else:
        img = img.resize(first_size)

    frames.append(np.array(img))

imageio.mimsave(gif_path, frames, duration=0.06)

    return gif_path, {
        "total_movement": round(distances.mean(), 2),
        "border_time": congestion_delay,
        "interaction_points": conflict_events,
        "tasks_completed": tasks_completed
    }
