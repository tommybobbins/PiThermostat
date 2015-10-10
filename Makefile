BINDIR ?=/usr/local/bin/
CONFIGDIR ?=/etc

install:
	@echo "Installing prereqs"
	apt-get install -y python-dev
	apt-get install -y redis-server python-redis weather-util apache2
	apt-get install -y python-django libapache2-mod-wsgi
	pip install --upgrade pytz evdev redis configparser
	pip install apiclient urllib3 django-icons-tango django-happenings
	git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
	cp -rp Adafruit-Raspberry-Pi-Python-Code /usr/local/lib/python2.7/site-packages/
	@echo "Installing into $(BINDIR)"
	cp calculate_temps.py  $(BINDIR)
	cp django_happenings.py  $(BINDIR)
	cp process_temperatures.py $(BINDIR)
	cp utilities/temp_stats.py $(BINDIR)
	cp utilities/read_redis.py $(BINDIR)
	cp utilities/retrieve_weather.sh $(BINDIR)
	cp utilities/parse_weather.py $(BINDIR)
	@echo "Setting executable permissions"
	chmod 755 $(BINDIR)/*.py
	chmod 755 $(BINDIR)/*.sh
	@echo "Copying configuration file"
	cp etc/pithermostat.conf /etc
	@echo "Copying init script"
	cp init.d/murunner.sh $(CONFIGDIR)/init.d
	cp init.d/thermostat.sh $(CONFIGDIR)/init.d/
	cp init.d/redis_sensor.sh $(CONFIGDIR)/init.d/
	@echo "Setting runlevels"
	insserv murunner.sh
	insserv thermostat.sh
	insserv redis_sensor.sh
	@echo "Installing Django"
	mkdir -p /usr/local/django
	cp -rp django/* /usr/local/django/
	python /usr/local/django/manage.py syncdb
	chmod 666 /usr/local/django/home.db
	@echo "Modifying hosts file"
	sed -i "s/raspberrypi/raspberrypi 433board 433host/g" /etc/hosts
	@echo "Initialized redis queues"
	utilities/setup_keys.sh
	@echo "Adding cron job"
	(crontab -u pi -l; cat utilities/crontab) | crontab -u pi -
	@echo "Copying apache2 configuration"
	cp -rp etc/apache2/* /etc/apache2/
	@echo "Downloading 433 code"
	git clone https://github.com/tommybobbins/Raspi_433
	cd Raspi_433/bcm2835-1.42
	make install
	cd ../TRANSMITTER
	make drayton
	make bgas
	cp bgas $(BINDIR) 
	chmod 755 $(BINDIR)/bgas
	cp drayton $(BINDIR) 
	chmod 755 $(BINDIR)/drayton
	cd ../../
	@echo "Starting processes"
	/etc/init.d/redis_sensor.sh start
	/etc/init.d/murunner.sh start
	/etc/init.d/thermostat.sh start
	/etc/init.d/apache2 restart
	@echo "Install complete"

clean:
	insserv -r murunner.sh
	insserv -r thermostat.sh
	insserv -r redis_sensor.sh
	rm /etc/init.d/murunner.sh
	rm /etc/init.d/thermostat.sh
	rm /etc/init.d/redis_sensor.sh
	rm /etc/pithermostat.conf 
	rm $(BINDIR)calculate_temps.py
	rm $(BINDIR)django_happenings.py
	rm $(BINDIR)process_temperatures.py
	rm $(BINDIR)calculate_temps.py
	rm $(BINDIR)read_redis.py
	rm $(BINDIR)retrieve_weather.sh
	rm $(BINDIR)parse_weather.py
	rm -rf /usr/local/django
	rm -rf /usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code
	@echo "Removal complete"
