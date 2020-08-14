set -ex

deb_url_base="https://download.foldingathome.org/releases/public/release/fahclient/debian-testing-64bit/v7.4/";
deb_file_name="fahclient_7.4.4_amd64.deb";
deb_url="${deb_url_base}${deb_file_name}";

cd /tmp;
if [ ! -f "${deb_file_name}" ]; then
  wget --quiet $deb_url;
fi
echo -e 'user\n1234\n6789\n3\nyes\n' | sudo dpkg -i --force-depends $deb_file_name;