import logging
from gym.envs.registration import register
from .gharrafa_basic import GharrafaBasicEnv

logger = logging.getLogger(__name__)

register(
    id='gymGharrafa-v0',
    entry_point='gym_gharrafa:GharrafaBasicEnv',
    max_episode_steps = 86400,
    reward_threshold = 8640
)
