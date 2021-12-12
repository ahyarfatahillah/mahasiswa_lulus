from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app=Flask(__name__)
app.secret_key="Andi Muh Achyar Fatahillah Salam"

# koneksi key sdk firebase setting->service account
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)


db= firestore.client()


@app.route('/')
def index():
    if "login" not in session:
        return redirect(url_for("login"))

    list_mahasiswa=[]
    # Mendapatkan semua dokumen dalam koleksi (query)
    docs = db.collection('mahasiswa').order_by("nilai",direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        # to_dict mengubah object ke dict python
        mhs=doc.to_dict()
        mhs["id"]=doc.id
        # nama=mhs["nama"]
        # append untuk memasukkan mhs ke list_mahasiswa
        list_mahasiswa.append(mhs)
    
    return render_template('index.html',list_mahasiswa=list_mahasiswa)

@app.route('/hapus/<get_id>')
def hapus(get_id):
    db.collection("mahasiswa").document(get_id).delete()
    return redirect(url_for('index'))

@app.route('/api/mhs')
def api_mhs():
    list_mahasiswa=[]
    docs=db.collection("mahasiswa").stream()
    for doc in docs:
        mhs=doc.to_dict()
        mhs["id"]=doc.id
        mhs.pop("password")
        list_mahasiswa.append(mhs)
    return jsonify(list_mahasiswa)

@app.route('/api/mhs/detail/<user_id>')
def api_mhs_detail(user_id):
    mhs=db.collection("mahasiswa").document(user_id).get().to_dict()
    return jsonify(mhs["deskripsi"])

@app.route('/dashboard', methods=["GET","POST"])
def dashboard():
    if "login" not in session:
        return redirect(url_for("login"))

    session["user"]=db.collection("mahasiswa").document(session["user_id"]).get().to_dict()
    list_mahasiswa=[]
    docs = db.collection('mahasiswa').stream()
    for doc in docs:
        mhs=doc.to_dict()
        list_mahasiswa.append(mhs)

    if request.method=="POST":
        # update
        doc_ref = db.collection("mahasiswa").document(session["user_id"])
        data={
            'nama': request.form["nama"],
            'nilai': int(request.form["nilai"]),
            'password': request.form["password"]
        }
        doc_ref.update(data)
        session["user"]=data
        return render_template("dashboard.html")
    doc_ref = db.collection("mahasiswa").document(session["user_id"]).get().to_dict()
    return render_template('dashboard.html',list_mahasiswa=list_mahasiswa)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/login',methods=["GET","POST"])
def login():
    if "login" in session:
        return redirect(url_for("index"))
    pesan=''
    if request.method=='POST':
        
        docs = db.collection('mahasiswa').where("nama","==",request.form["username"]).stream()
        pesan="Username Salah"
        for doc in docs:
            mhs=doc.to_dict()
            if request.form["password"]==mhs["password"]:
                session["login"]=True
                session["user"]=mhs
                session["user_id"]=doc.id
                return redirect(url_for("index"))
            else:
                pesan="Password Salah"
    return render_template('login.html',pesan=pesan,status="danger")

@app.route('/register',methods=["GET","POST"])
def register():
    if "login" in session:
        return redirect(url_for("index"))
    pesan=""    
    if request.method=="POST":  
        docs=db.collection("mahasiswa").where("nama","==",request.form["nama"]).stream()
        for doc in docs:
            pesan="Nama Sudah Terdaftar"
            return render_template("register.html",pesan=pesan,status="secondary")
        data = {
            'nama': request.form["nama"],
            'nilai': int(request.form["nilai"]),
            'password': request.form["password"]
        }
        db.collection("mahasiswa").add(data)
        pesan="Akun Berhasil dibuat. Silahkan Login !"
        return render_template("login.html",pesan=pesan,status="success")
    return render_template('register.html',pesan=pesan)

if __name__=="__main__":
    # debug
    app.run(debug=True)