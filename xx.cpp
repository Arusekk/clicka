//Przy użyciu https://dev.mysql.com/doc/connector-cpp/en/connector-cpp-examples-complete-example-1.html
//statement->executeUpdate albo statement->executeQuery = resultSet
#include <bits/stdc++.h>
#include <gen.h>

#include <mysql_connection.h>
#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>

#include <crypto++/cryptlib.h>
#include <cryptopp/filters.h>
#include <cryptopp/sha.h>
#include <cryptopp/hex.h>

#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;
typedef vector<string> VS;
#define CATCH catch (std::exception &e) { cout << "\n" << e.what() << endl;}

string sha256(string a)
{
  CryptoPP::SHA256 h256;
  string b;

  CryptoPP::StringSource(a, true, new CryptoPP::HashFilter(h256, new CryptoPP::HexEncoder(new CryptoPP::StringSink(b))));
  return b;
}

string escape(string & a)
{
  replace_all(a, "\"", "?");
  replace_all(a, "\\", "?");
  replace_all(a, "\'", "?");
  replace_all(a, "+", "&#43;");
  return a;
}

string escape_html(string & a)
{
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

string rpl(string & s, int c, ...)
{
  va_list list;
  va_start(list, c);

  for(int i = 0; i < c; i++)
  {
    replace_first(s, "{}", va_arg(list, string));
  }

  va_end(list);
  return  s;
}

string srpl(string s, int c, ...)
{
  va_list list;
  va_start(list, c);

  for(int i = 0; i < c; i++)
  {
    replace_first(s, "{}", va_arg(list, string));
  }

  va_end(list);
  return  s;
}

int main(int argc, char ** argv)
{
  string post_str, act, sid, username, z, yt, img, size, content, foreign, error;
  int weeks;
  bool logged = 0;
  VS cookies, get, post;
  char * get_str = getenv("QUERY_STRING");
  char * cookie_p = getenv("HTTP_COOKIE");
  sql::Driver *driver;
  sql::Connection *con;
  sql::Statement *stmt;
  sql::ResultSet *res;
  driver = get_driver_instance();
  string mysql_password = file("/var/www/mysql_password");
  mysql_password.resize(mysql_password.size() - 1);
  con = driver->connect("tcp://127.0.0.1:3306", "antek", mysql_password);
  con->setSchema("xx");
  stmt = con->createStatement();
  VS vhtml; file("html", vhtml);
  map<string, string> M;
  for(uint i = 0; i < vhtml.size(); i+=2)
  {
    M[vhtml[i]] = vhtml[i+1];
  }
  rpl(M["head"], 1, file("style.css"));
  map<string, string> imiona;
  res = stmt->executeQuery("select username, imie from users");
  while(res->next())
    imiona[res->getString("username")] = res->getString("imie");

  cout << "Content-type: text/html; charset=utf-8\n"; 

  if(cookie_p)
  {
    string cookie(cookie_p);
    while(cookie.size() and cookie.substr(0, 4) != "sid=")
      cookie = cookie.substr(1);
    //cout << "\n" << cookie << "\n";
    cookies = split(cookie, "= ");
    for(auto a: cookies) escape(a);
  }

  if(get_str)
  {
    get = split(get_str, "=&");
    for(auto a: get) escape(a);
  }

  for(uint i = 0; i < get.size(); i+=2)
  {
    if(get[i] == "a"){act = get[i+1];}
    if(get[i] == "z"){z = get[i+1];}
    if(get[i] == "yt"){yt = get[i+1];}
    if(get[i] == "img"){img = get[i+1];}
    if(get[i] == "size"){size = get[i+1];}
    if(get[i] == "weeks"){try{weeks = stoi(get[i+1]);}catch(...){weeks = 0;}}
    if(get[i] == "foreign"){foreign = get[i+1];}
    if(get[i] == "e"){error = get[i+1];}
  }

  if(act == "login_b")
  {
    cin >> post_str;
    if(post_str.size())
    {
      post = split(post_str, "=&");
      for(auto a: post) escape(a);
    }
  }

  for(uint i = 0; i < post.size(); i+=2)
  {
    if(post[i] == "content"){content = post[i+1];}
  }

  for(uint i = 0; i < cookies.size(); i+=2)
  {
    if(cookies[i] == "sid"){sid = cookies[i+1]; break;}
  }
  if(sid.empty())
    sid = "0";

  //logging
  ofstream log_f; log_f.open("log", ios_base::app);
  char * log_str = getenv("HTTP_REFERER");
  if(log_str != NULL)
    log_f << log_str << "\t";
  log_f << time(NULL) << "\t";
  log_str = getenv("REMOTE_ADDR");
  log_f << log_str << "\t";
  log_str = getenv("HTTP_USER_AGENT");
  log_f << log_str << endl;
  log_f.flush();
  log_f.close();
  // #TODO: jakaś ładna baza danych do śledzenia użytkowników

  // zrobiono init, sprawdzamy czy jest sesja
  try
  {
    res = stmt->executeQuery("select username from sessions where sid = \"" + sid + "\"");
  }
  catch (sql::SQLException &e) {
    cerr << "# ERR: SQLException in " << __FILE__;
    cerr << "(" << __FUNCTION__ << ") on line " << __LINE__ << endl;
    cerr << "# ERR: " << e.what();
    cerr << " (MySQL error code: " << e.getErrorCode();
    cerr << ", SQLState: " << e.getSQLState() << " )" << endl;
    cerr << "\nBłąd podczas logowania się\n" << endl;
    res = NULL;
  }

  while(res != NULL and res->next())
  {
    username = res->getString("username");
    logged = 1;
  }

  if(!logged)
  {
    if(act == "login_b")
    {
      goto LOGIN_B;
    }
    else 
    {
      if(act != "dump")
        goto LOGIN;
    }
  } 

  if(act == "")
    act = "view";

  if(act == "login_b")
  {
    LOGIN_B:
    string login, passwd; bool ok = 0;

    for(uint i = 0; i < post.size(); i+= 2)
    {
      if(post[i] == "login") login = post[i+1];
      if(post[i] == "passwd") passwd = post[i+1];
    }

    passwd = sha256(passwd);

    try
    {
      string q = "select username, imie from users where passwd = \"{passwd}\" and username = \"{login}\"";
      replace_all(q, "{passwd}", passwd); replace_all(q, "{login}", login); 
      res = stmt->executeQuery(q);
    }
    catch (sql::SQLException &e)
    {
      cerr << "\nNastąpił błąd logowania\n"; return 0;
    }

    while(res->next())
    {
      if(res->getString("username") == login)
        ok = 1;
    }

    if(!ok)
    {
      cout << "\nPodano nieprawidłowy login lub hasło :(\n";
      return 0;
    }

    char sid[130];
    for(int i = 0; i < 128; i++)
    {
      do
        sid[i] = rnd(48, 122);
      while(sid[i] == '"' or sid[i] == '=' or sid[i] == ';');
    }
    sid[128] = 0;

    string u = "insert into sessions values(\"{sid}\", \"{login}\", now(), 0)";
    replace_all(u, "{sid}", sid); replace_all(u, "{login}", login);
    string u2 = "delete from sessions where username = \"{}\"";
    u2 = rpl(u2, 1, login);
    
    try
    {
      stmt->executeUpdate(u2);
      stmt->executeUpdate(u);
    }
    catch (sql::SQLException &e)
    {
      cout << "\n# ERR: SQLException in " << __FILE__;
      cout << "(" << __FUNCTION__ << ") on line " << __LINE__ << endl;
      cout << "# ERR: " << e.what();
      cout << " (MySQL error code: " << e.getErrorCode();
      cout << ", SQLState: " << e.getSQLState() << " )" << endl;
    }

    cout << "Set-Cookie: sid="<< sid << "\n";
    cout << "Location: xx.py?a=view\n";
    cout << "\nCześć " + login + ", zalogowałeś się w serwisie\n" << endl; 

    return 0;
  }

  if(act == "login")
  { 
    LOGIN:
    cout << "\n";
    cout << rpl(M["head"], 1, "{}", file("style.css")) << M["login_form"];

    return 0;
  }

  if(act == "register")
  {
    cout << "\nRejestracja\n"; 
    return 0;
  }

  //robi listing należących grup
  string listing_grup = "";
  string q4 = "select groupid from group_belonging where user = \"{}\"";
  rpl(q4, 1, username);
  res = stmt->executeQuery(q4);
  vector<int> listing_grup_v_id;
  VS listing_grup_v;
  while(res != NULL and res->next())
    listing_grup_v_id.push_back(res->getInt("groupid"));
  for(auto a: listing_grup_v_id)
  {
    string q = "select nazwa from groups where id="; q += to_string(a);
    res = stmt->executeQuery(q); res->next();
    listing_grup_v.push_back(res->getString("nazwa"));
    listing_grup += srpl(M["entryp_o"], 1, string("group&id=") + to_string(a)) + res->getString("nazwa") + "</a></div>";
  }

  if(act == "view")
  {
    cout << "Location: xx.py?a=view\n\n";
    return 0;
  }

  if (act == "friends")
  {
    cout << "\n" << M["head"] << M["body_o"] << listing_grup << "</div>" <<  M["main_o"] << endl;
    cout << "<h1>W clice z założenia wszyscy jesteśmy znajomymi. Oto lista użytkowników clicki:</h1>";

    string q = "select imie, username from users where username != \"{}\" order by imie";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);

    while(res != NULL and res->next())
    {
      string tg = "<img src=\"xx.py?a=img&img=_profile_{}&size=medium\">";
      rpl(tg, 1, res->getString("username"));
      string tmp = "<br><a href=\"xx.cgi?a=mes&z={}\"><button>Wiadomość</button></a><a href=\"xx.py?a=space&user={}\"><button>Przestrzeń</button></a></div><br>";
      rpl(tmp, 2, res->getString("username"), res->getString("username"));

      cout << M["enum_o"] << tg << res->getString("imie") << tmp;
    }

    return 0;
  }

  if(act == "mes")
  {
    if(z == "")
    {
      string ql = "select do, count(czas) from messages where od = \"{}\" group by do order by count(czas) desc limit 1;";
      rpl(ql, 1, username);
      res = stmt->executeQuery(ql);
      while(res != NULL and res->next())
      {
        z = res->getString("do");
      }
    }

    if(!weeks) 
      weeks = 22;
    cout << "\n" << M["head"] << M["body_o"] << endl;

    set<string> rozmowcy;
    try
    {
    string q = "select distinct od from messages where do = \"{}\""; 
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while(res!= NULL and res->next())
      rozmowcy.insert(res->getString("od"));
    q = "select distinct do from messages where od = \"{}\""; 
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while(res!= NULL and res->next())
      rozmowcy.insert(res->getString("do"));
    } CATCH

    for(auto a: rozmowcy)
    {
      string o = M["entry_o"];
      cout << rpl(o, 1, string("mes&z=")+a) << imiona[a] << "</div></a>" << "\n";
    }

    cout << "</div>" << M["main_o"] << endl;
    //

    string q = "(select content, od, czas from messages where (od = \"{}\" and do = \"{}\") or (od = \"{}\" and do = \"{}\") order by czas desc limit {}) order by czas asc";
    rpl(q, 5, username, z, z, username, to_string(weeks));
    res = stmt->executeQuery(q);

    while(res != NULL and res->next())
    {
      string otag;
      if(res->getString("od") == username)
        otag = M["mymes_o"];
      else
        otag = M["almes_o"];
      
      replace_all(otag, "{time}", (string) res->getString("czas"));

      cout << otag;
      cout << res->getString("content") << "<br></span><br>";
    }

    cout << rpl(M["mes_form"], 3, z, z, to_string(weeks + 100));
    cout << "<h3 style=\"color: red\">Wiadomości trzeba odświeżać. Wiem, to głupie, naprawimy to kiedyś.</h3>";

    string u = "delete from last_mes_query where username = \"{}\"";
    string u2 = "insert into last_mes_query values (\"{}\", now())";
    rpl(u, 1, username);
    rpl(u2, 1, username);
    try {
      stmt->executeUpdate(u);
      stmt->executeUpdate(u2);
    } CATCH

    return 0;
  }

  if(act == "mes_b")
  {
    string in;

    while(cin >> in)
    {
      content += in;
      content += " ";
    }
    erase_first(content, "content=");
    escape_html(content);
    if (whitespace(content))
    {
      cout << "Location: xx.cgi?a=mes&z=" << z << "\n\n";
      return 0;
    }

    string u = "insert into messages values(0, \"{}\", \"{}\", \"{}\", now(), 0)";
    string u2 = "delete from messages where do not in (select username from users)";
    rpl(u, 3, username, z, content);
    try
    {
      stmt->executeUpdate(u);
      stmt->executeUpdate(u2);
    }
    catch(std::exception &e)
    {
      cerr << "\n" << e.what();
    }
    cout << "Location: xx.cgi?a=mes&z=" << z << "\n\n";
    return 0;
  }

  if(act == "publish")
  {
    cout << "\n" << M["head"] << M["body_o"] << listing_grup << "</div>" << M["main_o"];
    if(error != "")
    {
      if(error == "img")
        cout << "<h3 style=\"color: red\">Załączony obrazek ma nierozpoznawany format. Dodano post bez obrazka.</h3>";
      if(error == "img_size")
        cout << "<h3 style=\"color: red\">Przekroczono maksymalny rozmiar obrazka (a jest to 10 Mb)</h3>";
      else
        cout << error;
    }

    if(foreign == "true")
    {
      cout << "<h1>Napisz post do grupy:</h1>\n";
    }
    else
       cout << "<h1>Napisz post:</h1>\n";

    string form = M["post_form"], us="", gr="";
    string q = "select username, imie from users where username !=\"{}\";";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while(res->next())
    {
      us += srpl(string("<option value=\"{}\">{}</option>"), 2, res->getString("username"), res->getString("imie"));
    }

    q = "select groupid from group_belonging where user =\"{}\"";
    rpl(q, 1, username);
    res = stmt->executeQuery(q);
    while(res != NULL and res->next())
    {
      string id = res->getString("groupid");
      sql::ResultSet* resl = stmt->executeQuery(string("select nazwa from groups where id = ") + id);
      resl->next();
      gr += srpl(string("<option value=\"{}\">{}</option>"), 2, id, resl->getString("nazwa"));
    }
    rpl(form, 2, us, gr);
    cout << form;
    return 0;
  }

  // if(act == "groups")
  // {
  //   cout << "\n" << M["head"] << M["body_o"] << listing_grup << "</div>" << M["main_o"] << "<h1>Grupy:</h1>";
  //   cout << "<h3><a href=\"xx.py?a=create_group\"><u>Stwórz</u></a> własną grupę</h3>" << endl;
  //   string q = "select * from groups where typ != 2";
  //   res = stmt->executeQuery(q);

  //   while(res != NULL and res->next())
  //   {
  //     cout << M["enum_o"] << res->getString("nazwa") << "<br>" << "<span class=\"desc\">" << res->getString("opis") << "</span>";
  //     //#TODO: obrazek grupy
  //     if(res->getInt("typ") == 1)
  //       cout << M["group_o_img"];
  //     else
  //     {
  //       cout << srpl(M["group_c_img"], 1, imiona[res->getString("admin")]);
  //     }
  //     cout << "</div><br>" << endl;
  //   }

  //   return 0;
  // }

  if(act == "dump")
  {
    string ip = "90.156.16.110";
    char* addr = getenv("REMOTE_ADDR");
    if(addr == NULL)
    {
      cout << "Nie udało się określić adresu ip" << endl; return 0;
    }

    if(ip == string(addr))
    {
      cout << "Content-type: text/plain; charset=utf-8\n\n";
      cout << file("log") << endl;
    }
    else
    {
      cout << "\n\n" << endl;
      cout << addr << endl;
      cout << "<h1>Brak uprawnień. Incydent zostanie zgłoszony</h1>" << endl;
    }
    return 0;
  }

  cout << "\n" << M["nieznany_act"];
return 0;
}
