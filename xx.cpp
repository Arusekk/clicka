// Przy użyciu
// https://dev.mysql.com/doc/connector-cpp/en/connector-cpp-examples-complete-example-1.html
// statement->executeUpdate albo statement->executeQuery = resultSet
#include "gen.h"
#include <bits/stdc++.h>

#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>
#include <mysql_connection.h>

#include <crypto++/cryptlib.h>
#include <cryptopp/filters.h>
#include <cryptopp/hex.h>
#include <cryptopp/sha.h>

#include <boost/algorithm/string.hpp>

using namespace boost;

std::string sha256(std::string a) {
  CryptoPP::SHA256 h256;
  std::string b;

  CryptoPP::StringSource(
      a, true,
      new CryptoPP::HashFilter(
          h256, new CryptoPP::HexEncoder(new CryptoPP::StringSink(b))));
  return b;
}

std::string escape(std::string &a) {
  replace_all(a, "\"", "?");
  replace_all(a, "\\", "?");
  replace_all(a, "\'", "?");
  replace_all(a, "+", "&#43;");
  return a;
}

std::string escape_html(std::string &a) {
  // escape(a);
  replace_all(a, "&", "&amp;");
  replace_all(a, "\\", "&#92;");
  replace_all(a, "\"", "&quot;");
  replace_all(a, "\'", "&#39;");
  replace_all(a, "<", "&lt;");
  replace_all(a, ">", "&gt;");
  replace_all(a, "=", "&#61;");
  return a;
}

std::string rpl(std::string &s, int c, ...) {
  va_list list;
  va_start(list, c);

  for (int i = 0; i < c; i++) {
    replace_first(s, "{}", va_arg(list, std::string));
  }

  va_end(list);
  return s;
}

std::string srpl(std::string s, int c, ...) {
  va_list list;
  va_start(list, c);

  for (int i = 0; i < c; i++) {
    replace_first(s, "{}", va_arg(list, std::string));
  }

  va_end(list);
  return s;
}

