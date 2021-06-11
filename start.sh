#!/bin/csh -f

# This loads the most minimalistic Cadence environment
# and then starts Virtuoso. Running in a subshell suppresses
# messages like [PID] or Done. And all output is redirected
# to /dev/null.
(module load 2021/cadence/Cadence2021_eda; virtuoso >& /dev/null &)
