######!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import  division
# This to be sure that the result of the division of integers is a real, not an integer
from __future__ import absolute_import
from __future__ import print_function

# Import modules
import sys
import os

from . _version import __version__

# Import all the functions
__all__ = ['pyThGIS']

#from .text import joke
#from datathwritetools import writeheader_th, writecenterlineheader, writedata
from .pyThGIS import *

