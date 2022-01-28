BINDIR ?=/usr/local/bin/
CONFIGDIR ?=/etc
DJANGODIR ?=/usr/local/django/
CONFIGURE ?=./configure
MAKE_INSTALL ?=sudo make install
DOW :=$(shell date +%a)
AUTOMAKE ?= automake --add-missing
ACLOCAL ?= aclocal
MAKE ?=make

.PHONY: install raspi433 i2c osd daemons binaries django

i2c: 
	@echo "Allowing I2C"
	utilities/add_i2c.sh

os: 
	@echo "Installing prereqs"
	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt-get install -y redis-server python3-redis weather-util apache2
	sudo apt-get install -y libapache2-mod-wsgi-py3
	sudo apt-get install -y sqlite3 python3-bs4 python3-dateutil
	sudo apt-get install -y python-dev python3-smbus python3-pip
	@echo "Modifying redis-server to listen on all ports"
	sudo sed -i "s/^bind/#bind/g" /etc/redis/redis.conf
	sudo sed -i "s/^protected-mode yes/protected-mode no/g" /etc/redis/redis.conf
	sudo service redis-server restart
	@echo "Initialized redis queues"
	utilities/setup_keys.sh
	@echo "Adding cron job"
	(crontab -u $(USER) -l; cat utilities/crontab) | crontab -u $(USER) -
	@echo "Copying apache2 configuration"
	sudo cp -rp etc/apache2/* /etc/apache2/
	sudo cp -rp etc/apache2/.htpasswd /etc/apache2/
	sudo chmod 600 /etc/apache2/.htpasswd
        sudo chown www-data:www-data /etc/apache2/.htpasswd
	@echo "Modifying KeepAlive Off"
	sudo sed -i "s/^KeepAlive On/KeepAlive Off/g" /etc/apache2/apache2.conf

binaries: 
	@echo "Installing into $(BINDIR)"
	sudo cp bin/relay_state.py $(BINDIR)
	sudo cp bin/calculate_temps.py  $(BINDIR)
	sudo cp bin/heating_water_cal.py  $(BINDIR)
	sudo cp bin/process_temperatures.py $(BINDIR)
	sudo cp bin/read_redis.py $(BINDIR)
	sudo cp utilities/temp_stats.py $(BINDIR)
	sudo cp utilities/redis_sensor.py $(BINDIR)
	sudo cp utilities/retrieve_weather.sh $(BINDIR)
	sudo cp utilities/parse_weather.py $(BINDIR)
	sudo cp utilities/mean_outsidetemp.py $(BINDIR)
	@echo "Setting executable permissions"
	sudo chmod 755 $(BINDIR)/*.py
	sudo chmod 755 $(BINDIR)/*.sh
	@echo "Copying systemd script"
	sudo cp systemd/*.service /etc/systemd/system/

locale:
	@echo "Copying configuration file"
	sudo cp etc/pithermostat.conf /etc
	sudo cp django_db/db.sqlite3 $(DJANGODIR)hotf/
	sudo chmod 666 $(DJANGODIR)/hotf/db.sqlite3
	sudo chown www-data:www-data $(DJANGODIR)
	@echo "Modifying hosts file"
	sudo hostnamectl set-hostname hotf
	sudo utilities/edit_file.sh /etc/hosts 127.0.0.1 433board 433host hotf

django: 
	@echo "Installing Django"
	sudo python3 -m pip install django bs4
	sudo python3 -m pip install redis
	sudo python3 -m pip install pytz evdev
	sudo python3 -m pip install apiclient urllib3 django-icons-tango django-scheduler
	sudo mkdir -p /usr/local/django
	sudo cp -rp django/* $(DJANGODIR)
	sudo python3 $(DJANGODIR)hotf/manage.py migrate
	sudo chmod 666 $(DJANGODIR)/hotf/db.sqlite3
	sudo chown www-data:www-data $(DJANGODIR)
	sudo chmod g+w $(DJANGODIR)

daemons: 
	@echo "Starting processes"
	sudo systemctl daemon-reload
	sudo systemctl enable apache2 --now
	sudo systemctl enable murunner --now
	sudo systemctl enable redis_sensor --now
	sudo systemctl enable thermostat --now

restart_daemons: 
	@echo "Restarting processes"
	sudo systemctl daemon-reload
	sudo systemctl restart apache2
	sudo systemctl restart murunner
	sudo systemctl restart redis_sensor
	sudo systemctl restart thermostat

tradfri: 
	@echo "Building tradfri"
	sudo cp utilities/switch_tradfri.sh $(BINDIR)
	git clone --recursive https://github.com/obgm/libcoap.git
	cd libcoap
	git checkout dtls
	git submodule update --init --recursive
	./autogen.sh
	./configure --disable-documentation --disable-shared
	make
	sudo make install


test:
	sudo bin/unit_test.py

backup:
	sudo tar zvcf /var/tmp/backup_$(DOW).tgz $(BINDIR) /etc/pithermostat.conf $(DJANGODIR) /etc/apache2/
	sudo cp $(DJANGODIR)hotf/hotf/settings.py /var/tmp/

upgrade: backup binaries django test restart_daemons
	sudo cp /var/tmp/settings.py $(DJANGODIR)/hotf/hotf/
	sudo chown -R www-data:www-data $(DJANGODIR)
	@echo "Upgrade done"

install: os i2c binaries locale django daemons upgrade 
	@echo "Install complete"
	@echo "Remember to set tradfri Pass in $(BINDIR)/switch_tradfri.sh"

clean:
	sudo rm -f $(BINDIR)/relay_state.py
	sudo rm -f $(BINDIR)/calculate_temps.py
	sudo rm -f $(BINDIR)/heating_water_cal.py
	sudo rm -f $(BINDIR)/process_temperatures.py
	sudo rm -f $(BINDIR)/temp_stats.py
	sudo rm -f $(BINDIR)/read_redis.py
	sudo rm -f $(BINDIR)/redis_sensor.py
	sudo rm -f $(BINDIR)/retrieve_weather.sh
	sudo rm -f $(BINDIR)/parse_weather.py
	sudo rm -f $(BINDIR)/switch_tradfri.sh
	sudo rm -f $(BINDIR)/mean_outsidetemp.py
	sudo rm -f /etc/pithermostat.conf 
	sudo rm -rf $(DJANGODIR)
	sudo systemctl disable --now thermostat.service
	sudo systemctl disable --now murunner.service
	sudo systemctl disable --now redis_sensor.service
	sudo rm -f /etc/systemd/system/murunner.service 
	sudo rm -f /etc/systemd/system/thermostat.service 
	sudo rm -f /etc/systemd/system/redis_sensor.service 
	sudo rm -f /etc/init.d/murunner.sh
	sudo rm -f /etc/init.d/thermostat.sh
	sudo rm -f /etc/init.d/redis_sensor.sh
	@echo "Removal complete"
