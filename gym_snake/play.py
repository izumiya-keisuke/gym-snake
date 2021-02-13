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

import contextlib as ctxlib
import os
import termios
import tty

import gym  # pylint: disable=E0401

# import gym_snake
from gym_snake import Direction


@ctxlib.contextmanager
def no_echo():
    attr = termios.tcgetattr(0)
    try:
        tty.setraw(0)
        yield
    finally:
        termios.tcsetattr(0, termios.TCSAFLUSH, attr)


def main():
    env = gym.make("snake-v0")

    try:
        obs = env.reset()
        return_ = 0
        env.render()
        while True:
            with no_echo():
                ch = os.read(0, 1)
            if ord(ch) == 3:  # Ctrl-C
                break

            if ch in b"wk":
                action = Direction.UP
            elif ch in b"dl":
                action = Direction.RIGHT
            elif ch in b"sj":
                action = Direction.DOWN
            elif ch in b"ah":
                action = Direction.LEFT
            else:
                print("=== Invalid action ===")
                continue

            obs, reward, done, _ = env.step(action)
            return_ += reward
            if done:
                print("=== Game over ===")
                print(f"Episode return: {return_}")
                break

            env.render()
    finally:
        env.close()


if __name__ == "__main__":
    main()
