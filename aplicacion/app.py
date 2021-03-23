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
from flask import Flask, render_template, request,redirect, url_for, request, abort,\
    session,jsonify
from flask import send_file
from flask import flash
from datetime import datetime
import psycopg2
import numpy as np
from base64 import b64encode
from werkzeug.urls import url_parse
from keras.models import load_model
from matplotlib.image import imread
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
from werkzeug.utils import secure_filename
import re


app = Flask(__name__)
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
