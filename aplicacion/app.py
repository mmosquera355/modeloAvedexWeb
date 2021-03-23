#---------------------------------------------------------------------
# Programa principal de avedex, renderización de templates, crud de base de datos y logica.
# Avedex main program, template rendering, database and logic.
# Maria Angelica Mosquera Moreno
# gihub: mmosquera355
# Julio 2020
# ---------------------------------------------------------------------

#Importaciones de librerias
# Library imports
import os
import zipfile
from flask import Flask, render_template, request,redirect, url_for, request, abort,\
    session,jsonify
from flask import send_file
from flask import flash
from datetime import datetime
from flask_material import Material
import psycopg2
import numpy as np
from flask_toastr import Toastr
from flask_login import LoginManager
from base64 import b64encode
from werkzeug.urls import url_parse
from keras.models import load_model
from matplotlib.image import imread
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
from werkzeug.utils import secure_filename
import re


app = Flask(__name__)
Material(app)
toastr = Toastr(app)
toastr.init_app(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



#conexion con la bd
'''connection = psycopg2.connect(user="postgres",
                                password="1234",
                                host="127.0.0.1",
                                port="5432",
                                database="pAvedex")'''
                
connection = psycopg2.connect(user="ufwllvzjcevwyu",
                                password="426dfefe8a08febe9c56d3b4fdab4c2956be05daa3a647d124304a60e730c6c7",
                                host="ec2-35-174-118-71.compute-1.amazonaws.com",
                                port="5432",
                                database="da6rsdbd1l724g")
#DB_URI = "postgresql+psycopg2://{username}:{password}@{hostname}/{databasename}".format(username="postgres", password="1234", hostname="localhost", databasename="avedex")
#app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

'''Definifición de rutas'''
@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada... te invitamos a ingresar una dirección valida."), 404

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/")
def upload_file():
    return render_template("index.html")

@app.route('/layoutPanel')
def layoutPanel():
    return render_template("panelMenu.html")

@app.route('/layoutlogin')
def layoutlogin():
    return render_template("login.html")


@app.route('/layoutRegistro')
def layoutRegistro():
    return render_template("registro.html")



'''Consultas a la base de datos'''
def getAllData(sentencia):
    try:
        cursor = connection.cursor()
        postgreSQL_select_Query = sentencia
        cursor.execute(postgreSQL_select_Query)
        datos = cursor.fetchall()  
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    return datos

def getAllDataParameter(sentencia, info):
    try:
        cursor = connection.cursor()
        postgreSQL_select_Query = sentencia
        cursor.execute(postgreSQL_select_Query, info)
        datos = cursor.fetchall()  
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    return datos

def getOneData(sentencia, info):
    try:
        cursor = connection.cursor()
        postgreSQL_select_Query = sentencia
        cursor.execute(postgreSQL_select_Query,info)
        dato = cursor.fetchone()  
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    return dato

def insertData(sentenciaInsert, info, accion):
    try:
        cursor = connection.cursor()
        cursor.execute(sentenciaInsert, info)
        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into table")
        if(accion == "eliminar"):
            flash("Registro eliminado correctamente")
        if(accion == "insertar"):
            flash("Registro insertado correctamente")
        if(accion == "actualizar"):
            flash("Registro actualizado correctamente")


    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into table", error)


@app.route('/registro',  methods=['POST'])
def registro():
    if request.method == 'POST' and 'username' in request.form and 'useremail' in request.form and 'pass' in request.form:
        unsername = request.form.get("username")
        print(unsername)
        email = request.form.get("useremail")
        #valid Email
        #definición de la expresión regular
        '''regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(regex,email)):  
            password = request.form.get("pass")
            valorUno="insertar"
            postgres_insert_query = """ INSERT INTO usuario (nombre, email, codigo_especialidad) VALUES (%s,%s,%s)"""
            record_to_insert = (unsername, email, 3)
            insertData(postgres_insert_query,record_to_insert, valorUno)
            postgres_insert_query = """ INSERT INTO login (email, password, codigo_especialidad) VALUES (%s,%s,%s)"""
            record_to_insert = (email, password, 3) 
            insertData(postgres_insert_query,record_to_insert, valorUno)
            session['loggedin'] = True
            session['username'] = unsername
            return render_template("perfil.html")
        else:
            flash("Ingrese un email correcto")

        return render_template('registro.html')'''
        print("Valid Email")  
        print(email)
        password = request.form.get("pass")
        valorUno="insertar"
        postgres_insert_query = """ INSERT INTO usuario (nombre, email, codigo_especialidad) VALUES (%s,%s,%s)"""
        record_to_insert = (unsername, email, 3)
        insertData(postgres_insert_query,record_to_insert, valorUno)
        postgres_insert_query = """ INSERT INTO login (email, password, codigo_especialidad) VALUES (%s,%s,%s)"""
        record_to_insert = (email, password, 3) 
        insertData(postgres_insert_query,record_to_insert, valorUno)
        session['loggedin'] = True
        session['username'] = unsername
        return render_template("perfil.html")
    return render_template("registro.html")


@app.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        print(username)
        sentencia=  """SELECT * FROM login WHERE email = %s AND password = %s """
        record_to_select = (username, password,)

        account = getOneData(sentencia,record_to_select )
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            if (account[3]==1):
                return render_template('panelMenu.html')
            else:
                return redirect(url_for('perfil'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Datos incorrectos")
            #msg = 'Incorrect username/password!'
    return render_template('login.html')


'''Tabla de usuarios y login'''

@app.route('/usuarios', methods=['GET','POST'])
def usuarios():

    usuarios = getAllData('select * from usuario ORDER BY codigo')
    especialidades =  getAllData('select * from especialidad')

    if request.method == 'POST':
        id = request.form.get("idusr")
        print(id)
        username = request.form.get("username")
        print(username)
        email = request.form.get("email")
        print(email)
        password = request.form.get("pass")
        print(password)
        especialidad = request.form.get('especialidad')
        codigo = request.form.get("idusrEl")
        print(codigo)
        emailEl = request.form.get("emailEl")
        print(emailEl)
        valor = request.form.get("valor")
        valorUno = request.form.get("valorUno")
        print(valor)
        if(valor is None):
            if(id!=''):
                print("actualizaremos")
                sql_update_query = """Update usuario set nombre = %s, email = %s, codigo_especialidad= %s where codigo = %s"""
                record_to_update = (username, email, especialidad,id)
                insertData(sql_update_query,record_to_update, valorUno)
                sql_update_query = """Update login set email = %s, codigo_especialidad= %s where email = %s"""
                record_to_update = (email, especialidad,email)
                insertData(sql_update_query,record_to_update, valorUno)

            else:
                print("insertaremos")
                postgres_insert_query = """ INSERT INTO usuario (nombre, email, codigo_especialidad) VALUES (%s,%s,%s)"""
                record_to_insert = (username, email, especialidad)
                insertData(postgres_insert_query,record_to_insert, valorUno)
                postgres_insert_query = """ INSERT INTO login (email, password, codigo_especialidad) VALUES (%s,%s,%s)"""
                record_to_insert = (email, password, especialidad) 
                insertData(postgres_insert_query,record_to_insert, valorUno)
        else:
            print(valor)
            sql_delete_query = """Delete from usuario where codigo = %s"""
            record_to_delete = (codigo,)
            insertData(sql_delete_query,record_to_delete, valor) 
            print(email)
            sql_delete_query_login = """Delete from login where email = %s"""
            record_to_delete_login = (emailEl,)
            insertData(sql_delete_query_login,record_to_delete_login, valor) 
        
        #realizando de nuevo las consultas
        usuarios = getAllData('select * from usuario ORDER BY codigo')
        especialidades =  getAllData('select * from especialidad')
    return render_template("usuarios.html", usuarios = usuarios, especialidades = especialidades )

''' tabla de misiones '''

@app.route('/misiones', methods=['GET','POST'])
def misiones():

    misiones = getAllData('select * from mision ORDER BY codigo')

    if request.method == 'POST':
        id = request.form.get("idmis")
        print(id)
        titulo = request.form.get("nombre")
        print(titulo)
        descripcion = request.form.get("descripcion")
        print(descripcion)
        puntos = request.form.get("puntos")
        print(puntos)
        codigo = request.form.get("idmisEl")
        print(codigo)
        valor = request.form.get("valor")
        valorUno = request.form.get("valorUno")
        print(valor)
        if(valor is None):
            if(id!=''):
                print("actualizaremos")
                sql_update_query = """Update mision set nombre = %s, descripcion = %s, puntos= %s where codigo = %s"""
                record_to_update = (titulo, descripcion, puntos,id)
                insertData(sql_update_query,record_to_update, valorUno)

            else:
                print("insertaremos")
                postgres_insert_query = """ INSERT INTO mision (nombre, descripcion, puntos) VALUES (%s,%s,%s)"""
                record_to_insert = (titulo, descripcion, puntos)
                insertData(postgres_insert_query,record_to_insert, valorUno)
        else:
            print(valor)
            sql_delete_query = """Delete from mision where codigo = %s"""
            record_to_delete = (codigo,)
            insertData(sql_delete_query,record_to_delete, valor) 
        
        #realizando de nuevo las consultas
        misiones = getAllData('select * from mision ORDER BY codigo')
    return render_template("misiones.html", misiones = misiones)


'''tabla de aves y familia'''

@app.route('/aves', methods=['GET','POST'])
def aves():

    aves = getAllData('select * from ave ORDER BY codigo')
    familias = getAllData('select * from familia ORDER BY codigo')

    if request.method == 'POST':
        id = request.form.get("idmave")
        print(id)
        nomCo = request.form.get("nomCo")
        print(nomCo)
        nomCi = request.form.get("nomCi")
        print(nomCi)
        genero = request.form.get("genero")
        print(genero)
        especie = request.form.get("especie")
        print(especie)
        descripcion = request.form.get("descripcion")
        print(descripcion)
        orden = request.form.get("orden")
        print(orden)
        colores = request.form.get("colores")
        print(colores)
        idFamiliaAve = request.form.get("idFamiliaAve")
        print(idFamiliaAve)
        codigo = request.form.get("idaveEl")
        print(codigo)
        valor = request.form.get("valor")
        valorUno = request.form.get("valorUno")
        print(valor)
        if(valor is None):
            if(id!=''):
                print("actualizaremos")
                sql_update_query = """Update ave set nombre_comun = %s, nombre_cientifico = %s, genero= %s,
                especie = %s, descripcion = %s, orden= %s,
                colores_principales = %s, codigo_familia = %s where codigo = %s"""
                record_to_update = (nomCo, nomCi, genero,especie,descripcion,orden,colores,idFamiliaAve,id)
                insertData(sql_update_query,record_to_update, valorUno)

            else:
                print("insertaremos")
                postgres_insert_query = """ INSERT INTO ave (nombre_comun, nombre_cientifico, genero,
                especie,descripcion,orden,colores_principales,codigo_familia) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                record_to_insert = (nomCo, nomCi, genero,especie,descripcion,orden,colores,idFamiliaAve)
                insertData(postgres_insert_query,record_to_insert, valorUno)
        else:
            print(valor)
            sql_delete_query = """Delete from ave where codigo = %s"""
            record_to_delete = (codigo,)
            insertData(sql_delete_query,record_to_delete, valor) 
        
        #realizando de nuevo las consultas
        aves = getAllData('select * from ave ORDER BY codigo')
        familias = getAllData('select * from familia ORDER BY codigo')
    imagenes = getAllData('select * from foto ORDER BY codigo')
    nrows = []
    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)
    return render_template("aves.html", aves = aves, familias=familias, imagenes=nrows)

@app.route('/familia', methods=['GET','POST'])
def familia():

    aves = getAllData('select * from ave ORDER BY codigo')
    familias = getAllData('select * from familia ORDER BY codigo')
    imagenes = getAllData('select * from foto ORDER BY codigo')

    nrows = []
    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)


    if request.method == 'POST':
        id = request.form.get("idfami")
        print(id)
        nombre = request.form.get("nombre")
        print(nombre)
        descripcion = request.form.get("descripcion")
        print(descripcion)
        codigo = request.form.get("idfamiEl")
        print(codigo)
        valor = request.form.get("valor")
        valorUno = request.form.get("valorUno")
        print(valor)
        if(valor is None):
            if(id!=''):
                print("actualizaremos")
                sql_update_query = """Update familia set nombre = %s, descripcion = %s where codigo = %s"""
                record_to_update = (nombre, descripcion, id)
                insertData(sql_update_query,record_to_update, valorUno)

            else:
                print("insertaremos")
                postgres_insert_query = """ INSERT INTO familia (nombre, descripcion) VALUES (%s,%s)"""
                record_to_insert = (nombre, descripcion)
                insertData(postgres_insert_query,record_to_insert, valorUno)
        else:
            print(valor)
            sql_delete_query = """Delete from familia where codigo = %s"""
            record_to_delete = (codigo,)
            insertData(sql_delete_query,record_to_delete, valor) 
        
        #realizando de nuevo las consultas
    aves = getAllData('select * from ave ORDER BY codigo')
    familias = getAllData('select * from familia ORDER BY codigo')
    imagenes = getAllData('select * from foto ORDER BY codigo')

    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)
    return render_template("aves.html", aves = aves, familias=familias, imagenes=nrows)

'''imagenes'''
def convertToBinaryData(file):
    #Convert digital data to binary format
    blobData = file.read()
    return blobData

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

@app.route('/imagen', methods = ['GET', 'POST'])
def imagen():
    aves = getAllData('select * from ave ORDER BY codigo')
    familias = getAllData('select * from familia ORDER BY codigo')
    imagenes = getAllData('select * from foto ORDER BY codigo')

    nrows = []
    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)

    #Comprehension lists python.

    if request.method == 'POST':
        
        valor = request.form.get("valor")
        print(valor)
        valorUno = request.form.get("valorUno")            
        codigo = request.form.get("idimgEl")
        
        print(codigo)
        #f.save(secure_filename(f.filename))
        if(valor is None):
            id = request.form.get("idimg")
            print(id)
            descripcion = request.form.get("desimg")
            print(descripcion)
            idave = request.form.get("idAveimg")
            f = request.files['file']
            empPhoto = convertToBinaryData(f)
            print(idave)
            if(id!=''):
                print("actualizaremos")
                sql_update_query = """Update foto set photo = %s, descripcion = %s, codigo_ave = %s where codigo = %s"""
                record_to_update = (empPhoto, descripcion, idave, id)
                insertData(sql_update_query,record_to_update, valorUno)

            else:
                print("insertaremos")
                postgres_insert_query = """ INSERT INTO foto (photo, descripcion,codigo_ave) VALUES (%s,%s,%s)"""
                record_to_insert = (empPhoto, descripcion,idave)
                insertData(postgres_insert_query,record_to_insert, valorUno)
        else:
            print("eliminaremos")

            print(valor)
            sql_delete_query = """Delete from foto where codigo = %s"""
            record_to_delete = (codigo,)
            insertData(sql_delete_query,record_to_delete, valor) 
        
        #realizando de nuevo las consultas
    #data = getAllData('SELECT * FROM ave INNER JOIN familia ON familia.codigo = ave.codigo_familia ORDER BY ave.codigo')
    aves = getAllData('select * from ave ORDER BY codigo')
    familias = getAllData('select * from familia ORDER BY codigo')
    imagenes = getAllData('select * from foto ORDER BY codigo')

    nrows = []
    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)
    
    return render_template("aves.html", aves = aves, familias=familias, imagenes=nrows)


'''Prueba beta de predicciones del modelo'''
@app.route("/perfil")
def perfil():
    print("hola soy maria")
    sentencia=  """SELECT * FROM ave WHERE codigo = %s """
    codigo=1
    record_to_select = (codigo,)
    ave = getOneData(sentencia,record_to_select )

    if ave:
        codigo_familia= ave[8]
        nombreCientificoAve= ave[2]

    sentenciaFamilia=  """SELECT * FROM familia WHERE codigo = %s """
    record_to_selectFamilia = (codigo_familia,)
    familia = getOneData(sentenciaFamilia,record_to_selectFamilia )
    sentenciaImagen=  """SELECT * FROM foto WHERE codigo_Ave = %s """
    record_to_selectImagen = (codigo,)
    imagenes = getAllDataParameter(sentenciaImagen,record_to_selectImagen )
    nrows = []
    for a,b,c,d in imagenes:
        nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
        nrows.append(nrow)
    return render_template("perfil.html", ave=ave, familia=familia, imagenes= nrows, nombre= nombreCientificoAve)

UPLOAD_FOLDER = 'aplicacion\static\imagenes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/clasificar', methods = ['GET', 'POST'])
def clasificar():
    model = load_model('aplicacion\static\modelResnet50Epoch100Step15.h5')
    classes=('Amazilia_tzacatl','Brotogeris_jugularis','Buteo_magnirostris','Columbina_talpacoti',
        'Coragyps_atratus','Melanerpes_rubricapillus','Pitangus_sulphuratus','Tiaris_bicolor','Tyrannus_melancholicus')
    id_classes=(8,12,10,4,9,11,7,5,6)


    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        direc= "aplicacion/static/imagenes/"+ filename
        print(direc)
        print(type(direc))
        img = image.load_img(direc, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        prediccion= model.predict(x)
        predicted_class_indices = np.argmax(prediccion, axis = 1)
        print(predicted_class_indices)
        print(classes[predicted_class_indices[0]])
        sentencia=  """SELECT * FROM ave WHERE codigo = %s """
        codigo=id_classes[predicted_class_indices[0]]
        record_to_select = (codigo,)
        ave = getOneData(sentencia,record_to_select )

        if ave:
            codigo_familia= ave[8]
            nombreCientificoAve= ave[2]

        sentenciaFamilia=  """SELECT * FROM familia WHERE codigo = %s """
        record_to_selectFamilia = (codigo_familia,)
        familia = getOneData(sentenciaFamilia,record_to_selectFamilia )
        sentenciaImagen=  """SELECT * FROM foto WHERE codigo_Ave = %s """
        record_to_selectImagen = (codigo,)
        imagenes = getAllDataParameter(sentenciaImagen,record_to_selectImagen )
        nrows = []
        for a,b,c,d in imagenes:
            nrow = tuple([a, b64encode(b).decode("utf-8"),c,d])
            nrows.append(nrow)

    return render_template("perfil.html", ave=ave, familia=familia, imagenes= nrows, nombre= nombreCientificoAve)

'''@app.route('/clasificarappBD', methods = ['GET', 'POST'])
def clasificarappBD():
    postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (8,2 ,34,datetime.now(), "Primera prueba")
    insertData(postgres_insert_query,record_to_insert, "insertar")

    postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (4,3 ,34,datetime.now(), "Primera prueba")
    insertData(postgres_insert_query,record_to_insert, "insertar")

    postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (5,4 ,34,datetime.now(), "Primera prueba")
    insertData(postgres_insert_query,record_to_insert, "insertar")
    
    postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (6,5 ,34,datetime.now(), "Primera prueba")
    insertData(postgres_insert_query,record_to_insert, "insertar")

    postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (7,6 ,34,datetime.now(), "Primera prueba")
    insertData(postgres_insert_query,record_to_insert, "insertar")'''






'''Prueba beta de predicciones del modelo desde la app'''
@app.route('/clasificarapp', methods = ['GET', 'POST'])
def clasificarapp():
    model = load_model('aplicacion\static\modelResnet50Epoch100Step15.h5')
    classes=('Amazilia_tzacatl','Brotogeris_jugularis','Buteo_magnirostris','Columbina_talpacoti',
        'Coragyps_atratus','Melanerpes_rubricapillus','Pitangus_sulphuratus','Tiaris_bicolor','Tyrannus_melancholicus')
    id_classes=(5,9,7,1,6,8,4,2,3)


    if request.method == 'POST':
        idUsuario = request.form.get("idUser")
        latitud = request.form.get("latitud")
        logitud = request.form.get("longitud")
        print(latitud)
        print(logitud)
        print(idUsuario)
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        direc= "aplicacion/static/imagenes/"+ filename
        print(direc)
        print(type(direc))
        img = image.load_img(direc, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        prediccion= model.predict(x)
        predicted_class_indices = np.argmax(prediccion, axis = 1)
        print("soy angelica")
        print(predicted_class_indices)
        print("holaa")
        print(type(predicted_class_indices))
        print(classes[predicted_class_indices[0]])
        codigo=id_classes[predicted_class_indices[0]]
        print(type(codigo))
        print(codigo)
        #insertando la ubicación
        postgres_insert_query = """ INSERT INTO ubicacion(latitud,longitud,descripcion) VALUES (%s,%s,%s)"""
        record_to_insert = (latitud,logitud ,"Prueba desde sistema web")
        insertData(postgres_insert_query,record_to_insert, "insertar")

        #obteniendo el id de la ubicación insertada
        sentenciaUbicacion=  """SELECT MAX(codigo) FROM ubicacion"""
        ubicacion = getAllData(sentenciaUbicacion )
        print(type(ubicacion))
        print(ubicacion[0][0])
        #insertando la predicción con el usuario
        postgres_insert_query = """ INSERT INTO usuario_ave_ubicacion(codigo_ave,codigo_ubicacion,codigo_usuario,fecha_hora_identificacion,observacion) VALUES (%s,%s,%s,%s,%s)"""
        record_to_insert = (codigo,ubicacion[0][0] ,idUsuario,datetime.now(), "Prueba desde sistema web")
        insertData(postgres_insert_query,record_to_insert, "insertar")
    respuesta= jsonify({"status":"success","prediction":codigo,"confidence":classes[predicted_class_indices[0]],"upload_time":datetime.now()})
    print(respuesta)
    return jsonify({
                "status":"success",
                "prediction":codigo,
                "confidence":classes[predicted_class_indices[0]],
                "upload_time":datetime.now()
                })
