# Builds the pxl package with dpkg-deb from the /package directory to pxl.deb

SHELL := /bin/bash
build:
	rm -rf package/usr/lib/pxl
	mkdir -p package/usr/lib/pxl
	cp main.py package/usr/lib/pxl/
	cp -r pxl package/usr/lib/pxl/
	cp -r design package/usr/lib/pxl/
	python3.7 -m venv package/usr/lib/pxl/venv;
	\
	source package/usr/lib/pxl/venv/bin/activate; \
	pipenv sync; \
	deactivate; \
	\
	dpkg-deb -b package/ pxl.deb
	@echo "You can now install pxl by running 'sudo dpkg -i pxl.deb'"

clean:
	rm -rf package/usr/lib/pxl



