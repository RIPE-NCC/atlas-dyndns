#!/bin/bash

RUNDIR=~/run
V4MIN=500000
V6MIN=15000
DATADIR=~/data

echo Prefix updater started at `date`

wget -q -O $RUNDIR/prefixes.json --no-check-certificate "https://stat.ripe.net/data/ris-prefixes/data.json?resource=as3356&list_prefixes=true"
ls -l $RUNDIR/prefixes.json

~/atlas-dyndns/create-routed-list.py v4 < $RUNDIR/prefixes.json | sort | uniq | sort -R > $RUNDIR/v4.txt
~/atlas-dyndns/create-routed-list.py v6 < $RUNDIR/prefixes.json | sort | uniq | sort -R > $RUNDIR/v6.txt

v4l=`cat $RUNDIR/v4.txt | wc -l`
v6l=`cat $RUNDIR/v6.txt | wc -l`

echo Output sizes: v4 is $v4l, v6 is $v6l
if [ $v4l -gt $V4MIN -a $v6l -gt $V6MIN ]; then
    echo Moving files into place, effectively restarting the DNS service
    mkdir -p ~/data/topology4 ~/data/topology6
    mv $RUNDIR/v4.txt $DATADIR/topology4/
    mv $RUNDIR/v6.txt $DATADIR/topology6/
fi    

echo Prefix updater finished at `date`
