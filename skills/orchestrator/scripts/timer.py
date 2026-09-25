#!/usr/bin/env python3
"""Sleep, then print one line. The orchestrator runs it in the background as a watchdog:
when it exits, the session wakes up and checks whether the labelled task is still running.

  timer.py SECONDS LABEL...     e.g.  timer.py 10800 T04
"""
import sys
import time

if len(sys.argv) < 3:
    sys.exit("usage: timer.py SECONDS LABEL")
time.sleep(float(sys.argv[1]))
print(f"TIMER {' '.join(sys.argv[2:])}")
