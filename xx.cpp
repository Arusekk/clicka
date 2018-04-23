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
  std::string post_str, act, sid, username, z, yt, img, size, content, foreign,
      error;
  int weeks;
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
  rpl(M["head"], 1, file("style.css"));
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
    cookies = split(cookie, "= ");
    for (auto a : cookies)
      escape(a);
  }

  if (get_str) {
    get = split(get_str, "=&");
    for (auto a : get)
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
      for (auto a : post)
        escape(a);
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
    res = stmt->executeQuery("select username from sessions where sid = \"" +
                             sid + "\"");
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
    if (act == "login_b") {
      goto LOGIN_B;
    } else {
      if (act != "dump")
        goto LOGIN;
    }
  }

  if (act == "")
    act = "view";

  if (act == "login_b") {
  LOGIN_B:
    std::string login, passwd;
    bool ok = 0;

    for (unsigned int i = 0; i < post.size(); i += 2) {
      if (post[i] == "login")
        login = post[i + 1];
      if (post[i] == "passwd")
        passwd = post[i + 1];
    }

    passwd = sha256(passwd);

    try {
      std::string q = "select username, imie from users where passwd = "
                      "\"{passwd}\" and username = \"{login}\"";
      replace_all(q, "{passwd}", passwd);
      replace_all(q, "{login}", login);
      res = stmt->executeQuery(q);
    } catch (sql::SQLException &e) {
      std::cerr << "\nNastąpił błąd logowania\n";
      return 0;
    }

    while (res->next()) {
      if (res->getString("username") == login)
        ok = 1;
    }

    if (!ok) {
      std::cout << "\nPodano nieprawidłowy login lub hasło :(\n";
      return 0;
    }

    char sid[130];
    for (int i = 0; i < 128; i++) {
      do
        sid[i] = static_cast<char>(rnd(48, 122));
      while (sid[i] == '"' or sid[i] == '=' or sid[i] == ';');
    }
    sid[128] = 0;

    std::string u =
        "insert into sessions values(\"{sid}\", \"{login}\", now(), 0)";
    replace_all(u, "{sid}", sid);
    replace_all(u, "{login}", login);
    std::string u2 = "delete from sessions where username = \"{}\"";
    u2 = rpl(u2, 1, login);

    try {
      stmt->executeUpdate(u2);
      stmt->executeUpdate(u);
    } catch (sql::SQLException &e) {
      std::cout << "\n# ERR: SQLException in " << __FILE__;
      std::cout << "(" << __FUNCTION__ << ") on line " << __LINE__ << std::endl;
      std::cout << "# ERR: " << e.what();
      std::cout << " (MySQL error code: " << e.getErrorCode();
      std::cout << ", SQLState: " << e.getSQLState() << " )" << std::endl;
    }

    std::cout << "Set-Cookie: sid=" << sid << "\n";
    std::cout << "Location: xx.py?a=view\n";
    std::cout << "\nCześć " + login + ", zalogowałeś się w serwisie\n"
              << std::endl;

    return 0;
  }

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
      std::string ql = "select do, count(czas) from messages where od = \"{}\" "
                       "group by do order by count(czas) desc limit 1;";
      rpl(ql, 1, username);
      res = stmt->executeQuery(ql);
      while (res != NULL and res->next()) {
        z = res->getString("do");
      }
    }

    if (!weeks)
      weeks = 22;
    std::cout << "\n" << M["head"] << M["body_o"] << std::endl;

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

    std::string q = "(select content, od, czas from messages where (od = "
                    "\"{}\" and do = \"{}\") or (od = \"{}\" and do = \"{}\") "
                    "order by czas desc limit {}) order by czas asc";
    rpl(q, 5, username, z, z, username, std::to_string(weeks));
    res = stmt->executeQuery(q);

    while (res != NULL and res->next()) {
      std::string otag;
      if (res->getString("od") == username)
        otag = M["mymes_o"];
      else
        otag = M["almes_o"];

      replace_all(otag, "{time}", (std::string)res->getString("czas"));

      std::cout << otag;
      std::cout << res->getString("content") << "<br></span><br>";
    }

    std::cout << rpl(M["mes_form"], 3, z, z, std::to_string(weeks + 100));
    std::cout
        << "<h3 style=\"color: red\">Wiadomości trzeba odświeżać. Wiem, to "
           "głupie, naprawimy to kiedyś.</h3>";

    std::string u = "delete from last_mes_query where username = \"{}\"";
    std::string u2 = "insert into last_mes_query values (\"{}\", now())";
    rpl(u, 1, username);
    rpl(u2, 1, username);
    try {
      stmt->executeUpdate(u);
      stmt->executeUpdate(u2);
    } catch (std::exception &e) {
      std::cout << "\n" << e.what() << std::endl;
    }

    return 0;
  }

  if (act == "mes_b") {
    std::string in;

    while (std::cin >> in) {
      content += in;
      content += " ";
    }
    erase_first(content, "content=");
    escape_html(content);
    if (whitespace(content)) {
      std::cout << "Location: xx.cgi?a=mes&z=" << z << "\n\n";
      return 0;
    }

    std::string u =
        "insert into messages values(0, \"{}\", \"{}\", \"{}\", now(), 0)";
    std::string u2 =
        "delete from messages where do not in (select username from users)";
    rpl(u, 3, username, z, content);
    try {
      stmt->executeUpdate(u);
      stmt->executeUpdate(u2);
    } catch (std::exception &e) {
      std::cerr << "\n" << e.what();
    }
    std::cout << "Location: xx.cgi?a=mes&z=" << z << "\n\n";
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

  if (act == "dump") {
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
  }

  std::cout << "\n" << M["nieznany_act"];
  return 0;
}
