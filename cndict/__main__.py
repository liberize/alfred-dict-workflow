#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cndict import lookup

if len(sys.argv) < 3:
    print 'usage: python cndict <dict> <word>'
    sys.exit(1)

result = lookup(*(sys.argv[1:]))
print '\n'.join(result)
