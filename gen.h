/************************************
Ogólne ułatwiające funkcje to C++. Wersja okrojona dla clicki.
(C) Antek, licencja LGPL
************************************/

#ifndef _gEN_H_
#define _gEN_H_ 1
#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <cstdlib>
#ifdef __unix
	#include <sys/types.h>
	#include <signal.h>
	#include <unistd.h>
#endif
using namespace std;

int file(const char * fl, char * t, int lmt)
{
	ifstream str;
	str.open(fl);
	if(!str.good())
		return 0;
	str.read(t, lmt);
	if(!str.eof())
		return 0;
	str.close();
	for(char * i = t; i < t + lmt; i++)
	{
		if(!*i)
			return i-t;
	}
	return 0;
}

string file(const char * fl)
{
	ifstream str;
	str.open(fl);
	if(!str.good())
		return string("");

	str.seekg (0, str.end);
    int length = str.tellg();
    str.seekg (0, str.beg);

    char * buf = new char[length +1];
	str.read(buf, length);
	str.close();
	
	return string(buf, length);
}

string file(string s)
{
	return file(&s[0]);
}

template <typename T>
int file (T t_fl, vector<string> & v)
{
	string fl(t_fl);

	char buf[1000005];
	
	ifstream str;
	str.open(&fl[0]);
	if(!str.good())
		return 0;

	while(!str.eof())
	{
		str.getline(buf, 1000000);
		v.push_back(string(buf));
	}
	while(v[v.size() - 1] == "")
		v.pop_back();
	
	return v.size();
}

void write(const char * fl, string cont)
{
	ofstream of; 
	of.open(fl, ofstream::out);
	of << cont;
	of.close();
}

void operator<< (ostream & o, vector<string> v)
{
	for(int i = 0; i < v.size(); i++)
	{
		o << v[i];
		if(v[i][v[i].size() - 1] != '\n')
			o << "\n";
	}
	return;
}

template <typename T>
void operator<< (ostream & o, vector<T> v)
{
	for(int i = 0; i < v.size(); i++)
	{
		o << v[i] << "\n";
	}
	return;
}


bool whitespace(string a)
{
	for(int i = 0; i < a.length(); i++)
	{
		if(a[i] != '\n' and a[i] != ' ' and a[i] != '\t' and a[i] != '\r')
			return false;
	}
	return true;
}

vector<string> split(string b, string s) //dzieli string na vector stringów, tnąc wzdłuż dowolnego symbolu z s
{
	vector<string>V;
	string akt;

	bool add = 1;

	for(int i = 0; i < b.size(); i++)
	{
		for(int j = 0; j < s.size(); j++)
		{
			if(b[i] == s[j] and !akt.empty())
			{
				V.push_back(akt); akt.resize(0); add = 0;
			}
		}
		if(add)
			akt+=b[i];
		add = 1;

		if(i+1 == b.size()) V.push_back(akt);
	}
	return V;
}

int rnd(int a, int b) //sprawdza się dla niezbyt dużych liczb, ale za to wysoka jakość pseudolosowości
{
	unsigned long long l;
	int buff[101];
	FILE * urnd = fopen("/dev/urandom", "r");
	fread(buff, 4, 100, urnd);
	for(int i = 0; i <= 101; i++)
		l += buff[i];

	l %= (b - a + 1);
	l += a;
	fclose(urnd);
	return (int) l;
}
#endif