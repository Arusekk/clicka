CXX := /usr/bin/g++
CXXFLAGS := -O2 -std=c++11 -Wall -Wextra -Wshadow -Wconversion -pedantic

all: xx

xx: xx.o gen.o
	$(CXX) $(CXXFLAGS) xx.o gen.o -lmysqlcppconn -o xx

xx.o: xx.cpp
	$(CXX) $(CXXFLAGS) -c -o xx.o xx.cpp

gen.o: gen.cpp
	$(CXX) $(CXXFLAGS) -c -o gen.o gen.cpp

clean:
	rm xx.o gen.o

distclean:
	rm xx xx.o gen.o

install:
	cp xx /var/www/html/xx.cgi
	cp html /var/www/html
	cp style.css /var/www/html/style.css
	cp xx.py /var/www/html/xx.py
	cp mysql_aut.py /var/www/html/mysql_aut.py
	cp notifs.py /var/www/html/notifs.py
	cp script.js /var/www/html/script.js

uninstall:
	rm /var/www/html/xx.cgi
	rm /var/www/html/html
	rm /var/www/html/style.css
	rm /var/www/html/xx.py
	rm /var/www/html/script.js

.PHONY: all clean distclean install uninstall
