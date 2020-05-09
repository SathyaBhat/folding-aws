#!/bin/bash

set -ex

deb_url_base="https://download.foldingathome.org/releases/public/release/fahclient/debian-testing-64bit/v7.4/";
deb_file_name="fahclient_7.4.4_amd64.deb";
deb_url="${deb_url_base}${deb_file_name}";

cd /tmp;
if [ ! -f "${deb_file_name}" ]; then
  wget --quiet $deb_url;
fi
echo -e 'user\n1234\n6789\n3\nyes\n' | sudo dpkg -i --force-depends $deb_file_name;

sed -i "s/passkey v=''/passkey v='$fah_passkey'/; \
     s/team v=''/team v='$fah_team'/; \
     s/user v=''/user v='$fah_user'/" /tmp/config.xml;

sudo service FAHClient stop;
sleep 10;
sudo mv /tmp/config.xml /etc/fahclient/config.xml;
sudo chown fahclient:root /etc/fahclient/config.xml;
sleep 10;
sudo service FAHClient start;

echo "small test to see if the config file has been correctly generated";
grep team /etc/fahclient/config.xml;
