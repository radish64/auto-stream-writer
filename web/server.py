import psycopg2
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, Response, request, send_file, abort, jsonify, render_template
from uuid import uuid4
app = Flask(__name__)

#from https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask#61535724
def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

#pages
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file('./favicon.png', mimetype='image/png')

@app.route('/add-show/')
def add_show():
    id = request.args.get('id')
    print(id)
    return render_template('add.html', id=id)

@app.route('/add-host/')
def add_host():
    id = request.args.get('id')
    print(id)
    return render_template('add-host.html', id=id)

@app.route('/edit/')
def edit_menu():
    id = request.args.get('id')
    print(id)
    return render_template('edit.html', id=id)

@app.route('/edit-host/')
def edit_host_menu():
    id = request.args.get('id')
    print(id)
    return render_template('edit-host.html', id=id)

@app.route('/show/')
def show_page():
    id = request.args.get('id')
    print(id)
    return render_template('show.html', id=id)

@app.route('/host/')
def host_page():
    id = request.args.get('id')
    print(id)
    return render_template('host.html', id=id)

#API
@app.route('/list-shows/')
def send_list():
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()

    cur.execute('''select shows.showid, shows.name, hosts.name, shows.starttime, shows.endtime, shows.weekday from hostshowlink
                    join shows on hostshowlink.showid = shows.showid
                    join hosts on hostshowlink.hostid = hosts.hostid order by shows.starttime, shows.name;
                ''')
    select = cur.fetchall()

    finallist = list()
    k=0 #k is the index of the last finallist entry
    newlist=list(select[0])
    newlist[2] = list([newlist[2]])
    finallist.append(newlist)
    for i in range (1,len(select)):
        newlist=list(select[i])
        if (newlist[0] == finallist[k][0]):
            finallist[k][2] = list([finallist[k][2][0], newlist[2]])
        else:
            newlist[2] = list([newlist[2]])
            k+=1
            finallist.append(newlist)
        print (i)
        print (k)
        print(newlist)
        print(finallist)
        #print("k ",k)
        #print("newlist ",newlist)
        #print("finallist ",finallist[k])
        #print("--------------------------")

    print(finallist)
    con.close()
    return (jsonify(finallist))

@app.route('/details/')
def get_details():
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()

    id = request.args.get('id')
    
    cur.execute('''select shows.name, hosts.name, shows.starttime, shows.endtime, shows.weekday, shows.description, shows.photo, hosts.hostid from hostshowlink
                    join shows on hostshowlink.showid = shows.showid
                    join hosts on hostshowlink.hostid = hosts.hostid
                    where shows.showid = %s;
                ''', (id,))
    select = cur.fetchall()

    #thefuckinglength = len(select[0])
    #newlist = []
    newlist = list(select[0])
    newlist[1] = []
    newlist[1].append(list([select[0][1], select[0][7]]))
    #for i in range (thefuckinglength):
    #    newlist.append(select[0][i])
    if (len(select) > 1):
        if (select[0][0] == select[1][0]):
            newlist[1].append(list([select[1][1], select[1][7]]))
        else:
            print("what the fuck")
            abort(500)
    #else:
    #    newlist[1] = list([select[0][1], ])
    finallist = []
    finallist.append(newlist)

    #print (select)
    print(finallist)
    con.close()
    return(jsonify(finallist))
    #return (jsonify(select))

@app.route('/host-details/')
def get_host():
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()
    id = request.args.get('id')
    
    cur.execute('select * from hosts where hostid=%s', (id,))
    select = cur.fetchall()

    con.close()
    return(jsonify(select))


@app.route('/list-hosts/')
def get_hosts():
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()

    cur.execute('select hostid, name from hosts;')
    select = cur.fetchall()

    con.close()
    return(jsonify(select))


@app.route('/edit-submit/', methods=['POST'])
def add_task():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        id = request.form['id']
        sname = request.form['submitted-name']
        host1 = request.form['submitted-host1']
        host2 = request.form['submitted-host2']
        start = request.form['submitted-start']
        end = request.form['submitted-end']
        weekday = request.form['submitted-weekday']
        desc = request.form['submitted-desc']
        image = request.files['submitted-image']
        if image:
            image_name = make_unique(image.filename)
            imagepath='./static/'+image_name
            f = open(imagepath, "bx")
            f.write(image.read())
        else:
            image_name = None
        cur.execute("update shows set name = %s where showid = %s", (sname,id,))
        con.commit()
        cur.execute("update shows set starttime = %s where showid = %s", (int(start),id,))
        con.commit()
        cur.execute("update shows set endtime = %s where showid = %s", (int(end),id,))
        con.commit()
        cur.execute("update shows set weekday = %s where showid = %s", (int(weekday),id,))
        con.commit()
        cur.execute("update shows set description = %s where showid = %s", (desc,id,))
        con.commit()
        if(image):
            cur.execute("update shows set photo=%s where showid = %s", (image_name,id,))
            con.commit()
        cur.execute("delete from hostshowlink where showid = %s", (id,))
        con.commit()
        cur.execute("insert into hostshowlink values (%s, %s)", (host1,id,))
        con.commit()
        if (host2 != "None"):
            cur.execute("insert into hostshowlink values (%s, %s)", (host2,id,))
            con.commit()
        con.close()

        return(f'''
               <meta http-equiv="refresh" content="0; URL=/show?id={id}"> 
               <link rel="canonical" href="/show?id={id}"> 
               ''')
    else:
        abort(400)

