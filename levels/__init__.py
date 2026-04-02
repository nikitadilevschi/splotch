"""
Level data management and building.
"""

from levels.gaps import GAPS_L1, GAPS_L2, GAPS_L3
from levels.spikes import SPIKES_L1, SPIKES_L2, SPIKES_L3
from levels.push import PUSH_L1, PUSH_L2, PUSH_L3
from levels.platforms import PLATFORMS_L1, PLATFORMS_L2, PLATFORMS_L3
from levels.saws import SAWS_L1, SAWS_L2, SAWS_L3
from core.constants import CAT_NAMES, CAT_COLORS

LEVELS = [
    [GAPS_L1,      GAPS_L2,      GAPS_L3],
    [SPIKES_L1,    SPIKES_L2,    SPIKES_L3],
    [PUSH_L1,      PUSH_L2,      PUSH_L3],
    [PLATFORMS_L1, PLATFORMS_L2, PLATFORMS_L3],
    [SAWS_L1,      SAWS_L2,      SAWS_L3],
]

__all__ = ['LEVELS', 'CAT_NAMES', 'CAT_COLORS']

