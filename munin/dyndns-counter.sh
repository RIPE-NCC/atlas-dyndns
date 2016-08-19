#!/bin/sh

case $1 in
    config)
        cat <<EOF
graph_title Atlas DYNDNS counters
graph_vlabel Queries per second
graph_category Atlas
graph_args -l 0
graph_info Amount of queries per second for IPv4/IPv6/unknown hosts
EOF

	for i in c4 c6 cx; do
	        echo $i.label $i
	        echo $i.type DERIVE
	        echo $i.min 0
	        echo $i.draw LINE1
	        echo $i.info Queries for $i hosts
	done

        exit 0
                ;;
    autoconf)
                echo yes
                exit 0
esac

if [ -f /var/log/atlas/count.log ]; then
    cx=`stat -c '%s' /var/log/atlas/count.log`
else
    cx=0
fi

if [ -f /var/log/atlas/count4.log ]; then
    c4=`stat -c '%s' /var/log/atlas/count4.log`
else
    c4=0
fi

if [ -f /var/log/atlas/count6.log ]; then
    c6=`stat -c '%s' /var/log/atlas/count6.log`
else
    c6=0
fi


echo c4.value $c4
echo c6.value $c6
echo cx.value $cx

exit 0
