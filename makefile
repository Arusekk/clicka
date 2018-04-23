all:
	g++ -Wall -o xx xx.cpp  -lmysqlcppconn -lcryptopp -std=c++11 -I . 
install:
	sudo cp xx /var/www/html/xx.cgi
	sudo cp html /var/www/html
	sudo cp style.css /var/www/html/style.css
	sudo cp xx.py /var/www/html/xx.py
	sudo cp script.js /var/www/html/script.js
