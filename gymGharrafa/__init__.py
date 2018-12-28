import logging
from gym.envs.registration import register
from gymGharrafa.GharrafaBasicEnv import GharrafaBasicEnv

logger = logging.getLogger(__name__)

register(
    id='gymGharrafa-v0',
    entry_point='gymGharrafa:GharrafaBasicEnv',
    kwargs={'GUI' : True},
    max_episode_steps = 86400,
    reward_threshold = 2500
)

register(
    id='gymGharrafa-v1',
    entry_point='gymGharrafa:GharrafaBasicEnv',
    kwargs={'GUI' : False},
    max_episode_steps = 86400,
    reward_threshold = 2500
)
