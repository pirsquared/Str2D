"""
stencil.py

a module to produce Stencils and Masks that selectively conceal or reveal
elements of a sequence.
More of a discrete Jacquard than a continuous stencil, but, maybe, the noun
stencil is more universally understood.

# there is wonderful trivia and vocabulary to learn and maybe use here:
# https://en.wikipedia.org/wiki/Jacquard_loom#Principles_of_operation
"""

from masking.mask import Mask
from masking.perforation import Perforation
from masking.perforation import SOLID, PUNCHED
from masking.stencil import Stencil
