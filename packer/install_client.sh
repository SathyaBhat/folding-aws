#!/bin/bash

set -ex

deb_url_base="https://download.foldingathome.org/releases/public/release/fahclient/debian-testing-64bit/v7.4/";
deb_file_name="fahclient_7.4.4_amd64.deb";
deb_url="${deb_url_base}${deb_file_name}";

cd /tmp;
if [ ! -f "${deb_file_name}" ]; then
  wget --quiet $deb_url;
fi
echo -e 'user\nteam\n123\n1\nyes\n' | sudo dpkg -i --force-depends $deb_file_name;

sed "s/passkey v=''/passkey v='$fah_passkey'/; \
     s/team v=''/team v='$fah_team'/; \
     s/user v=''/user v='$fah_user'/" config.xml;

sudo mv config.xml /etc/fahclient/config.xml

sudo service FAHClient restart;
