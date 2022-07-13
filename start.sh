#!/bin/tcsh -f
source $home/.cshrc

set SIMSERVER = "amnesix.ies.e-technik.tu-darmstadt.de"

echo "CADENCE VIRTUOSO LAUNCHER"
echo ""

# so if there's no SSH key we'll deal with that...
if (! -e ~/.ssh/id_rsa) then
    # first we have to fix the permissions :(
    chmod go-w "/home/$user"
    if (! -d ~/.ssh ) then
        mkdir ~/.ssh
    endif
    chmod 700 ~/.ssh
    # generate SSH key
    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
    # add it so it can be used for authorization
    cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys

# connect to the simulation server and add its host fingerprint
# without prompting the user
ssh -o StrictHostKeyChecking=no -X -l "$user" "$SIMSERVER" 'tcsh -s' < /home/$USER/cad4soc_veriloga/virtuoso.sh
