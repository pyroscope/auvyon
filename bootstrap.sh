# This script has to be sourced in a shell and is thus NOT executable.

# Preconditions
which virtualenv >/dev/null || \
    { echo "ERROR: You MUST install Python virtualenv (e.g. 'apt-get install python-virtualenv')!"; exit 1; }
which montage >/dev/null || \
    { echo "ERROR: You MUST install ImageMagick (e.g. 'apt-get install imagemagick')!"; exit 1; }
which ffmpeg >/dev/null || \
    { echo "ERROR: You MUST install ffmpeg (e.g. 'apt-get install ffmpeg')!"; exit 1; }
which flac >/dev/null || \
    { echo "ERROR: You MUST install FLAC support (e.g. 'apt-get install flac')!"; exit 1; }

test -f /usr/include/mpg123.h || \
    { echo "ERROR: You MUST install mpg123 headers (e.g. 'apt-get install libmpg123-dev')!"; exit 1; }
test -f /usr/include/sndfile.h || \
    { echo "ERROR: You MUST install sndfile headers (e.g. 'apt-get install libsndfile1-dev')!"; exit 1; }

# Use or create virtualenv
if test -f ../bin/activate; then
    test -L bin -a -f bin/activate || ln -nfs ../bin .
elif test ! -f ./bin/activate; then
    deactivate 2>/dev/null || true
    virtualenv --no-site-packages . || return 1
fi

export DEBFULLNAME=pyroscope
export DEBEMAIL=pyroscope.project@gmail.com

grep DEBFULLNAME bin/activate || cat >>bin/activate <<EOF
export DEBFULLNAME=$DEBFULLNAME
export DEBEMAIL=$DEBEMAIL
EOF

. bin/activate || return 1

# Tools
./bin/easy_install -U "setuptools>=0.6c11" || return 1
./bin/easy_install -U "paver>=1.0.1" || return 1
./bin/easy_install -U "nose>=1.0" || return 1
./bin/easy_install -U "yolk>=0.4.1" || return 1

# Dependencies
easy_install -U https://github.com/superjoe30/PyWaveform/zipball/master

./bin/paver develop -U

