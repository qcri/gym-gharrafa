import os, sys
if 'SUMO_HOME' not in os.environ:
     os.environ["SUMO_HOME"]="/usr/share/sumo"
     #sys.path.append('SUMO_HOME')

tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
sys.path.append(tools)
sumoBinary = "/usr/bin/sumo"
sumoBinaryGUI = "/usr/bin/sumo-gui"
