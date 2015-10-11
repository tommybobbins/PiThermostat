BINDIR ?=/usr/local/bin/
CONFIGDIR ?=/etc
CONFIGURE ?=./configure
MAKE_INSTALL ?=sudo make install
AUTOMAKE ?= automake --add-missing
ACLOCAL ?= aclocal
MAKE ?=make

raspi433:
	git clone https://github.com/tommybobbins/Raspi_433
	cd Raspi_433/TRANSMITTER && $(MAKE_INSTALL)

adafruit:
	git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
	sudo cp -rp Adafruit-Raspberry-Pi-Python-Code /usr/local/lib/python2.7/site-packages/

install: raspi433 adafruit
	@echo "Installing prereqs"
	sudo apt-get install -y python-dev
	sudo apt-get install -y redis-server python-redis weather-util apache2
	sudo apt-get install -y python-django libapache2-mod-wsgi
	sudo pip install --upgrade pytz evdev redis configparser
	sudo pip install apiclient urllib3 django-icons-tango django-happenings
	@echo "Installing into $(BINDIR)"
	sudo cp calculate_temps.py  $(BINDIR)
	sudo cp django_happenings.py  $(BINDIR)
	sudo cp process_temperatures.py $(BINDIR)
	sudo cp utilities/temp_stats.py $(BINDIR)
	sudo cp utilities/read_redis.py $(BINDIR)
	sudo cp utilities/retrieve_weather.sh $(BINDIR)
	sudo cp utilities/parse_weather.py $(BINDIR)
	@echo "Setting executable permissions"
	sudo chmod 755 $(BINDIR)/*.py
	sudo chmod 755 $(BINDIR)/*.sh
	@echo "Copying configuration file"
	sudo cp etc/pithermostat.conf /etc
	@echo "Copying init script"
	sudo cp systemd/*.service /etc/systemd/system/
	@echo "Setting systemd"
	sudo systemctl enable murunner.service  
	sudo systemctl enable redis_sensor.service
	sudo systemctl enable thermostat.service
	@echo "Installing Django"
	sudo mkdir -p /usr/local/django
	sudo cp -rp django/* /usr/local/django/
	sudo python /usr/local/django/manage.py syncdb
	sudo chmod 666 /usr/local/django/home.db
	@echo "Modifying hosts file"
	sudo sed -i "s/raspberrypi/raspberrypi 433board 433host/g" /etc/hosts
	@echo "Initialized redis queues"
	utilities/setup_keys.sh
	@echo "Adding cron job"
	(crontab -u pi -l; cat utilities/crontab) | crontab -u pi -
	@echo "Copying apache2 configuration"
	sudo cp -rp etc/apache2/* /etc/apache2/
	@echo "Starting processes"
	service murunner start
	service redis_sensor start
	service thermostat start
	service apache2 restart
	@echo "Install complete"

clean:
	sudo rm $(BINDIR)calculate_temps.py
	sudo rm $(BINDIR)django_happenings.py
	sudo rm $(BINDIR)process_temperatures.py
	sudo rm $(BINDIR)calculate_temps.py
	sudo rm $(BINDIR)read_redis.py
	sudo rm $(BINDIR)retrieve_weather.sh
	sudo rm $(BINDIR)parse_weather.py
	sudo rm -rf Adafruit-Raspberry-Pi-Python-Code
	sudo rm -rf Raspi_433
	sudo rm /etc/pithermostat.conf 
	sudo rm -rf /usr/local/django
	sudo rm -rf /usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code
	sudo insserv -r murunner.sh
	sudo insserv -r thermostat.sh
	sudo insserv -r redis_sensor.sh
	sudo systemctl disable thermostat.service
	sudo systemctl disable murunner.service
	sudo systemctl disable redis_sensor.service
	sudo rm /etc/systemd/system/murunner.service 
	sudo rm /etc/systemd/system/thermostat.service 
	sudo rm /etc/systemd/system/redis_sensor.service 
	sudo rm /etc/init.d/murunner.sh
	sudo rm /etc/init.d/thermostat.sh
	sudo rm /etc/init.d/redis_sensor.sh
	@echo "Removal complete"
