# can I exclude empty files?
cd $(dirname $0)
exec ./bin/nosetests --with-coverage --cover-package=servequnit --cover-html --cover-html-dir=./coverage-output --cover-tests "$@"