@app.route('/edit-host-submit/', methods=['POST'])
def edit_host_sumbit():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        id = request.form['id']
        sname = request.form['submitted-name']
        bio = request.form['submitted-bio']
        image = request.files['submitted-image']
        if image:
            image_name = make_unique(image.filename)
            imagepath='./static/'+image_name
            f = open(imagepath, "bx")
            f.write(image.read())
        else:
            image_name = None
        cur.execute("update hosts set name = %s where hostid = %s", (sname,id,))
        con.commit()
        cur.execute("update hosts set bio = %s where hostid = %s", (bio,id,))
        con.commit()
        if(image):
            cur.execute("update hosts set photo = %s where hostid = %s", (image_name,id,))
        con.commit()
        return(f'''
               <meta http-equiv="refresh" content="0; URL=/host?id={id}"> 
               <link rel="canonical" href="/host?id={id}"> 
               ''')
    else:
        abort(400)
@app.route('/add-host-submit/', methods=['POST'])
def add_host_sumbit():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        sname = request.form['submitted-name']
        bio = request.form['submitted-bio']
        image = request.files['submitted-image']
        if image:
            image_name = make_unique(image.filename)
            imagepath='./static/'+image_name
            f = open(imagepath, "bx")
            f.write(image.read())
        else:
            image_name = None
        con.commit()
        if(image):
            cur.execute("insert into hosts (name, bio, photo) values (%s, %s, %s)", (sname, bio, image_name));
        else:
            cur.execute("insert into hosts (name, bio) values (%s, %s)", (sname, bio));
        con.commit()
        return('''
               <meta http-equiv="refresh" content="0; URL=/"> 
               <link rel="canonical" href="/"> 
               ''')
    else:
        abort(400)

@app.route('/add-show-submit/', methods=['POST'])
def add_show_submit():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        id = request.form['id']
        sname = request.form['submitted-name']
        host1 = request.form['submitted-host1']
        host2 = request.form['submitted-host2']
        start = request.form['submitted-start']
        end = request.form['submitted-end']
        weekday = request.form['submitted-weekday']
        desc = request.form['submitted-desc']
        image = request.files['submitted-image']
        if image:
            image_name = make_unique(image.filename)
            imagepath='./static/'+image_name
            f = open(imagepath, "bx")
            f.write(image.read())
        else:
            image_name = None
        con.commit()
        if(image):
            cur.execute("insert into shows (name, starttime, endtime, weekday, description, photo) values (%s, %s, %s, %s, %s, %s) returning showid", (sname, start, end, weekday, desc, image_name));
        else:
            cur.execute("insert into shows (name, starttime, endtime, weekday, description) values (%s, %s, %s, %s, %s) returning showid", (sname, start, end, weekday, desc));
        con.commit()
        sid = cur.fetchone()[0]
        cur.execute("insert into hostshowlink (hostid, showid) values (%s, %s)",(host1, sid))
        con.commit()
        if (host2 != "None"):
            cur.execute("insert into hostshowlink (hostid, showid) values (%s, %s)",(host2, sid))
            con.commit()
        return('''
               <meta http-equiv="refresh" content="0; URL=/"> 
               <link rel="canonical" href="/"> 
               ''')
    else:
        abort(400)

@app.route('/remove-show/', methods=['POST'])
def remove_show():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        id = request.form['id']

        print(id)

        cur.execute("delete from shows where showid = %s", (id,))
        con.commit()
        cur.execute("delete from hostshowlink where showid = %s", (id,))
        con.commit()
        con.close()

        return('''
               <meta http-equiv="refresh" content="0; URL=/"> 
               <link rel="canonical" href="/"> 
               ''')
    else:
        abort(400)

@app.route('/remove-host/', methods=['POST'])
def remove_host():
    if request.method == 'POST':
        con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
        cur = con.cursor()
        id = request.form['id']

        print(id)

        cur.execute("delete from hosts where hostid = %s", (id,))
        con.commit()
        cur.execute("delete from hostshowlink where hostid = %s", (id,))
        con.commit()
        con.close()

        return('''
               <meta http-equiv="refresh" content="0; URL=/"> 
               <link rel="canonical" href="/"> 
               ''')
    else:
        abort(400)


if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
