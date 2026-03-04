import numpy as np
from collections import deque

GRID_SIZE = 20

# Absolute directions: 0=Up 1=Right 2=Down 3=Left
DIR_VECTORS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

# 8 compass directions for vision rays (N, NE, E, SE, S, SW, W, NW)
VISION_DIRS = [
    (-1,  0), (-1,  1), (0,  1), (1,  1),
    ( 1,  0), ( 1, -1), (0, -1), (-1, -1),
]


class SnakeEnv:
    def __init__(self, grid_size=GRID_SIZE, max_steps_no_food=150):
        self.grid_size = grid_size
        self.max_steps_no_food = max_steps_no_food
        self.reset()

    # ------------------------------------------------------------------
    def reset(self):
        mid = self.grid_size // 2
        self.head = [mid, mid]
        self.body = deque([[mid, mid], [mid, mid - 1], [mid, mid - 2]])
        self.direction = 1          # facing right
        self.score = 0
        self.steps = 0
        self.steps_since_food = 0
        self.alive = True
        self._place_food()
        return self._get_obs()

    # ------------------------------------------------------------------
    def _place_food(self):
        body_set = {tuple(b) for b in self.body}
        while True:
            r = np.random.randint(0, self.grid_size)
            c = np.random.randint(0, self.grid_size)
            if (r, c) not in body_set:
                self.food = [r, c]
                break

    # ------------------------------------------------------------------
    def step(self, action: int):
        """
        action: 0=Up 1=Right 2=Down 3=Left (absolute).
        180-degree reversals are ignored (snake keeps current direction).
        Returns (obs, reward, done, info).
        """
        opposite = (self.direction + 2) % 4
        if action == opposite:
            action = self.direction
        self.direction = action

        dr, dc = DIR_VECTORS[self.direction]
        new_head = [self.head[0] + dr, self.head[1] + dc]

        self.steps += 1
        self.steps_since_food += 1

        # Wall collision
        if not (0 <= new_head[0] < self.grid_size and
                0 <= new_head[1] < self.grid_size):
            self.alive = False
            return self._get_obs(), -1.0, True, self._info()

        # Self collision  (skip tail tip — it will move away)
        body_list = list(self.body)[:-1]
        if new_head in body_list:
            self.alive = False
            return self._get_obs(), -1.0, True, self._info()

        # Move
        self.body.appendleft(new_head)
        self.head = new_head

        # Food
        if new_head == self.food:
            self.score += 1
            self.steps_since_food = 0
            self._place_food()
            reward = 10.0
        else:
            self.body.pop()
            # Small reward for moving toward food, penalty for away
            head_dist  = abs(self.head[0] - self.food[0]) + abs(self.head[1] - self.food[1])
            prev_dist  = abs(self.head[0] - dr - self.food[0]) + abs(self.head[1] - dc - self.food[1])
            reward = 0.1 if head_dist < prev_dist else -0.1

        # Starvation
        if self.steps_since_food >= self.max_steps_no_food:
            self.alive = False
            return self._get_obs(), -0.5, True, self._info()

        return self._get_obs(), reward, False, self._info()

    # ------------------------------------------------------------------
    def _info(self):
        return {"score": self.score, "steps": self.steps}

    # ------------------------------------------------------------------
    def _get_obs(self) -> np.ndarray:
        """
        24-dimensional observation:
        For each of 8 compass directions cast a ray and return:
          [1/dist_to_wall,  1/dist_to_body (0 if none),  food_flag]
        All values in [0, 1].
        """
        obs = np.zeros(24, dtype=np.float32)
        body_set = {tuple(b) for b in self.body}

        for i, (dr, dc) in enumerate(VISION_DIRS):
            r, c = self.head
            step = 0
            wall_inv = 0.0
            body_inv = 0.0
            food_seen = 0.0

            while True:
                r += dr
                c += dc
                step += 1
                if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
                    wall_inv = 1.0 / step
                    break
                if body_inv == 0.0 and (r, c) in body_set:
                    body_inv = 1.0 / step
                if food_seen == 0.0 and [r, c] == self.food:
                    food_seen = 1.0

            obs[i * 3]     = wall_inv
            obs[i * 3 + 1] = body_inv
            obs[i * 3 + 2] = food_seen

        return obs

    # ------------------------------------------------------------------
    def render_grid(self) -> np.ndarray:
        """Returns 2-D int8 array: 0=empty 1=food 2=body 3=head."""
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        for b in self.body:
            if 0 <= b[0] < self.grid_size and 0 <= b[1] < self.grid_size:
                grid[b[0], b[1]] = 2
        hr, hc = self.head
        if 0 <= hr < self.grid_size and 0 <= hc < self.grid_size:
            grid[hr, hc] = 3
        fr, fc = self.food
        if 0 <= fr < self.grid_size and 0 <= fc < self.grid_size:
            grid[fr, fc] = 1
        return grid
