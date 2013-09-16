# can I exclude empty files?
exec ./bin/nosetests --with-coverage --cover-package=servequnit --cover-html --cover-html-dir=coverage-output "$@"
