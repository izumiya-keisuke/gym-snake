#########
gym-snake
#########

gym-snake is the OpenAI Gym environment for the Snake game.

*******
Install
*******

If you use `poetry <https://python-poetry.org/>`_, you can install gym-snake by:
::

    $ poetry add git+https://github.com/izumiya-keisuke/gym-snake.git

Installing with pip is also supported:
::

    $ pip install https://github.com/izumiya-keisuke/gym-snake.git

************
Environments
************

========
snake-v0
========

:code:`snake-v0` is a default environment.
You can set parameters as follows:

* Field height and width (default: 10, minimum: 3)
* initial length of snake (default: 3, minimum: 3, maximum: min(height, width))

Gym environment fields are as follows:

observation_space
    :code:`gym.spaces.Box(low=0, high=4, shape=(height, width))` (0: wall, 1: floor, 2: head, 3: body, 4: food)
action_space
    :code:`gym.spaces.Discrete(4)` (up, right, down, left)
reward_range
    :code:`(-1, 1)` (eat food: 1, dead: -1, other: 0)
meta_data
    :code:`{"render.modes": ["human", "ansi"]}`

**************
Playing script
**************

After installing, you can play snake (:code:`snake-v0`) by
::

    $ snake-play

If you install gym-snake with poetry, you can play snake without activating the virtual environment, by
::

    $ poetry run snake-play

By running these commands, you can see the game window:
::

    ++++++++++++
    +..........+
    +..........+
    +......s~~.+
    +.........%+
    +..........+
    +..........+
    +..........+
    +..........+
    +..........+
    +..........+
    ++++++++++++

:code:`+` shows wall, :code:`.` shows floor, :code:`%` shows a food, :code:`s` shows a snake head, and :code:`~` shows snake body.

Commands:

* go up: :code:`w` or :code:`k`
* go right: :code:`d` or :code:`l`
* go down: :code:`s` or :code:`j`
* go left: :code:`a` or :code:`h`
* quit the game: :code:`Ctrl-c`

*******
License
*******

Apache-2.0
