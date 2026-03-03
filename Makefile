# Makefile for installing the Marco file explorer

PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
TARGET = $(BINDIR)/marco
SRC    = ./marco.py

install: $(BINDIR)
	chmod +x $(SRC) && cp $(SRC) $(TARGET)

uninstall:
	rm -f $(TARGET)

.PHONY: install uninstall
