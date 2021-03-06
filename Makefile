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
	sudo apt-get update
	sudo apt-get install -y python-dev python-smbus python-pip python3-pip
	git clone https://github.com/adafruit/Adafruit_Python_GPIO.git 
	cd Adafruit_Python_GPIO && /usr/bin/python3 setup.py install

install: adafruit
	@echo "Installing prereqs"
	sudo apt-get update
        sudo apt-get -y upgrade
	sudo apt-get install -y redis-server python-redis weather-util apache2
	sudo apt-get install -y python-django libapache2-mod-wsgi
	sudo apt-get install -y sqlite3
	sudo pip install --upgrade pytz evdev redis configparser
	sudo pip install apiclient urllib3 django-icons-tango django-happenings
	@echo "Installing into $(BINDIR)"
	sudo cp calculate_temps.py  $(BINDIR)
	sudo cp django_happenings.py  $(BINDIR)
	sudo cp process_temperatures.py $(BINDIR)
	sudo cp utilities/temp_stats.py $(BINDIR)
	sudo cp utilities/read_redis.py $(BINDIR)
	sudo cp utilities/redis_sensor.py $(BINDIR)
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
	sudo cp -rp utilities/happenings_url.py /usr/local/lib/python2.7/dist-packages/happenings/urls.py
	sudo python /usr/local/django/manage.py migrate
	sudo chmod 666 /usr/local/django/home.db
	sudo chown www-data:www-data /usr/local/django/
	sudo chmod g+w /usr/local/django/
	@echo "Modifying hosts file"
	printf '\n127.0.0.1 433board 433host\n' | sudo tee -a /etc/hosts > /dev/null
	@echo "Modifying redis-server to listen on all ports"
	sudo sed -i "s/^bind/#bind/g" /etc/redis/redis.conf
	sudo service redis-server restart
	@echo "Initialized redis queues"
	utilities/setup_keys.sh
	@echo "Adding cron job"
	(crontab -u $(USER) -l; cat utilities/crontab) | crontab -u $(USER) -
	@echo "Copying apache2 configuration"
	sudo cp -rp etc/apache2/* /etc/apache2/
	@echo "Modifying KeepAlive Off"
	sudo sed -i "s/^KeepAlive On/KeepAlive Off/g" /etc/apache2/apache2.conf
	@echo "Starting processes"
	sudo service murunner start
	sudo service redis_sensor start
	sudo service thermostat start
	sudo service apache2 restart
	@echo "Install complete"

clean:
	sudo rm -rf Raspi_433
	sudo rm -rf Adafruit-Raspberry-Pi-Python-Code
	sudo rm $(BINDIR)calculate_temps.py
	sudo rm $(BINDIR)django_happenings.py
	sudo rm $(BINDIR)process_temperatures.py
	sudo rm $(BINDIR)calculate_temps.py
	sudo rm $(BINDIR)read_redis.py
	sudo rm $(BINDIR)retrieve_weather.sh
	sudo rm $(BINDIR)parse_weather.py
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
