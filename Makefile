# NAME
APP_NAME=pyqt-mail-checker
#VERSION
VERSION=1.12.55

#PATH
DESTDIR=/usr
APPS_DIR=$(DESTDIR)/share/
EXEC=$(DESTDIR)/bin/
APP=$(APPS_DIR)$(APP_NAME)/
DESKTOP=$(APPS_DIR)applications/
APP_DOC=$(APPS_DIR)doc/$(APP_NAME)-$(VERSION)/
APP_ICONS=$(APPS_DIR)icons/hicolor/32x32/apps/
CODE=contents/code
ICONS=contents/icons

#COMMANDS
INSTALL=install -D -m 0644 -p
INSTALL_EXEC=install -D -m 0755 -p
LRELEASE=/usr/bin/lrelease-qt4

ru.qm:
	$(LRELEASE) $(CODE)/misc/ru.ts -qm $(CODE)/misc/ru.qm

build: ru.qm
	@echo "Nothing to build"

install: build
	# *.desktop
	$(INSTALL) $(APP_NAME).desktop $(DESKTOP)$(APP_NAME).desktop
	# EXEC
	$(INSTALL_EXEC) $(APP_NAME).py $(EXEC)$(APP_NAME).py
	# SOURCE
	$(INSTALL) VERSION $(APP)VERSION
	cp -pr $(CODE)/* $(APP)
	mkdir -p $(APP_ICONS)
	cp -p $(ICONS)/mailChecker* $(APP_ICONS)
	# prepare DOCS
	cp -p $(ICONS)/Licenses .
	# tree $(DESTDIR)

clean:
	rm -rf $(DESKTOP)$(APP_NAME).desktop
	rm -rf $(EXEC)$(APP_NAME).sh
	rm -rf $(APP)
	rm -rf $(APP_ICONS)mailChecker*
	rm -rf $(APP_DOC)
