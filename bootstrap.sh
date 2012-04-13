# This script has to be sourced in a shell and is thus NOT executable.

# Helpers
have_pypkg() {
    ./bin/python -c "import $1" 2>/dev/null
}
need_pypkg() {
    have_pypkg "$1" && false || true
}

# Use or create virtualenv
if test -f ../bin/activate; then
    test -L bin -a -f bin/activate || ln -nfs ../bin .
elif test ! -f ./bin/activate; then
    python -c "import urllib2; open('virtualenv.py', 'w').write(\
        urllib2.urlopen('https://raw.github.com/pypa/virtualenv/master/virtualenv.py').read())"
    deactivate 2>/dev/null || true
    python virtualenv.py --system-site-packages . || return 1
fi

export DEBFULLNAME=pyroscope
export DEBEMAIL=pyroscope.project@gmail.com

grep DEBFULLNAME bin/activate >/dev/null || cat >>bin/activate <<EOF
export DEBFULLNAME=$DEBFULLNAME
export DEBEMAIL=$DEBEMAIL
EOF

. bin/activate || return 1

# Preconditions
ok=true
which montage >/dev/null || \
    { echo "ERROR: You MUST install ImageMagick (e.g. 'apt-get install imagemagick')!"; ok=false; }
which ffmpeg >/dev/null || \
    { echo "ERROR: You MUST install ffmpeg (e.g. 'apt-get install ffmpeg')!"; ok=false; }
which flac >/dev/null || \
    { echo "ERROR: You MUST install FLAC support (e.g. 'apt-get install flac')!"; ok=false; }

# PyWaveform
have_pypkg waveform || test -f /usr/include/mpg123.h || \
    { echo "ERROR: You MUST install mpg123 headers (e.g. 'apt-get install libmpg123-dev')!"; ok=false; }
have_pypkg waveform || test -f /usr/include/sndfile.h || \
    { echo "ERROR: You MUST install sndfile headers (e.g. 'apt-get install libsndfile1-dev')!"; ok=false; }

# numpy / scipy
have_pypkg scipy || which gfortran >/dev/null || \
    { echo "ERROR: You MUST install GNU fortran (e.g. 'apt-get install gfortran')!"; ok=false; }
have_pypkg numpy || test -d /usr/include/atlas || \
    { echo "ERROR: You MUST install ATLAS headers (e.g. 'apt-get install libatlas-dev')!"; ok=false; }
have_pypkg numpy || test -f /usr/lib/liblapack.a || \
    { echo "ERROR: You MUST install the LAPACK libraries (e.g. 'apt-get install liblapack-dev')!"; ok=false; }

$ok || { echo "FATAL: Fix above dependency errors first!"; return 1; }

# Tools
./bin/easy_install -U "setuptools>=0.6c11" || return 1
./bin/easy_install -U "paver>=1.0.1" || return 1
./bin/easy_install -U "nose>=1.0" || return 1
./bin/easy_install -U "yolk>=0.4.1" || return 1
./bin/easy_install -U "bpython" || return 1

# Dependencies
have_pypkg waveform || easy_install -U https://github.com/superjoe30/PyWaveform/zipball/master || :
have_pypkg numpy || easy_install numpy || :
have_pypkg matplotlib || easy_install matplotlib || :
have_pypkg scipy || easy_install scipy || :

./bin/paver develop -U

