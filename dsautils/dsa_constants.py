"""Definition of physical and DSA-110-specific constants that are commonly used in Python scripts

    It is recommended that these be imported as

        import dsa_constants as CONSTS

    and used as, e.g.,

        lambda = CONSTS.C / (112.0 * CONSTS.GHZ)
"""

import math

# ------------------------------------------------------------------------------
# Physical constants

# Data from "The NIST Reference on Constants, Units, and Uncertainty, from
# CODATA Recommended Values of the Fundamental Constants" - 2002, by Peter
# J. Mohr and Barry N. Taylor, National Institute of Standards and Technology.
#
# Unless otherwise noted, all constants are in SI units

# Speed of light
# Units: m s^-1
C = 299792458.0

# Newton's gravitational constant
# Units: m^3 kg^-1 s^-1
G = 6.6742E-11

# Boltzmann's constant
# Units: J K^-1
K = 1.3806505E-23

# Planck's constant
# Units: J s
H = 6.6260693E-34

# Absolute zero
# Units: degrees Celsius
ABS_ZERO = -273.15

# Individual gas constant for water
# Units: J kg^-1 K^-1
R_WATER = 461.5

# jansky
# W m^-2 Hz^-1
JY = 1.0E-26

# Conversion of nanoseconds of delay to meters of delay
NANOSEC_PER_METER = 3.33564095198

# ------------------------------------------------------------------------------
# Unit conversions

# Length
# Base unit: m
METER = 1.0
MM = 1000.0
CM = 100.0
KM = 0.001

# Frequency
# Base unit: Hz
HERTZ = 1.0
KHZ = 1.0E3
MHZ = 1.0E6
GHZ = 1.0E9

# Angles
# Base unit: radian
RADIAN = 1.0
DEG = math.pi / 180.0
ARCMIN = math.pi / 10800.0
ARCSEC = math.pi / 648000.0

# Time
# Base unit: s
SECOND = 1.0
MINUTE = 60
HOUR = 3600
DAY = 86400
