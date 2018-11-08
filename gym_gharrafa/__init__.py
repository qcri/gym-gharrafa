import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='gymGharrafa-v0',
    entry_point='gymGharrafa:GharrafaV0',
)
