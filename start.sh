#!/bin/tcsh -f
source $home/.cshrc

echo "CADENCE VIRTUOSO LAUNCHER"
echo ""

ssh -X amnesix 'tcsh -s' < /home/$USER/cad4soc_veriloga/virtuoso.sh

