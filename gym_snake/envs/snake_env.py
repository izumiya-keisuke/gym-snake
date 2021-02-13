"""
Copyright 2021 Keisuke Izumiya

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random as rnd

import gym  # pylint: disable=E0401
import numpy as np  # pylint: disable=E0401

from gym_snake.alt_set import AltSet
from gym_snake.enum import Cell, Direction
from gym_snake.utils import CELL_TO_CHAR_DICT


class SnakeEnvV0(gym.Env):
    def __init__(self, height=10, width=10, initial_length=3, max_step=None):
        assert height > 2, f"height must be greater than 2, but got {height}."
        assert width > 2, f"width must be greater than 2, but got {width}."
        assert (
            3 <= initial_length <= min(height, width)
        ), f"initial_length must be in [3, min(height, width)], but got {initial_length}."
        assert (
            max_step is None or max_step > 0
        ), f"max_step must be positive or None, but got {max_step}."

        self._height = height
        self._width = width
        self._initial_length = initial_length
        if max_step is None:
            self._max_step = float("inf")
        else:
            self._max_step = max_step

        obs_shape = (height, width)
        cells_shape = (height + 2, width + 2)

        self._already_done = True
        self._step = None

        # gym env fields
        self.observation_space = gym.spaces.Box(min(Cell), max(Cell), obs_shape)
        self.action_space = gym.spaces.Discrete(4)
        self.reward_range = (-1, 1)
        self.metadata = {"render.modes": ["human", "ansi"]}

        # fields
        self._cells = np.empty(cells_shape, dtype=np.uint8)
        self._directions = np.empty(cells_shape, dtype=np.uint8)

        # position
        self._head_pos = None
        self._tail_pos = None
        self._floor_poses = None

        # position diff (used in step)
        self._diffs = {
            Direction.UP: (-1, 0),
            Direction.RIGHT: (0, 1),
            Direction.DOWN: (1, 0),
            Direction.LEFT: (0, -1),
        }

        # initial cells, directions, floor-positions (used in reset)
        self._init_cells = np.full(cells_shape, Cell.WALL, dtype=np.uint8)
        self._init_cells[1:-1, 1:-1] = np.full(obs_shape, Cell.FLOOR)
        self._init_directions = np.full(cells_shape, Direction.UP, dtype=np.uint8)
        self._init_floor_poses = AltSet(
            (y, x) for x in range(1, width + 1) for y in range(1, height + 1)
        )

    def _set_food(self):
        # if floor does not exist (game clear), return 1
        if self._floor_poses.empty():
            return 1

        y, x = self._floor_poses.pop()
        self._cells[y, x] = Cell.FOOD

        return 0

    def reset(self):
        self._already_done = False
        self._step = 0

        # initialize cells, directions and floor-positions
        self._cells = self._init_cells.copy()
        self._directions = self._init_directions.copy()
        self._floor_poses = self._init_floor_poses.copy()

        # set snake, directions and floor-positions
        direction = rnd.choice(list(Direction))
        if direction == Direction.UP:
            head_x = rnd.randint(1, self._width)
            tail_x = head_x
            head_y = rnd.randint(1, self._height - self._initial_length + 1)
            tail_y = head_y + self._initial_length - 1

            self._cells[head_y + 1 : tail_y + 1, head_x] = Cell.BODY
            self._directions[head_y + 1 : tail_y + 1, head_x] = direction
            for y in range(head_y, tail_y + 1):
                self._floor_poses.remove((y, head_x))
        elif direction == Direction.DOWN:
            head_x = rnd.randint(1, self._width)
            tail_x = head_x
            tail_y = rnd.randint(1, self._height - self._initial_length + 1)
            head_y = tail_y + self._initial_length - 1

            self._cells[tail_y:head_y, head_x] = Cell.BODY
            self._directions[tail_y:head_y, head_x] = direction
            for y in range(tail_y, head_y + 1):
                self._floor_poses.remove((y, head_x))
        elif direction == Direction.LEFT:
            head_x = rnd.randint(1, self._width - self._initial_length + 1)
            tail_x = head_x + self._initial_length - 1
            head_y = rnd.randint(1, self._height)
            tail_y = head_y

            self._cells[head_y, head_x + 1 : tail_x + 1] = Cell.BODY
            self._directions[head_y, head_x + 1 : tail_x + 1] = direction
            for x in range(head_x, tail_x + 1):
                self._floor_poses.remove((head_y, x))
        else:  # Direction.RIGHT
            tail_x = rnd.randint(1, self._width - self._initial_length + 1)
            head_x = tail_x + self._initial_length - 1
            head_y = rnd.randint(1, self._height)
            tail_y = head_y

            self._cells[head_y, tail_x:head_x] = Cell.BODY
            self._directions[head_y, tail_x:head_x] = direction
            for x in range(tail_x, head_x + 1):
                self._floor_poses.remove((head_y, x))
        self._head_pos = (head_y, head_x)
        self._tail_pos = (tail_y, tail_x)
        self._cells[head_y, head_x] = Cell.HEAD

        assert self._set_food() == 0

        return self._cells[1:-1, 1:-1].copy()

    def step(self, action):
        if self._already_done:
            return self._cells[1:-1, 1:-1].copy(), 0.0, True, {"step": self._step}

        # remove old tail
        old_tail_pos = self._tail_pos
        old_tail_y, old_tail_x = old_tail_pos
        self._cells[old_tail_y, old_tail_x] = Cell.FLOOR
        self._floor_poses.add((old_tail_y, old_tail_x))

        # set new tail
        diff_y, diff_x = self._diffs[self._directions[old_tail_y, old_tail_x]]
        self._tail_pos = (old_tail_y + diff_y, old_tail_x + diff_x)

        # remove old head
        old_head_y, old_head_x = self._head_pos
        self._cells[old_head_y, old_head_x] = Cell.BODY
        self._directions[old_head_y, old_head_x] = action

        # add new head
        diff_y, diff_x = self._diffs[action]
        new_head_y = old_head_y + diff_y
        new_head_x = old_head_x + diff_x
        eaten_cell = self._cells[new_head_y, new_head_x]
        new_head_pos = (new_head_y, new_head_x)
        self._head_pos = new_head_pos
        self._cells[new_head_y, new_head_x] = Cell.HEAD
        self._floor_poses.discard(new_head_pos)

        # calc reward, done
        if eaten_cell == Cell.FLOOR or old_tail_pos == new_head_pos:
            reward = 0.0
            done = False
        elif eaten_cell in (Cell.BODY, Cell.WALL):  # game over
            reward = -1.0
            done = True
        elif eaten_cell == Cell.FOOD:
            reward = 1.0
            self._cells[old_tail_y, old_tail_x] = Cell.BODY
            self._tail_pos = old_tail_pos
            self._floor_poses.remove(old_tail_pos)

            done = self._set_food() == 1
        else:  # eaten_cell == Cell.HEAD
            raise ValueError("Impossible path (maybe bug).")

        self._step += 1
        if self._step >= self._max_step:
            done = True
        self._already_done = done

        return self._cells[1:-1, 1:-1].copy(), reward, done, {"step": self._step}

    def render(self, mode="human"):
        if mode not in self.metadata["render.modes"]:
            raise NotImplementedError

        # make field str array
        ary = [[None] * (self._width + 2) for _ in range(self._height + 2)]
        for y in range(self._height + 2):
            for x in range(self._width + 2):
                ary[y][x] = CELL_TO_CHAR_DICT[self._cells[y, x]]

        # convert array to str
        str_ = ""
        for row in ary:
            str_ += "".join(row) + "\n"
        str_ = str_[:-1]

        if mode == "human":
            print(str_)
        else:  # mode == 'ansi'
            return str_

    def seed(self, seed=None):
        self.rng, seed = gym.utils.seeding.np_random(seed)
        return [seed]
