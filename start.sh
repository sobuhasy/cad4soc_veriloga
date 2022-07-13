#!/bin/tcsh -f
source $home/.cshrc

set SIMSERVER = "amnesix.ies.e-technik.tu-darmstadt.de"

echo "CADENCE VIRTUOSO LAUNCHER"
echo ""

# first we have to fix the permissions :(
chmod go-w "/home/$user"
if ( -d ~/.ssh ) then
    chmod 700 ~/.ssh
endif

# so if there's no SSH key we'll generate one
if (! -e ~/.ssh/id_rsa) then
    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
endif

# let's check if our key is in the authorized_keys file and if
# not we'll add it
grep -f ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys >& /dev/null
if ($? != 0) then
    cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys
endif

# connect to the simulation server and add its host fingerprint
# without prompting the user
ssh -o StrictHostKeyChecking=no -X -l "$user" "$SIMSERVER" 'tcsh -s' < /home/$USER/cad4soc_veriloga/virtuoso.sh
