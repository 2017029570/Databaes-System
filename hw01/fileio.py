import psycopg2 as pg
import psycopg2.extras
import csv
import os

def read_csv(filepath):
    #filepath = 'assignment\\Fire_corp.csv'
    read_file = open(filepath, encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter=',')
    result = []
    for row in reader:
        print(f"{row} \n", end='')
        result.append(row)

    
    read_file.close()

def write_csv(filepath, row):
    write_file = open(filepath,'a', encoding = 'utf-8',newline='')
    writer = csv.writer(write_file)
    row = row.rstrip('\n')
    row = row.split(',')

    writer.writerow(row)

    write_file.close()

def filewrite_csv(filepath, rows):
    read_file = open(filepath, encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')
    #rows = rows.rstrip('\n')
    #rows = rows.split(',')

    for row in reader:
        if row[1] == rows[1]:
            print(row[1]+"는 이미 저장된 연락처입니다")
            break

        else:
               
            write_file = open(filepath,'a', encoding = 'utf-8',newline='')
            writer = csv.writer(write_file)

            
            writer.writerow(rows)

            write_file.close()
            break

    read_file.close()

def changeadmin_csv(filepath,sid, rows):
    read_file = open(filepath, encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')
    write_file = open('temp.csv','a', encoding='utf-8', newline='')
    writer = csv.writer(write_file)
    

    for row in reader:
        if sid == row[0]:
            rows = sid+','+rows
            rows = rows.rstrip('\n')
            rows = rows.split(',')
            writer.writerow(rows)

        else:
            writer.writerow(row)

    read_file.close()
    write_file.close()

    
    os.remove(filepath)

    os.rename('temp.csv',filepath)

def change_csv(filepath, rows):
    read_file = open(filepath, encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')
    write_file = open('temp.csv','a', encoding='utf-8', newline='')
    writer = csv.writer(write_file)
    rows = rows.rstrip('\n')
    rows = rows.split(',')

    for row in reader:
        if row[0] == rows[0]:
            write_file.writer(rows)

        else:
            write_file.writer(row)

    read_file.close()
    write_file.close()

    
    os.remove(filepath)

    os.rename('temp.csv',filepath)
        
def delete_csv(filepath,sid):
    read_file = open(filepath, encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')
    write_file = open('temp.csv','a', encoding='utf-8', newline='')
    writer = csv.writer(write_file)
    #rows = rows.rstrip('\n')
    #rows = rows.split(',')

    for row in reader:
        if sid != row[0]:
            writer.writerow(row)



    read_file.close()
    write_file.close()

    os.remove(filepath)

    os.rename('temp.csv',filepath)

def login(id, passwd):
    read_file = open('students.csv', encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')

    cnt = 0
    for row in reader:
        if cnt == 0:
            cnt = cnt + 1
            
        
        else:
            row[0] = row[0].rstrip(' ')
            row[1] = row[1].rstrip(' ')

            if row[0] == id and row[1] == passwd:
                return 1
            
            else:
                return 0

    read_file.close()

def countDomain():
    read_file = open('한양인주소록.csv', encoding = 'utf-8')
    reader = csv.reader(read_file, delimiter = ',')

    domain = []
    cnt = []


    

    for row in reader:
        d = row[2].split('@')
        
        if len(d) == 1:
            continue

        elif domain.count(d[1])==0:
            domain.append(d[1])
            cnt.append(1)


        elif domain.count(d[1])!=0:
            cnt[domain.index(d[1])] += 1

    print("도메인, 개수")
    for i in range(len(domain)):
        print(domain[i], cnt[i])


if __name__ == "__main__":
    id = ''
    while id != 'quit':
        id = input("ID를 입력하세요 : ")
        if id == 'admin':
            command = ''
            while command != "lgout":
                command = input("연락처 추가, 변경, 삭제, 열람 중 하나를 선택하세요 : ")
                if command == "add":
                    row = input("추가할 학생 정보를 입력하세요 : ")
                    write_csv('students.csv',row)
                    read_csv('students.csv')


                    rows = input("학생의 학번, 연락처, 이메일을 입력하세요 : ")
                    write_csv('한양인주소록.csv',rows)
                    read_csv('한양인주소록.csv')
                
                elif command == "change":
                    sname = input("학생 이름을 입력하세요 : ")
                    read_file = open('students.csv', encoding = 'utf-8')
                    reader = csv.reader(read_file, delimiter=',')

                    for row in reader:
                        if row[2] == sname:
                            rows = input("저장할 연락처, 이메일을 입력하세요 : ")
                            changeadmin_csv('한양인주소록.csv',row[0], rows)
                            read_file.close()
                            break
                    
                    read_csv('한양인주소록.csv') 

                elif command == "delete":
                    sname = input("학생 이름을 입력하세요 : ")
                    read_file = open('students.csv', encoding = 'utf-8')
                    reader = csv.reader(read_file, delimiter=',')

                    for row in reader:
                        if row[2] == sname:
                            delete_csv('한양인주소록.csv', row[0])
                            read_file.close()
                            break
                    
                    read_csv('한양인주소록.csv')

                elif command == "open":
                    print("주소록 목록 : ")
                    for file in os.listdir('./'):
                        if '.csv' in file:
                            print(f"{file}")

                    filename = input("열람할 주소록을 선택하세요 : ")

                    while 1:
                        try:
                            read_csv(filename)
                            breaㅏ
                        except FileNotFoundError:
                            filename = input("파일 이름을 다시 입력하세요 : ")

                elif command == "email address":
                    countDomain()
                        
        elif id != 'quit':
            passwd = input("비밀번호를 입력하세요 : ")
            if login(id, passwd) :
                command = ''
                while command != "lgout":
                    command = input("주소록 열람, 연락처 추가, 변경, 삭제 중 하나를 선택하세요 : ")
                    if command == "open":
                        read_csv('한양인주소록.csv')
                        try:
                            read_csv(id+'.csv')
                        except FileNotFoundError:
                            print("개인 주소록에 아무 정보가 없습니다.")
                    
                    elif command == "add":
                        info = input("추가할 정보 또는 주소록 파일 이름을 입력하세요 : ")
                        if ".csv" in info:
                            read_file = open(info, encoding = 'utf-8')
                            reader = csv.reader(read_file, delimiter=',')
                            for row in reader:
                                filewrite_csv(id+'.csv',row)

                            read_file.close()
                        else:
                            write_csv(id+'.csv',info)
                        
                        read_csv(id+'.csv')
                    
                    elif command == "change":
                        sid = input("학번을 입력하세요 : ")
                        read_file = open(id+'.csv', encoding = 'utf-8')
                        reader = csv.reader(read_file, delimiter=',')

                        for row in reader:
                            if row[0] == sid:
                                rows = input("저장할 연락처, 이메일을 입력하세요 : ")
                                rows = sid + rows
                                change_csv(id+'.csv',rows)
                                read_csv(id+'.csv')
                                read_file.close()
                                break

                    elif command == "delete":
                        sid = input("학번을 입력하세요 : ")
                        delete_csv(id+'.csv',sid)
                        read_csv(id+'.csv')
            else:
                print("로그인 정보가 틀렸습니다.")
                
