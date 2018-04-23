/************************************
Ogólne ułatwiające funkcje to C++. Wersja okrojona dla clicki.
(C) Antek, licencja LGPL
************************************/

#ifndef _gEN_H_
#define _gEN_H_
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <random>
#include <signal.h>
#include <string>
#include <sys/types.h>
#include <unistd.h>
#include <vector>

int file(const char *path, char *dest, int len);

std::string file(const char *path);

std::string file(const std::string &path);

template <typename T> int file(T t_fl, std::vector<std::string> &v) {
  std::string fl(t_fl);

  char buf[1000005];

  std::ifstream str;
  str.open(&fl[0]);
  if (!str.good())
    return 0;

  while (!str.eof()) {
    str.getline(buf, 1000000);
    v.push_back(std::string(buf));
  }
  while (v[v.size() - 1] == "")
    v.pop_back();

  return static_cast<int>(v.size());
}

void write(const char *path, const std::string &cont);

void operator<<(std::ostream &stream, const std::vector<std::string> &v);

template <typename T>
std::ostream operator<<(std::ostream &stream, std::vector<T> &v) {
  for (const auto &it : v) {
    stream << it << '\n';
  }
  return stream;
}

bool whitespace(std::string const &s);

std::vector<std::string> split(const std::string &b, const std::string &s);

int rnd(int a, int b); // sprawdza się dla niezbyt dużych liczb, ale za to
                       // wysoka jakość pseudolosowości

#endif
