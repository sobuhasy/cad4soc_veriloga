#!/bin/tcsh

echo $USER
ssh -XY -t $USER@talentix "cd ~/Desktop/cad4soc_veriloga;python performance_python.py"

exit 0 


