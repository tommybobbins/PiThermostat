#redis-cli -h localhost set "temperature/attic/sensor" "15.3"
#redis-cli -h localhost set "temperature/attic/multiplier" "1"
#redis-cli -h localhost set "temperature/attic/zone" "inside"
#redis-cli -h localhost set "temperature/barab/sensor" "15.3"
#redis-cli -h localhost set "temperature/barab/multiplier" "1"
#redis-cli -h localhost set "temperature/barab/zone" "inside"
#redis-cli -h localhost set "temperature/cellar/sensor" "15.3"
#redis-cli -h localhost set "temperature/cellar/multiplier" "1"
#redis-cli -h localhost set "temperature/cellar/zone" "inside"
#redis-cli -h localhost set "temperature/damocles/sensor" "15.3"
#redis-cli -h localhost set "temperature/damocles/multiplier" "1"
#redis-cli -h localhost set "temperature/damocles/zone" "inside"
#redis-cli -h localhost set "temperature/eden/sensor" "10.0"
#redis-cli -h localhost set "temperature/eden/multiplier" "1"
#redis-cli -h localhost set "temperature/eden/zone" "outside"
#redis-cli -h localhost set "temperature/forno/sensor" "10.0"
#redis-cli -h localhost set "temperature/forno/multiplier" "1"
#redis-cli -h localhost set "temperature/forno/zone" "outside"
redis-cli -h localhost set "temperature/weather" "10.0"
redis-cli -h localhost set "temperature/userrequested" "10.0"
redis-cli -h localhost set "temperature/failover" "10.0"
redis-cli -h localhost set "temperature/calendar" "10.0"
redis-cli -h localhost set "temperature/outside/rollingmean" "10.0"
redis-cli -h localhost set "temperature/outside/weightedmean" "10.0"
redis-cli -h localhost set "temperature/inside/weightedmean" "15.0"
redis-cli -h localhost set "boiler/4hourtimeout" "False"
#redis-cli -h localhost hset espsensor_name 18:fe:34:f4:d2:77 "damocles"
#redis-cli -h localhost hset espsensor_mult 18:fe:34:f4:d2:77 1.0
#redis-cli -h localhost hset espsensor_locn 18:fe:34:f4:d2:77 "inside"
