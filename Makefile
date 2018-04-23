CXX := /usr/bin/g++
CXXFLAGS := -O2 -std=c++11 -Wall -Wextra -Wshadow -Wconversion -pedantic

all: xx

xx: xx.cpp
	$(CXX) $(CXXFLAGS) -lmysqlcppconn -lcryptopp -I . -o xx xx.cpp

clean:
	rm xx

install:
	cp xx /var/www/html/xx.cgi
	cp html /var/www/html
	cp style.css /var/www/html/style.css
	cp xx.py /var/www/html/xx.py
	cp script.js /var/www/html/script.js

uninstall:
	rm /var/www/html/xx.cgi
	rm /var/www/html/html
	rm /var/www/html/style.css
	rm /var/www/html/xx.py
	rm /var/www/html/script.js

.PHONY: all clean install uninstall
