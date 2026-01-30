"""
Configuration file for PairAssoDevon experiment - PyEPL2 Version

This config file sets parameters for the paired associate memory experiment.
"""

# Experiment structure
NLISTS = 3  # Number of study-test lists
RUN_PRACTICE = 2  # Whether to run practice list-pair (2) or not (0)
NPAIRS = 32  # Number of word pairs per list
NPAIRS_PRACTICE = 8 # Number of word pairs per practice list

# Timing parameters (in milliseconds)
PRES_TIME = 2000  # Word presentation duration
IPI_lower = 500   # Inter-pair interval lower bound
IPI_upper = 800  # Inter-pair interval upper bound

# Distractor parameters
NDIST = 8  # Number of arrow trials (0 = no distractor)
D_RESP_TIME = 2000  # Response time for each arrow trial
D_BLANK_TIME = 250  # Blank time between arrow trials
DIST_MIN = 1  # Minimum number in math problems
DIST_MAX = 9  # Maximum number in math problems

# Test/recognition parameters
C_RESP_TIME = 5000  # Response time for recognition test
C_BLANK_TIME = 250  # Blank time between test trials

# Response keys
keyLeft = "Z"  # Left response key
keyRight = "/"  # Right response key (forward slash)

# Display parameters
# Note: In PyEPL2, these are typically set via command line or experiment defaults
# fullscreen = True
# resolution = (1024, 768)

# TIPI questionnaire timeout (if used)
maxRTVVIQ = 30000
