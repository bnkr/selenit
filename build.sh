#!/bin/sh
# Setup for the lazy.
set +e
cd $(dirname $0)
virtualenv --python /usr/bin/python2.7 venv
./venv/bin/pip install selenium

bin=bin/vselenibench
python="$(pwd)/venv/bin/python"
echo "#!/bin/sh" > $bin
echo "exec \"$python\" \"$(pwd)/bin/selenibench\" \"\$@\"" >> $bin
chmod +x $bin
