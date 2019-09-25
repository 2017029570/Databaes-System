import psycopg2 as pg
import psycopg2.extras
import csv
import sqlite3

db_connector = {
       'host' : 'localhost',
       'user' : 'postgres',
       'dbname' : 'postgres',
       'port' : '5432',
       'password' : 'dkssud'
   }

def select(table):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
   # print(connect_string)

    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "SELECT * FROM "+table

    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.commit()
    conn.close()

def students_insert(table,values):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #cur.execute("\dt"+"\n")
    
    values = values.replace(" ","")

    row = values.split(",")

    #try:    
    sql = f"INSERT INTO {table} VALUES ('{row[0]}', '{row[1]}','{row[2]}', '{row[3]}', {row[4]}, {row[5]}, {row[6]});"

    
    cur.execute(sql)
    values = values.split(",")
    make_address(row[2])

    #except:
     #   print(f"{row[0]}가 이미 있습니다.")
    
    #make_address(row[2])
    conn.commit()
    conn.close()

def address_insert(table,values): 
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    values = values.replace(" ","")

    row = values.split(",")


       
    sql = f"INSERT INTO {table} VALUES ('{row[0]}', '{row[1]}','{row[2]}');"

    
    cur.execute(sql)
    values = values.split(",")

    
    
    conn.commit()
    conn.close()

def change_address(table, values):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    values = values.replace(" ","")
    row = values.split(",")

    sql = f'''UPDATE {table}
            SET phone = '{row[1]}'
            WHERE sid = '{row[0]}';
            '''
    cur.execute(sql)

    sql = f'''UPDATE {table}
            SET email = '{row[2]}'
            WHERE sid = '{row[0]}';
            '''
    cur.execute(sql)
    conn.commit()
    conn.close()

def make_address(table):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)




    sql = f'''CREATE TABLE {table} (
            sid CHAR(15), 
            phone CHAR(15), 
            email CHAR(30), 
            PRIMARY KEY(sid)
            );
            '''.format(table=table)
    #print(sql)
    cur.execute(sql)
    conn.commit()
    conn.close()

def delete_address(table, sid):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    sql = f"DELETE FROM {table} WHERE sid = '{sid}';"

    cur.execute(sql)

    conn.commit()
    conn.close()

def countDomain():
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT email FROM 한양인주소록")

    r = cur.fetchall()
    domain=[]
    cnt=[] 
    #print(r[1]['email'])
    for i in range(len(r)):
        r[i]['email'] = r[i]['email'].strip()
        d = r[i]['email'].split("@")
       
        if domain.count(d[1]) == 0:
            domain.append(d[1])
            cnt.append(1)
        
        else:
            cnt[domain.index(d[1])] += 1
    
    print("도메인, 개수")
    for i in range(len(domain)):
        print(domain[i], cnt[i]) 
    conn.commit()
    conn.close()

def login(id, passwd):
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(f"SELECT password FROM students WHERE sid = '{id}';")

    try:
        r = cur.fetchone()
        r['password'] = r['password'].strip()
        if r['password'] == passwd:
            return 1
        else:
            return 0
    except TypeError:
        return 0

    conn.commit()
    conn.close()

if __name__ == "__main__":
    connect_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)
    conn = pg.connect(connect_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


    id = ''
    while id != 'quit':
        id = input("ID를 입력하세요 : ")
        if id == 'admin':
            command = ''
            while command != "lgout":
                command = input("연락처 추가, 변경, 삭제, 열람 중 하나를 선택하세요 : ")
                if command == "add":
                    row = input("추가할 학생 정보를 입력하세요 : ")
                    students_insert("students", row)
                    #select('한양인주소록')


                    rows = input("학생의 학번, 연락처, 이메일을 입력하세요 : ")
                    address_insert('한양인주소록', rows)
                    select('한양인주소록')
                
                elif command == "change":
                    sname = input("학생 이름을 입력하세요 : ")
                    cur.execute(f"SELECT sid FROM students WHERE sname = '{sname}';")
                    r = cur.fetchone()
                    
                    
                    values = input("저장할 연락처, 이메일을 입력하세요 : ")
                    values = r['sid']+',' + values
                    change_address('한양인주소록',values)
                    
                    select('한양인주소록') 

                elif command == "delete":
                    sname = input("학생 이름을 입력하세요 : ")
                    cur.execute(f"SELECT sid FROM students WHERE sname = '{sname}';")
                    r = cur.fetchone()

                    
                    delete_address('한양인주소록',r['sid'])


                    select('한양인주소록')

                elif command == "open":
                    print("테이블 목록 : ")
                    cur.execute("SELECT * FROM pg_tables WHERE schemaname='public';")
                    r = cur.fetchall()

                    for row in r:
                        print(row['tablename'])

                    tablename = input("열람할 테이블을 선택하세요 : ")
                    select(tablename)
                   
                   

                elif command == "email address":
                    countDomain()
                       
        elif id != 'quit':
            passwd = input("비밀번호를 입력하세요 : ")
            if login(id, passwd) :
                cur.execute(f"SELECT sname FROM students WHERE sid = '{id}';")
                r = cur.fetchone()
                name = r['sname']
                try:
                    make_address(name)
                except:
                    continue
                finally:
                    command = ''
                    while command != "lgout":
                        command = input("주소록 열람, 연락처 추가, 변경, 삭제 중 하나를 선택하세요 : ")
                        if command == "open":
                            select('한양인주소록')
                            
                            try:
                                select(name)
                            except psycopg2.ProgrammingError:
                                print("개인 주소록에 아무 정보가 없습니다.")
                        
                        elif command == "add":
                            info = input("추가할 정보 또는 주소록 파일 이름을 입력하세요 : ")
                            if ".csv" in info:
                                read_file = open(info, encoding = 'utf-8')
                                reader = csv.reader(read_file, delimiter=',')
                                for row in reader:
                                    row = f"{row[0]},{row[1]},{row[2]}"
                                    address_insert(name,row)

                                read_file.close()
                            else:
                                address_insert(name,info)
                            
                            select(name)
                        
                        elif command == "change":
                            sid = input("학번을 입력하세요 : ")
                        
                            values = input("저장할 연락처, 이메일을 입력하세요 : ")
                            values = sid+","+ values
                            change_address(name,values)
                            select(name)

                        elif command == "delete":
                            sid = input("학번을 입력하세요 : ")
                            delete_address(name,sid)
                            select(name)
            else:
                print("로그인 정보가 틀렸습니다.")
                

    conn.commit()
    conn.close()