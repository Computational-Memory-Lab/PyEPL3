"""
Configuration file for PairAssoDevon experiment

This config file sets parameters for the paired associate memory experiment.
"""

from pyepl3 import Key

# Experiment structure
NLISTS = 1  # Number of study-test lists
RUN_PRACTICE = 1  # Whether to run practice (1) or not (0)
NPAIRS = 16  # Number of word pairs per list

# Timing parameters (in milliseconds)
PRES_TIME = 2000  # Word presentation duration
IPI_lower = 500   # Inter-pair interval lower bound
IPI_upper = 800  # Inter-pair interval upper bound

# Distractor parameters
NDIST = 5  # Number of distractor problems (0 = no distractor)
D_RESP_TIME = 5000  # Response time for each distractor problem
D_BLANK_TIME = 100  # Blank time between distractor problems
DIST_MIN = 1  # Minimum number in math problems
DIST_MAX = 9  # Maximum number in math problems

# Test/recognition parameters
C_RESP_TIME = 5000  # Response time for recognition test
C_BLANK_TIME = 500  # Blank time between test trials

# Response keys
keyLeft = "Z"  # Left response key
keyRight = "/"  # Right response key (forward slash)

# Display parameters
fullscreen = False  # Run in windowed mode for testing
resolution = (1024, 768)  # Screen resolution
