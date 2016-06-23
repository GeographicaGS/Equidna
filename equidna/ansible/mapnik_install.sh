
sudo yum -y install make gcc47 gcc-c++ bzip2-devel libpng-devel libtiff-devel zlib-devel libjpeg-devel libxml2-devel python-setuptools git-all python-nose python27-devel python27 proj-devel proj proj-epsg proj-nad freetype-devel freetype libicu-devel libicu harfbuzz-devel harfbuzz

# install optional deps
sudo yum -y install gdal-devel gdal postgresql-devel sqlite-devel sqlite libcurl-devel libcurl cairo-devel cairo pycairo-devel pycairo

JOBS=`grep -c ^processor /proc/cpuinfo`

# build recent boost
export BOOST_VERSION="1_56_0"
export S3_BASE="http://mapnik.s3.amazonaws.com/deps"
curl -O ${S3_BASE}/boost_${BOOST_VERSION}.tar.bz2
tar xf boost_${BOOST_VERSION}.tar.bz2
cd boost_${BOOST_VERSION}
./bootstrap.sh
./b2 -d1 -j${JOBS} \
    --with-thread \
    --with-filesystem \
    --with-python \
    --with-regex -sHAVE_ICU=1  \
    --with-program_options \
    --with-system \
    link=shared \
    release \
    toolset=gcc \
    stage
sudo ./b2 -j${JOBS} \
    --with-thread \
    --with-filesystem \
    --with-python \
    --with-regex -sHAVE_ICU=1 \
    --with-program_options \
    --with-system \
    toolset=gcc \
    link=shared \
    release \
    install
cd ../
rm -R boost_$
cd ../
rm -R boost_${BOOST_VERSION}*
# set up support for libraries installed in /usr/local/lib
sudo bash -c "echo '/usr/local/lib' > /etc/ld.so.conf.d/boost.conf"
sudo ldconfig

# mapnik
wget -O mapnik-3.0.9.tar.gz https://github.com/mapnik/mapnik/archive/v3.0.9.tar.gz
tar xvzf mapnik-3.0.9.tar.gz
cd mapnik-3.0.9
./configure
make
make test-local
sudo make install
cd ..
rm -R mapnik-3.0.9.*

# Optional install Python bindings
pip install mapnik
