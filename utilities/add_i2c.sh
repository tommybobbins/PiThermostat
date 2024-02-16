echo "Allowing I2C"
/bin/rm -f /etc/modprobe.d/raspi-blacklist.conf
utilities/edit_file.sh /etc/modules i2c-dev
