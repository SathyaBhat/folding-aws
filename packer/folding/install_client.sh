#!/bin/bash

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
