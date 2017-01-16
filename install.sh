sudo apt-get install git build-essential python-pip python-dev python-pygame flex bison -y
sudo pip install flask
git clone https://github.com/atenart/dtc
cd dtc
make
sudo  make install PREFIX=/usr
cd ..
git clone git://github.com/xtacocorex/CHIP_IO.git
cd CHIP_IO
sudo python setup.py install
cd ..
sudo rm -rf CHIP_IO
