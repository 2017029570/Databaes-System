from flask import Flask, render_template, redirect, request, jsonify, json
import ast
from datetime import datetime
import psycopg2 as pg
import psycopg2 .extras

app = Flask(__name__)

session = {'sid' : None, 'name' : None, 'passwd' : None, 'type' : None, 'contact': None}
msg = False
contacts = {}
orderlist = {}
bucket={}

db_connector = {
    'host' : 'localhost',
    'user' : 'postgres',
    'dbname' : 'postgres',
    'port' : '5432',
    'password' : 'dkssud'
}
conn_str = "host={host} user={user} dbname={dbname} password={password} port={port}".format(**db_connector)

@app.route("/")
def index():
    return render_template("index.html",session=session)

@app.route('/login',methods=['GET','POST'])
def login():
    
    sid = request.form.get('sid')
    passwd = request.form.get('passwd')


    id = sid.split('@')

    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = f"SELECT T.tablename, C.local, C.domain, C.passwd, C.name FROM customer C, (SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='customer') T WHERE local='{id[0]}' AND domain='{id[1]}' AND passwd='{passwd}' UNION SELECT T.tablename, S.local, S.domain, S.passwd, S.name FROM seller S,(SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='seller') T WHERE local='{id[0]}' AND domain='{id[1]}' AND passwd='{passwd}' UNION SELECT T.tablename, D.local, D.domain, D.passwd, D.name FROM delivery D,(SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='delivery') T WHERE local='{id[0]}' AND domain='{id[1]}' AND passwd='{passwd}'"
    
    cur.execute(sql)
    rows = cur.fetchall()

    if(len(rows)==0):
        conn.close()
        return render_template('index.html',session=session, msg = False)

    elif(len(rows) > 1):
        session['sid'] = sid
        session['name'] = rows[0]['name']
        session['passwd']=passwd
        for i in range(len(rows)):
            print(rows[i]['tablename'])
        return render_template('usertype.html', option=[rows[x]['tablename'] for x in range(len(rows))])
        conn.close()

    else:
        
        
        if (rows[0]['passwd'].strip()==passwd):

            session['sid'] = sid
            session['name'] = rows[0]['name']
            session['passwd'] = passwd
            session['type'] = rows[0]['tablename']
            if session['type'] == 'customer':
                key = list(contacts.keys())
                if len(key) == 0:
                    contacts[f"{session['name']}".strip()] = []
                else:
                    if key.count(f"{session['name']}".strip())==0:
                        contacts[f"{session['name']}".strip()] = []

                key = list(bucket.keys())
                if len(key) == 0:
                    bucket[f'{session["name"]}'.strip()]=[]
                else:
                    if key.count(f"{session['name']}".strip())==0:
                        bucket[f"{session['name']}".strip()] = []
           
            conn.close()
            return redirect("/"+rows[0]['tablename'])

    
    

@app.route("/logout")
def logout():
    session = {'sid' : None, 'name' : None, 'type' : None, 'passwd' : None}
    return render_template("index.html",session=session)

@app.route("/seller")
def seller():
    return render_template("seller.html",session=session, msg=msg)

@app.route("/customer")
def customer():
    return render_template("customer.html", session=session, msg=msg)

@app.route("/store")
def store():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = f"SELECT store.sid, store.sname, menu.menu FROM store, menu, seller WHERE store.sid=menu.sid AND seller.sid=store.seller_id AND seller.name='{session['name'].strip()}'"
    cur.execute(sql)
    rows = cur.fetchall()
    
    
    return render_template("store.html", store=rows)

