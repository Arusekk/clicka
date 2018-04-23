#include "gen.h"

int file(const char *path, char *dest, int len) {
  std::ifstream file_handler;
  file_handler.open(path);
  if (false == file_handler.good()) {
    perror("file_handler");
    return 0;
  }
  file_handler.read(dest, len);
  if (false == file_handler.eof()) {
    return 0;
  }
  file_handler.close();
  for (char *iter = dest; iter < dest + len; ++iter) {
    if (0 == *iter) {
      return iter - dest;
    }
  }
  return 0;
}

std::string file(const char *path) {
  std::ifstream file_handler;
  file_handler.open(path);
  if (false == file_handler.good()) {
    perror("file_handler");
    return std::string("");
  }

  file_handler.seekg(0, file_handler.end);
  int length = file_handler.tellg();
  file_handler.seekg(0, file_handler.beg);

  char *buffer = new char[length + 1];
  file_handler.read(buffer, length);
  file_handler.close();

  std::string result(buffer, length);
  delete[] buffer;
  return result;
}

std::string file(const std::string &path) { return file(path.c_str()); }

void write(const char *path, const std::string cont) {
  std::ofstream out;
  out.open(path, std::ofstream::out);
  out << cont;
  out.close();
}

void operator<<(std::ostream &stream, const std::vector<std::string> &v) {
  for (const auto &it : v) {
    stream << it;
    if (it.back() != '\n')
      stream << '\n';
  }
}

bool whitespace(const std::string &s) {
  for (auto it : s) {
    if ('\n' != it && ' ' != it && '\t' != it && '\r' != it)
      return false;
  }
  return true;
}

std::vector<std::string> split(const std::string &b, const std::string &s) {
  std::vector<std::string> result;
  std::string act;
  bool add = true;

  for (auto it : b) {
    for (auto ptr : s) {
      if (it == ptr && act.empty() == false) {
        result.push_back(act);
        act.clear();
        add = false;
      }
    }
    if (true == add) {
      act.push_back(it);
    }
    add = true;
  }
  result.push_back(act);
  return result;
}

int rnd(int a, int b) {
  if (a > b) { // ugly hack
    std::swap(a, b);
    std::cerr << "rnd: a < b\n";
  }
  std::random_device rd;
  std::mt19937 mt(rd());
  std::uniform_int_distribution<int> dist(a, b);
  return dist(mt);
}
