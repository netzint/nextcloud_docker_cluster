#!/bin/bash
# by lukas.spitznagel@netzint.de

STATE_DB1=$(cat ./db01-data/grastate.dat | grep "safe_to_bootstrap:" | awk '{print $2}')
STATE_DB2=$(cat ./db02-data/grastate.dat | grep "safe_to_bootstrap:" | awk '{print $2}')

if [[ $STATE_DB1 == 0 ]] && [[ $STATE_DB2 == 0 ]]; then
  echo "Both databases are in slave mode... Thats wrong!"
  echo "Should I set database 1 to master?"
  echo -n "(y/n) "
  read answer
  if [[ "$answer" == "y" ]]; then
    sed -i 's/safe_to_bootstrap: 0/safe_to_bootstrap: 1/g' ./db01-data/grastate.dat
    echo "Set DB01 to master. Now try to start the Nextcloud-Cluster again."
  else
    echo "Okay, then you have to do it on your own!"
  fi
elif [[ $STATE_DB1 == 1 ]] && [[ $STATE_DB2 == 0 ]]; then
  echo "DB01 is master of the database cluster. Everything looks fine!"
elif [[ $STATE_DB1 == 0 ]] && [[ $STATE_DB2 == 1 ]]; then
  echo "DB02 is master of the database cluster. Everything looks fine!"
else
  echo "Something is wrong. Try to contact your nextcloud specialist!"
fi
