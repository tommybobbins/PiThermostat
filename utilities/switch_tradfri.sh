#!/bin/bash
#switches tradfri appliances on (1) or off (0)
ITEM=$1
STATE=$2
#echo $ITEM $STATE
/usr/local/bin/coap-client -m put -u "PI433" -k "mysupercoolpass" -e '{ "3311": [{ "5850": '$STATE' }] }' "coaps://192.168.0.63:5684/15001/${ITEM}"