@app.route("/changeinfo", methods=['GET','POST'])
def changeinfo():
    if request.method == "GET":
        return render_template("changeinfo.html", msg=None)

    
    elif request.method =="POST":
        passwd = request.form.get('passwd')
        name = request.form.get('name')

        if passwd == "":
            passwd = session['passwd']

        if name == "":
            name = session['name']

        conn = pg.connect(conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
        ch = False

       
        if(passwd != session['passwd']):  
            sql = f"UPDATE {session['type']} SET passwd='{passwd}' WHERE local='{session['sid'].split('@')[0]}' AND domain='{session['sid'].split('@')[1]}' AND passwd='{session['passwd']}';"
            session['passwd'] = passwd
            cur.execute(sql)
         
            
            ch = True

        if(name != session['name']):
            sql = f"UPDATE {session['type']} SET name='{name}' WHERE local='{session['sid'].split('@')[0]}' AND domain='{session['sid'].split('@')[1]}' AND passwd='{session['passwd']}';"
            session['name']=name
            cur.execute(sql)
            cur.execute(f"select * from {session['type']} where name='{name}'" )
            
            rows = cur.fetchall()
    
            ch = True
            
        if ch==False:
            return render_template("changeinfo.html",msg=False)

        else:
            conn.commit()
            conn.close()
            return render_template(session['type']+".html",session=session, msg=True)
        
        

@app.route("/contact")
def contact():
    check = False
    
    if contacts[f"{session['name']}".strip()] == []:
        return render_template("contact.html", check=False, session=session)

    else:
        return render_template("contact.html",check=True, contacts=contacts[f"{session['name']}".strip()], session=session)
    
@app.route("/add", methods=['GET','POST'])
def add():
    if request.method == 'GET':
        return render_template("add.html",msg=None)

    elif request.method == 'POST':
        number = request.form.get('number')
        if contacts[f"{session['name']}".strip()].count(number) != 0:
            return render_template("add.html",msg=False )

        contacts[f"{session['name']}".strip()].append(number)

        return render_template("contact.html",check=True, msg="추가",contacts=contacts[f"{session['name']}".strip()],session=session)

@app.route("/delete", methods=['GET','POST']) 
def delete():
    if request.method == 'GET':
        return render_template("delete.html", msg=None)

    elif request.method == 'POST':
        number = request.form.get('number')
        if contacts[f"{session['name']}".strip()].count(number) == 0:
            return render_template("delete.html",msg=False)

        contacts[f"{session['name']}".strip()].remove(number)
        if len(contacts[f"{session['name']}".strip()]) == 0:
            return render_template("contact.html",check=False, msg="삭제", session=session)

        else:
            return render_template("contact.html",check=True, msg="삭제",contacts=contacts[f"{session['name']}".strip()], session=session)

@app.route("/change",methods=['GET','POST'])
def change():
    if request.method == 'GET':
        return render_template("change.html",msg=None)

    elif request.method == 'POST':
        old = request.form.get('old')
        new = request.form.get('new')

        if contacts[f"{session['name']}".strip()].count(old) == 0:
            return render_template("change.html",msg=False)
        
        contacts[f"{session['name']}".strip()][contacts[f"{session['name']}".strip()].index(old)] = new

        return render_template("contact.html",check=True, msg="변경",contacts=contacts[f"{session['name']}".strip()],session=session)

@app.route("/menuadd", methods=['GET','POST'])
def menuadd():
    if request.method == 'GET':
        return render_template("menuadd.html",msg=None)

    elif request.method == 'POST':
        conn = pg.connect(conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        st = request.form.get('store')
        new = request.form.get('menu')


        sql = f"INSERT INTO menu VALUES ('{new}',{st})"
        cur.execute(sql)
        conn.commit()
        sql = f"SELECT store.sid, store.sname, menu.menu FROM store, menu, seller WHERE store.sid=menu.sid AND seller.sid=store.seller_id AND seller.name='{session['name'].strip()}'"
        cur.execute(sql)
        rows = cur.fetchall()
    
        return render_template("store.html", msg="추가", store=rows)

@app.route("/menudelete", methods=['GET','POST']) 
def menudelete():
    if request.method == 'GET':
        return render_template("menudelete.html", msg=None)

    elif request.method == 'POST':
        conn = pg.connect(conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        st = request.form.get('store')
        menu = request.form.get('menu')

        sql = f"SELECT count(*) FROM menu WHERE sid={st} AND menu='{menu}'"
        cur.execute(sql)
        rows = cur.fetchall()
     

        if(rows[0]==[0]):
             return render_template("menudelete.html",msg=False)
        else:
            sql = f"DELETE FROM menu WHERE menu='{menu}' AND sid={st}"
            cur.execute(sql)
            conn.commit()
            sql = f"SELECT store.sid, store.sname, menu.menu FROM store, menu, seller WHERE store.sid=menu.sid AND seller.sid=store.seller_id AND seller.name='{session['name'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()
            return render_template("store.html",msg="삭제",store=rows)

@app.route("/menuchange", methods=['GET','POST']) 
def menuchange():
    if request.method == 'GET':
        return render_template("menuchange.html", msg=None)

    elif request.method == 'POST':
        conn = pg.connect(conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        st = request.form.get('store')
        old = request.form.get('old')
        new = request.form.get('new')

        sql = f"SELECT count(*) FROM menu WHERE sid={st} AND menu='{old}'"
        cur.execute(sql)
        rows = cur.fetchall()
        
        if(rows[0]==[0]):
             return render_template("menuchange.html",msg=False)
        else:
            sql = f"UPDATE menu SET menu='{new}' WHERE menu='{old}' AND sid={st}"
            cur.execute(sql)
            conn.commit()
        
            sql = f"SELECT store.sid, store.sname, menu.menu FROM store, menu, seller WHERE store.sid=menu.sid AND seller.sid=store.seller_id AND seller.name='{session['name'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()
            return render_template("store.html",msg="변경",store=rows)

@app.route("/pay")
def pay():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
    cur.execute(sql)
    rows = cur.fetchall()        
    new = json.loads(rows[0]['payments'])

    return render_template("pay.html", pay=new)
  
@app.route("/payadd", methods=['GET','POST'])
def payadd():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method=='GET':
        return render_template("payadd.html", msg=None)

    else:
        paytype=request.form.get('paytype')

        if paytype=='카드':
            cardnum = request.form.get('cardnum')
            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()
            
            new = json.loads(rows[0]['payments'])

            
            dic = {"type":"card", "data":{"card_num": int(cardnum)}}
            new.append(dic)
                
            up = json.dumps(new)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        elif paytype=='계좌':
            bankname = request.form.get('bankname')
            acc=request.form.get('account')

            cur.execute(f"select bid from bank where name='{bankname}'")
            n=cur.fetchall()

            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()

            new = json.loads(rows[0]['payments'])
            dic = {"type":"bank", "data":{"bid": int(n[0]['bid']), "acc_num":int(acc)}}
            new.append(dic)

            up = json.dumps(new)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
        cur.execute(sql)
        rows = cur.fetchall()
        
      
        new = json.loads(rows[0]['payments'])
        
        return render_template("pay.html",msg="추가", pay=new)

@app.route("/paychange", methods=['GET','POST'])
def paychange():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method=='GET':
        return render_template("paychange.html", msg=None)

    else:
        paytype=request.form.get('paytype')

        if paytype=='카드':
            old = request.form.get('old')
            new = request.form.get('new')
          
            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()
    
           
            
            yes = json.loads(rows[0]['payments'])

            for i in range(len(yes)):
                if yes[i]['type']=='card':
                    if yes[i]['data']['card_num']==int(old):
                        yes[i]['data']['card_num']=int(new)
                        
                        break

                if i == len(yes)-1:
                    return render_template("paychange.html", msg=False)

            up = json.dumps(yes)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        elif paytype=='계좌':
            bankname = request.form.get('bankname')
            old=request.form.get('bold')
            new=request.form.get('bnew')

            cur.execute(f"select bid from bank where name='{bankname}'")
            n=cur.fetchall()

            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()

            yes = json.loads(rows[0]['payments'])

            for i in range(len(yes)):
                if yes[i]['type']=='bank':

                    if yes[i]['data']['bid']==int(n[0]['bid']):
                       
                        if yes[i]['data']['acc_num']==int(old):
                            yes[i]['data']['acc_num']=int(new)
                            break
                if i == len(yes)-1:
                    return render_template("paychange.html", msg=False)

            up = json.dumps(yes)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
        cur.execute(sql)
        rows = cur.fetchall()
        
       
        new = json.loads(rows[0]['payments'])
        
        return render_template("pay.html",msg="변경", pay=new)

@app.route("/paydelete", methods=['GET','POST'])
def paydelete():
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method=='GET':
        return render_template("paydelete.html", msg=None)

    else:
        paytype=request.form.get('paytype')

        if paytype=='카드':
            num = request.form.get('cardnum')
           
            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()

            yes = json.loads(rows[0]['payments'])

            for i in range(len(yes)):
                if yes[i]['type']=='card':
                    if yes[i]['data']['card_num']==int(num):
                        del yes[i]
                        break

                if i == len(yes)-1:
                    return render_template("paydelete.html", msg=False)

            up = json.dumps(yes)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        elif paytype=='계좌':
            bankname = request.form.get('bankname')
            num=request.form.get('account')

            cur.execute(f"select bid from bank where name='{bankname}'")
            n=cur.fetchall()

            sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
            cur.execute(sql)
            rows = cur.fetchall()

            yes = json.loads(rows[0]['payments'])

            for i in range(len(yes)):
                if yes[i]['type']=='bank':
                    if yes[i]['data']['bid']==int(n[0]['bid']):
                        if yes[i]['data']['acc_num']==int(num):
                            del yes[i]
                            break
                if i == len(yes)-1:
                    return render_template("paydelete.html", msg=False)

            up = json.dumps(yes)

            cur.execute(f"update customer set payments='{up}' where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'")
            conn.commit()

        sql = f"select payments from customer where local='{session['sid'].split('@')[0].strip()}' and domain='{session['sid'].split('@')[1].strip()}' and passwd='{session['passwd'].strip()}'"
        cur.execute(sql)
        rows = cur.fetchall()
       
        new = json.loads(rows[0]['payments'])
        
        return render_template("pay.html",msg="삭제", pay=new)




@app.route("/search", methods=['GET','POST'])
def search():
    menu = {}
    if request.method=='GET':
        return render_template("order.html", msg=None)

    else:
        sname=request.form.get('name')
        tag = request.form.get('tag')
        address = request.form.get('address')

        if sname!="":
            conn = pg.connect(conn_str)
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"select count(*) from store where sname='{sname}'")
            num = cur.fetchall()

            if num[0] == [0]:
                sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
                cur.execute(sql)

                near=cur.fetchall()
                for i in range(len(near)):
                    sql = f"select menu from menu where sid = {near[i]['sid']}"
                    cur.execute(sql)
                    menu[near[i]['sid']] = cur.fetchall()

                return render_template("order.html", msg=False, near=near, menu=menu)

            else:
                cur.execute(f"select * from store where sname='{sname}'")
                row = cur.fetchall()
                sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
                cur.execute(sql)

                near=cur.fetchall()
                for i in range(len(near)):
                    sql = f"select menu from menu where sid = {near[i]['sid']}"
                    cur.execute(sql)
                    menu[near[i]['sid']] = cur.fetchall()

                return render_template("order.html", msg=True, store=row, menu=menu, near=near)

        elif address!="":
            conn = pg.connect(conn_str)
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"select count(*) from store where address='{address}'")
            num = cur.fetchall()

            if num[0] == [0]:
                sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
                cur.execute(sql)

                near=cur.fetchall()
                for i in range(len(near)):
                    sql = f"select menu from menu where sid = {near[i]['sid']}"
                    cur.execute(sql)
                    menu[near[i]['sid']] = cur.fetchall()

                return render_template("order.html", msg=False, near=near, menu=menu)

            else:
                cur.execute(f"select * from store where sname='{address}'")
                row = cur.fetchall()
                sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
                cur.execute(sql)

                near=cur.fetchall()
                for i in range(len(near)):
                    sql = f"select menu from menu where sid = {near[i]['sid']}"
                    cur.execute(sql)
                    menu[near[i]['sid']] = cur.fetchall()

                return render_template("order.html", msg=True, store=row, near=near, menu=menu)

@app.route("/order", methods=['GET','POST'])
def order():
    menu = {}
        
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
    cur.execute(sql)

    near=cur.fetchall()
        
    for i in range(len(near)):
        n = near[i]['schedules'].replace('\"\"', '"')
        time = json.loads(n)

    for i in range(len(near)):
        menu[near[i]['sid']] = []
        sql = f"select menu from menu where sid = {near[i]['sid']}"
        cur.execute(sql)
        rows=cur.fetchall()
        for j in range(len(rows)):
            menu[near[i]['sid']].append(rows[j]['menu'].strip())

            
        
    if request.method == 'GET' :
        return render_template("order.html", msg=None, near=near, menu=menu, bucket=bucket[f'{session["name"]}'])
    else:
        st = request.form.get('near')
        me = request.form.get(f'{st}')
        cnt = request.form.get('cnt')

        dic = {'store' : f'{st}', 'menu':f'{me}', 'cnt': cnt}
        bucket[f'{session["name"]}'.strip()].append(dic)
        
        return render_template("order.html", bucket=bucket[f'{session["name"]}'.strip()], add=True, near=near, menu=menu)

@app.route("/doorder", methods=['GET','POST'])
def doorder():
    menu = {}
  
    conn = pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = f"select store.sid, store.sname, store.schedules from (select * from customer where name='{session['name']}') c, store order by sqrt(power(c.lat - store.lat, 2)+power(c.lng-store.lng,2)) limit 10"
    cur.execute(sql)

    near=cur.fetchall()
        
    for i in range(len(near)):
        n = near[i]['schedules'].replace('\"\"', '"')
        time = json.loads(n)

    for i in range(len(near)):
        menu[near[i]['sid']] = []
        sql = f"select menu from menu where sid = {near[i]['sid']}"
        cur.execute(sql)
        rows=cur.fetchall()
        for j in range(len(rows)):
            menu[near[i]['sid']].append(rows[j]['menu'].strip())

    sql = f"select payments from customer where name='{session['name'].strip()}'"
    cur.execute(sql)
    row = cur.fetchall()

    pay = json.loads(row[0]['payments'])
  

    if request.method=='GET':
        if bucket[f'{session["name"]}'.strip()] == []:
            return render_template("order.html", menu=menu, bucket=[], near=near)
        elif pay == []:
            return render_template("order.html", menu=menu, bucket=bucket[f'{session["name"]}'.strip()], near=near, pay=False)
        else:
            return render_template("doorder.html", pay=pay)

    else:
        nows = datetime.now()
        pays=request.form.get('payment')
        lists=[]
        for i in range(len(bucket[f'{session["name"]}'.strip()])):
            lists.append(bucket[f'{session["name"]}'.strip()][i])
            lists[i]['name']=f'{session["name"]}'.strip()
            lists[i]['payments']=pays
            lists[i]['time']=str(nows)
            
        orderlist[nows] = lists
        bucket[f'{session["name"]}'.strip()]=[]
       

        return render_template("customer.html",order=True, session=session)

@app.route("/orderprint")
def orderprint():
    if orderlist=={}:
        return render_template("customer.html", order=False)

    newlist=[]
    for key in list(orderlist.keys()):
        for i in range(len(orderlist[key])):
            
            if orderlist[key][i]['name']==f'{session["name"]}'.strip():
                newlist.append(orderlist[key][i])
                
    return render_template("orderprint.html", orderlist=newlist)

@app.route("/delivery")
def delivery():
    conn=pg.connect(conn_str)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    lists=orderlist
    for key in list(orderlist.keys()):
        for i in range(len(orderlist[key])):
            sql=f"select phone, lng, lat from customer where name='{orderlist[key][i]['name']}'"
            cur.execute(sql)
            rows=cur.fetchall()

            lists[key][i]['phone']=rows[0]['phone']
            lists[key][i]['lng']=rows[0]['lng']
            lists[key][i]['lat']=rows[0]['lat']

    return render_template("orderprint.html", orderlist=lists, type='delivery', name=session['name'])


if __name__ == "__main__":

    app.run(debug = True)