int main() {
  std::string post_str, act, sid, username, z, yt, img, size, content, foreign, error;
  int weeks = 0;
  bool logged = 0;
  std::vector<std::string> cookies, get, post;
  char *get_str = getenv("QUERY_STRING");
  char *cookie_p = getenv("HTTP_COOKIE");
  sql::Driver *driver;
  sql::Connection *con;
  sql::Statement *stmt;
  sql::ResultSet *res;
  driver = get_driver_instance();
  std::string mysql_password = file("/var/www/mysql_password");
  mysql_password.resize(mysql_password.size() - 1);
  con = driver->connect("tcp://127.0.0.1:3306", "antek", mysql_password);
  con->setSchema("xx");
  stmt = con->createStatement();
  std::vector<std::string> vhtml;
  file("html", vhtml);
  std::map<std::string, std::string> M;
  for (unsigned int i = 0; i < vhtml.size(); i += 2) {
    M[vhtml[i]] = vhtml[i + 1];
  }
  //rpl(M["head"], 1, file("style.css"));
  std::map<std::string, std::string> imiona;
  res = stmt->executeQuery("select username, imie from users");
  while (res->next())
    imiona[res->getString("username")] = res->getString("imie");

  std::cout << "Content-type: text/html; charset=utf-8\n";

  if (cookie_p) {
    std::string cookie(cookie_p);
    while (cookie.size() and cookie.substr(0, 4) != "sid=")
      cookie = cookie.substr(1);
    // cout << "\n" << cookie << "\n";
    cookies = split(cookie, "=;");
    for (auto & a : cookies)
      escape(a);
  }

  if (get_str) {
    get = split(get_str, "=&");
    for (auto & a : get)
      escape(a);
  }

  for (unsigned int i = 0; i < get.size(); i += 2) {
    if (get[i] == "a") {
      act = get[i + 1];
    }
    if (get[i] == "z") {
      z = get[i + 1];
    }
    if (get[i] == "yt") {
      yt = get[i + 1];
    }
    if (get[i] == "img") {
      img = get[i + 1];
    }
    if (get[i] == "size") {
      size = get[i + 1];
    }
    if (get[i] == "weeks") {
      try {
        weeks = stoi(get[i + 1]);
      } catch (...) {
        weeks = 0;
      }
    }
    if (get[i] == "foreign") {
      foreign = get[i + 1];
    }
    if (get[i] == "e") {
      error = get[i + 1];
    }
  }

  if (act == "login_b") {
    std::cin >> post_str;
    if (post_str.size()) {
      post = split(post_str, "=&");
      for (auto & a : post)
      {
        for (auto & c : a)
        {
          if (int(c) > 125 or int(c) < 32)
            c = '*';
        }
        escape(a);
      }
    }
  }

  for (unsigned int i = 0; i < post.size(); i += 2) {
    if (post[i] == "content") {
      content = post[i + 1];
    }
  }

  for (unsigned int i = 0; i < cookies.size(); i += 2) {
    if (cookies[i] == "sid") {
      sid = cookies[i + 1];
      if (sid[sid.size() - 1] == ';')
        sid.resize(sid.size() - 2);
      break;
    }
  }
  if (sid.empty())
    sid = "0";

  // logging
  std::ofstream log_f;
  log_f.open("log", std::ios_base::app);
  char *log_str = getenv("HTTP_REFERER");
  if (log_str != NULL)
    log_f << log_str << "\t";
  log_f << time(NULL) << "\t";
  log_str = getenv("REMOTE_ADDR");
  log_f << log_str << "\t";
  log_str = getenv("HTTP_USER_AGENT");
  log_f << log_str << std::endl;
  log_f.flush();
  log_f.close();
  // #TODO: jakaś ładna baza danych do śledzenia użytkowników

  // zrobiono init, sprawdzamy czy jest sesja
  try {
    res = stmt->executeQuery("select username from sessions where sid = \"" + sid + "\"");
  } catch (sql::SQLException &e) {
    std::cerr << "# ERR: SQLException in " << __FILE__;
    std::cerr << "(" << __FUNCTION__ << ") on line " << __LINE__ << std::endl;
    std::cerr << "# ERR: " << e.what();
    std::cerr << " (MySQL error code: " << e.getErrorCode();
    std::cerr << ", SQLState: " << e.getSQLState() << " )" << std::endl;
    std::cerr << "\nBłąd podczas logowania się\n" << std::endl;
    res = NULL;
  }

  while (res != NULL and res->next()) {
    username = res->getString("username");
    logged = 1;
  }

  if (!logged) {
    goto LOGIN;
  }
  
  if (act == "")
    act = "view";

  if (act == "login") {
  LOGIN:
    std::cout << "\n";
    std::cout << rpl(M["head"], 1, "{}", file("style.css")) << M["login_form"];

    return 0;
  }

  if (act == "register") {
    std::cout << "\nRejestracja\n";
    return 0;
  }

  // robi listing należących grup
  std::string listing_grup = "";
  std::string q4 = "select groupid from group_belonging where user = \"{}\"";
  rpl(q4, 1, username);
  res = stmt->executeQuery(q4);
  std::vector<int> listing_grup_v_id;
  std::vector<std::string> listing_grup_v;
  while (res != NULL and res->next())
    listing_grup_v_id.push_back(res->getInt("groupid"));
  for (auto a : listing_grup_v_id) {
    std::string q = "select nazwa from groups where id=";
    q += std::to_string(a);
    res = stmt->executeQuery(q);
    res->next();
    listing_grup_v.push_back(res->getString("nazwa"));
    listing_grup +=
        srpl(M["entryp_o"], 1, std::string("group&id=") + std::to_string(a)) +
        res->getString("nazwa") + "</a></div>";
  }

  if (act == "view") {
    std::cout << "Location: xx.py?a=view\n\n";
    return 0;
  }

  if (act == "friends") {
    std::cout << "\n"
              << M["head"] << M["body_o"] << listing_grup << "</div>"
              << M["main_o"] << std::endl;
    std::cout
        << "<h1>W clice z założenia wszyscy jesteśmy znajomymi. Oto lista "
           "użytkowników clicki:</h1>";

    std::string q = "select imie, username from users where username != \"{}\" "
                    "order by imie";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);

    while (res != NULL and res->next()) {
      std::string tg = "<img src=\"xx.py?a=img&img=_profile_{}&size=medium\">";
      rpl(tg, 1, res->getString("username"));
      std::string tmp =
          "<br><a href=\"xx.cgi?a=mes&z={}\"><button>Wiadomość</button></a><a "
          "href=\"xx.py?a=space&user={}\"><button>Przestrzeń</button></a></"
          "div><br>";
      rpl(tmp, 2, res->getString("username"), res->getString("username"));

      std::cout << M["enum_o"] << tg << res->getString("imie") << tmp;
    }

    return 0;
  }

  if (act == "mes") {
    if (z == "") {
      std::string ql = "select do, count(czas) from messages where od = \"{}\" group by do order by count(czas) desc limit 1;";
      rpl(ql, 1, username);
      res = stmt->executeQuery(ql);
      while (res != NULL and res->next()) {
        z = res->getString("do");
      }
    }

    if (!weeks)
      weeks = 22;
    std::cout << "\n" << M["head"] << M["body_o"] << "<script>z = \"" << z << "\"</script>" << std::endl;

    std::set<std::string> rozmowcy;
    try {
      std::string q = "select distinct od from messages where do = \"{}\"";
      rpl(q, 1, username);
      res = stmt->executeQuery(q);
      while (res != NULL and res->next())
        rozmowcy.insert(res->getString("od"));
      q = "select distinct do from messages where od = \"{}\"";
      rpl(q, 1, username);
      res = stmt->executeQuery(q);
      while (res != NULL and res->next())
        rozmowcy.insert(res->getString("do"));
    } catch (std::exception &e) {
      std::cout << "\n" << e.what() << std::endl;
    }

    for (auto a : rozmowcy) {
      std::string o = M["entry_o"];
      std::cout << rpl(o, 1, std::string("mes&z=") + a) << imiona[a]
                << "</div></a>"
                << "\n";
    }
    std::cout << "</div>" << M["main_o"] << std::endl;
    //

    std::cout << "<span id=\"messages\">\n";
    std::cout << "</span>\n";

    std::cout << rpl(M["mes_form"], 3, z, z, std::to_string(weeks + 100));
    std::cout << "<h3 style=\"color: green\">Wiadomości odświeżają się same.</h3>";

    return 0;
  }

  if (act == "publish") {
    std::cout << "\n"
              << M["head"] << M["body_o"] << listing_grup << "</div>"
              << M["main_o"];
    if (error != "") {
      if (error == "img")
        std::cout
            << "<h3 style=\"color: red\">Załączony obrazek ma nierozpoznawany "
               "format. Dodano post bez obrazka.</h3>";
      if (error == "img_size")
        std::cout << "<h3 style=\"color: red\">Przekroczono maksymalny rozmiar "
                     "obrazka (a jest to 10 Mb)</h3>";
      else
        std::cout << error;
    }

    if (foreign == "true") {
      std::cout << "<h1>Napisz post do grupy:</h1>\n";
    } else
      std::cout << "<h1>Napisz post:</h1>\n";

    std::string form = M["post_form"], us = "", gr = "";
    std::string q = "select username, imie from users where username !=\"{}\";";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while (res->next()) {
      us += srpl(std::string("<option value=\"{}\">{}</option>"), 2,
                 res->getString("username"), res->getString("imie"));
    }

    q = "select groupid from group_belonging where user =\"{}\"";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while (res != NULL and res->next()) {
      std::string id = res->getString("groupid");
      sql::ResultSet *resl = stmt->executeQuery(
          std::string("select nazwa from groups where id = ") + id);
      resl->next();
      gr += srpl(std::string("<option value=\"{}\">{}</option>"), 2, id,
                 resl->getString("nazwa"));
    }
    rpl(form, 2, us, gr);
    std::cout << form;
    return 0;
  }

  // if(act == "groups")
  // {
  //   cout << "\n" << M["head"] << M["body_o"] << listing_grup << "</div>" <<
  //   M["main_o"] << "<h1>Grupy:</h1>"; cout << "<h3><a
  //   href=\"xx.py?a=create_group\"><u>Stwórz</u></a> własną grupę</h3>" <<
  //   endl; std::string q = "select * from groups where typ != 2"; res =
  //   stmt->executeQuery(q);

  //   while(res != NULL and res->next())
  //   {
  //     cout << M["enum_o"] << res->getString("nazwa") << "<br>" << "<span
  //     class=\"desc\">" << res->getString("opis") << "</span>";
  //     //#TODO: obrazek grupy
  //     if(res->getInt("typ") == 1)
  //       cout << M["group_o_img"];
  //     else
  //     {
  //       cout << srpl(M["group_c_img"], 1,
  //       imiona[res->getString("admin")]);
  //     }
  //     cout << "</div><br>" << endl;
  //   }

  //   return 0;
  // }

  /*if (act == "dump") {
    std::string ip = "90.156.16.110";
    char *addr = getenv("REMOTE_ADDR");
    if (addr == NULL) {
      std::cout << "Nie udało się określić adresu ip" << std::endl;
      return 0;
    }

    if (ip == std::string(addr)) {
      std::cout << "Content-type: text/plain; charset=utf-8\n\n";
      std::cout << file("log") << std::endl;
    } else {
      std::cout << "\n\n" << std::endl;
      std::cout << addr << std::endl;
      std::cout << "<h1>Brak uprawnień. Incydent zostanie zgłoszony</h1>"
                << std::endl;
    }
    return 0;
  }*/

  std::cout << "\n" << M["nieznany_act"];
  return 0;
}
