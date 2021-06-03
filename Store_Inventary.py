#interfaz grafica
import tkinter as tk ##
from tkinter import ttk
from tkinter import *
from tkinter import messagebox as MessageBox
from tkinter import filedialog as fd
#modelo de conecion de sqlite
import sqlite3
from sqlite3 import Error
con=sqlite3.connect("mydatabase.db")
cursorObj=con.cursor()
#obtener el tiempo
from datetime import datetime

#leer codigo de barras
import cv2
import numpy as np
import imutils
import os  #traer archivos
import shutil

from pyzbar.pyzbar import decode
from PIL import Image

#base de datos
conVenta=sqlite3.connect("mydatabaseCOMPRAS.db")
cursorObjVenta=conVenta.cursor()

conHistorial=sqlite3.connect("mydatabaseHistorial.db")
cursorObjHistorial=conVenta.cursor()

#contraseña principal
paswordJ='bob'

#orientacion a objetos en ventana
class Product:

    #conectarse con la base de datos
    db_name='mydatabase.db'
    db_compras='mydatabaseCOMPRAS.db'
    db_historial='mydatabaseHistorial.db'
    db_clientes='mydatabaseClientes.db'
    db_usuarios='mydatabaseUsuarios.db'
    #crear interfaz
    def __init__(self,window,usuario,dinero):
        self.wind=window
        self.wind.title("Programa")
        #total
        self.total=DoubleVar(value=0)
        self.deposito=DoubleVar(value=0)
        self.cambio=DoubleVar(value=0)

        #calculadora
        self.calculadora=DoubleVar(value=0)

        #variables de la cuentas
        self.usuario=StringVar(value=usuario)
        self.total_caja=DoubleVar(value=0)
        tm=datetime.now()
        self.DiaInicio=IntVar(value=tm.day)
        self.HoraInicio=IntVar(value=tm.hour)
        self.MinutoInicio=IntVar(value=tm.minute)


        #menu
        menubar=Menu(self.wind)
        self.wind.config(menu=menubar)
        #corte
        filecorte=Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Usuario",menu=filecorte)
        filecorte.add_command(label="corte de cajero",command=lambda: self.historial_ventas(dinero,usuario))
        filecorte.add_separator()
        filecorte.add_command(label="Agregar usuario",command=self.agregar_Usuario)
        filecorte.add_command(label="Eliminar usuario")
        #------archivo
        filemenu=Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Archivo",menu=filemenu)
        filemenu.add_command(label="Abrir un historial",command=self.tablaHistorialOld)
        filemenu.add_separator()
        filemenu.add_command(label="Cerrar cesion",command=self.wind.quit)
        #clientes
        fileclientes=Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Clientes",menu=fileclientes)
        fileclientes.add_command(label="Historial de clientes",command=self.ventana_clientes)

        #crear un frame
        frame=LabelFrame(self.wind,text="Tabla de compras")
        frame.place(x=0,y=0,width=500,height=110)
        #frame.grid(row=0,column=0,columnspan=1,pady=0)

        #entrada de un nombre
        Label(frame,text="Nombre: ").place(x=0,y=10,width=60,height=10)
        self.name=Entry(frame)
        self.name.focus()  #para que parpadie al entrar
        self.name.place(x=56,y=6,width=180,height=20)

        #agregar precio
        Label(frame,text="Precio: ").place(x=0,y=36,width=60,height=10)
        self.price=Entry(frame)
        self.price.place(x=56,y=32,width=180,height=20)

        #agregar cantidad
        Label(frame,text="Cantidad: ").place(x=236,y=36,width=60,height=10)
        self.cantidad=Entry(frame)
        self.cantidad.place(x=300,y=32,width=100,height=20)

        #agrefar codigo
        Label(frame,text="Codigo: ").place(x=236,y=10,width=90,height=10)
        self.codigo=Entry(frame)
        self.codigo.place(x=300,y=10,width=100,height=20)

        self.imgEscaner=PhotoImage(file='escaner.png')
        ttk.Button(frame,text='Escanear',image=self.imgEscaner,command=lambda: self.guardarQRNewDato(1)).place(x=400,y=8,width=50,height=25)

        #boton agregar producto
        ttk.Button(frame,text="Guardar producto",command=self.add_product).place(x=55,y=60,width=181,height=30)
        self.imgEnviar=PhotoImage(file="enviar.png")
        self.imgE=Label(self.wind,image=self.imgEnviar)
        self.imgE.place(x=73,y=82,width=16,height=17)
        #boton de salida
        self.message=Label(text="",fg="white",bg=self.rgb(172, 187, 215),font=("verdana",12))
        self.message.place(x=0,y=110,width=781,height=30)
        #tabla
        self.tree=ttk.Treeview(self.wind,height=2,columns=("name","price","codigo"))
        self.tree.place(x=0,y=138,width=800,height=500)

        #encabezado de tabla
        self.tree.heading('#0',text='Nombre',anchor=CENTER)
        self.tree.heading('#1',text='Precio',anchor=CENTER)
        self.tree.heading('#2',text='cantidad',anchor=CENTER)
        self.tree.heading('#3',text='codigo de barras',anchor=CENTER)

        #scroollbar
        self.scrollbarO = ttk.Scrollbar(self.wind,orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbarO.place(x=780,y=138,width=30,height=500)
        self.tree.configure(yscrollcommand=self.scrollbarO.set)

        #botones de editar y eliminar
        ttk.Button(text="Eliminar",command=self.confirmarAutorizacionE).place(x=0,y=638,width=200,height=30)
        self.imgBasura=PhotoImage(file="basura.png")
        self.imgEliminar=Label(self.wind,image=self.imgBasura)
        self.imgEliminar.place(x=60,y=644,width=11,height=17)

        ttk.Button(text="Editar",command=self.confirmarAutorizacionC).place(x=200,y=638,width=200,height=30)
        self.imgEdit=PhotoImage(file="editar.png")
        self.img3=Label(self.wind,image=self.imgEdit)
        self.img3.place(x=259,y=642,width=20,height=20)

        ttk.Button(text="Devoluciones",command=lambda:self.rembolso(self.tree.selection())).place(x=400,y=638,width=200,height=30)
        self.imgRembolso=PhotoImage(file="renvolso.png")
        self.img4=Label(self.wind,image=self.imgRembolso)
        self.img4.place(x=438,y=643,width=20,height=20)

        ttk.Button(text='Buscar por codigo',command=self.ventanaBusquedaQR).place(x=600,y=638,width=180,height=30)
        self.img45=Label(self.wind,image=self.imgEscaner)
        self.img45.place(x=620,y=643,width=20,height=20)

        self.actualizarTabla()
        #tabla de compra
        frameCompras=LabelFrame(self.wind,text="Registra un nuevo producto")
        frameCompras.place(x=805,y=0,width=600,height=440)

        #tabla de compras
        self.troo=ttk.Treeview(self.wind,height=2,columns=2)
        self.troo.place(x=820,y=30,width=500,height=300)
        #encabezado de tabla
        self.troo.heading('#0',text='Producto',anchor=CENTER)
        self.troo.heading('#1',text='Precio',anchor=CENTER)
        #scroollbar
        self.scrollbar = ttk.Scrollbar(self.wind,orient=tk.VERTICAL, command=self.troo.yview)
        self.scrollbar.place(x=1320,y=30,width=30,height=300)
        self.troo.configure(yscrollcommand=self.scrollbar.set)
        #boton de salida para la segunda tabla
        self.messageVentas=Label(frameCompras,text="",fg="red")
        self.messageVentas.place(x=820,y=100,width=400,height=30)
        #botones de editar y eliminar
        ttk.Button(text="Cobrar",command=self.cobrar).place(x=820,y=330,width=200,height=30)
        self.imgCarro=PhotoImage(file="carro.png")
        self.imgCobrar=Label(self.wind,image=self.imgCarro)
        self.imgCobrar.place(x=876,y=334,width=20,height=20)

        ttk.Button(text="Eliminar producto",command=self.eliminarCompra).place(x=1000,y=330,width=200,height=30) #30
        self.imgEliminar2=Label(self.wind,image=self.imgBasura)
        self.imgEliminar2.place(x=1033,y=336,width=11,height=17)

        ttk.Button(text="+",command=lambda:self.agregarProducto(self.tree.selection())).place(x=1188,y=330,width=50,height=30)
        ttk.Button(text='Escanear',image=self.imgEscaner,command=self.agregarQRCompras).place(x=1236,y=330,width=50,height=25)
        self.actualizarTablaVentas()

        #total
        #Label(self.wind,text="TOTAL: ",fg="blue",font=("verdana",16)).place(x=806,y=385,width=94,height=30)
        Label(self.wind,text="$",fg="blue",font=("verdana",24)).place(x=880,y=378,width=20,height=40)
        Entry(self.wind,textvariable=self.total,state="readonly",fg="blue",font=("verdana",24)).place(x=900,y=380,width=200,height=40)

        #historial
        ttk.Button(text="Ventas del dia y devoluciones",command=lambda: self.historial_ventas(dinero,usuario)).place(x=1130,y=640,width=210,height=30)
        self.imgHistorial=PhotoImage(file="historial.png")
        self.imgH=Label(self.wind,image=self.imgHistorial)
        self.imgH.place(x=1135,y=645,width=18,height=18)

    #crear colores
    def rgb(self,a,b,c):
         return ("#%02x%02x%02x" % (a, b, c))

#LEER CODIGO DE BARRAS
    def guardarQR(self):
        ######-------------guardar el codigo QR-------------------#####
        #crear carpeta donde estaran los datos
        Datos='codigo'
        #capturar la imagen
        cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)

        #dibujar un rectangulo de lectura
        x1,y1=190,80
        x2,y2=450,398

        #guardar todas las imagenes que aparescan en video
        s=1;
        while s==1:
            ret,frame=cap.read()
            if ret==False: break
            #dibujar el rectangulo en pantalla y capturar esa imagen
            imAux=frame.copy()
            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
            objeto=imAux[y1:y2,x1:x2]
            #objeto=imutils.resize(objeto,width=30) #redimencionar la imagen

            #visualizar imagenes
            cv2.imshow('frame',frame)
            cv2.imshow('objeto',objeto)

            #guardar imagenes
            k=cv2.waitKey(1)
            if k==27:
                break
            #si presiono la tecla S guardar la imagen en la carpeta de objetos
            if k==ord('s'):
                cv2.imwrite(Datos+'.png',objeto)
                return self.leerQR()
                #parar de leer codigo
                s=0
        cap.release()
        cv2.destroyAllWindows()

    def leerQR(self):
        ######-------------lectura codigo QR-------------------#####
        #obtener la imagen para leer el codigo
        img=Image.open('codigo.png')
        result=decode(img) #obtener el QR
        #imprimir cadda numero del QR
        for i in result:
            codQR=i.data.decode("utf-8")
            return codQR

    def guardarQRNewDato(self,boton):
        #agregarle el valor
        QR=self.guardarQR()

        if (boton==1):
            self.codigo.delete(0,END)
            self.codigo.insert(0,str(QR))
        elif (boton==2):
            self.new_codigo.delete(0,END)
            self.new_codigo.insert(0,str(QR))
        elif (boton==3):
            self.BusquedaQR1.delete(0,END)
            self.BusquedaQR1.insert(0,str(QR))

    def agregarQRCompras(self):
        QR=self.guardarQR()

        #checar todos los codigos de barra que tengo y compararlos
        records=self.tree.get_children()

        for producto in records:
            codigo_producto=self.tree.item(producto)["values"][2]


            if (float(QR)==float(codigo_producto)):
                self.agregarProductoQR(producto)

    def buscarQR(self):
        QR=self.guardarQR()

        #checar todos los codigos de barra que tengo y compararlos
        records=self.tree.get_children()
        for producto in records:
            codigo_producto=self.tree.item(producto)["values"][2]


            if (float(QR)==float(codigo_producto)):
                self.agregarProductoQR(producto)

#ACCIONES DE OTROS ARTICULOS PERO CON CODIGOS
    def ventanaBusquedaQR(self):  #7501050411134.0
        self.ventanaBusquedaQR=Toplevel()
        self.ventanaBusquedaQR.title="Busqueda por QR"
        self.ventanaBusquedaQR.geometry("240x100")

        cuadro=LabelFrame(self.ventanaBusquedaQR,text='objeto').place(x=5,y=10,width=235,height=90)
        Label(self.ventanaBusquedaQR,text='codigo: ').place(x=15,y=25,width=50,height=30)


        self.BusquedaQR1=Entry(self.ventanaBusquedaQR,textvariable=StringVar(self.ventanaBusquedaQR,value='0'))
        self.BusquedaQR1.place(x=80,y=30,width=100,height=20)

        ttk.Button(self.ventanaBusquedaQR,text='Escanear',image=self.imgEscaner,command=lambda: self.guardarQRNewDato(3)).place(x=183,y=30,width=50,height=25)

        ttk.Button(self.ventanaBusquedaQR,text='Buscar',command=lambda: self.ventanaBusquedaQRDatos(self.BusquedaQR1.get())).place(x=80,y=50,width=100,height=30)


    def ventanaBusquedaQRDatos(self,codigo):
        self.ventanaBusquedaQR.destroy()
        #comprobar si existe un codigo
        try:
            codigo=float(codigo)
        except:
            MessageBox.showwarning("Error","Codigo no reconocido")
            return


        #--------------------buscar el objeto con codigo
        QR=codigo
        objetoNameQR=StringVar(value=0)
        objetoPrecioQR=StringVar(value=0)
        objetoCantidadQR=StringVar(value=0)
        objetoCodigoQR=StringVar(value=0)

        #checar todos los codigos de barra que tengo y compararlos
        records=self.tree.get_children()

        for producto in records:
            codigo_producto=self.tree.item(producto)["values"][2]

            #si es igual detener la busqueda
            if (float(QR)==float(codigo_producto)):
                objetoNameQR.set(self.tree.item(producto)["text"])
                objetoPrecioQR.set(self.tree.item(producto)["values"][0])
                objetoCantidadQR.set(self.tree.item(producto)["values"][1])
                objetoCodigoQR.set(self.tree.item(producto)["values"][2])
                break

        #--------------------crear la ventana de busqueda

        self.ventanaBusquedaQR=Toplevel()
        self.ventanaBusquedaQR.title="Busqueda"
        self.ventanaBusquedaQR.geometry("300x200")

        cuadro=self.ventanaBusquedaQR
        LabelFrame(self.ventanaBusquedaQR,text='objeto').grid(row=0,column=0)


        Label(cuadro,text='Nombre: ').grid(row=0,column=0)
        Entry(cuadro,textvariable=objetoNameQR).grid(row=0,column=1)

        Label(cuadro,text='Precio: ').grid(row=1,column=0)
        Entry(cuadro,textvariable=objetoPrecioQR).grid(row=1,column=1)

        Label(cuadro,text='Cantidad: ').grid(row=2,column=0)
        Entry(cuadro,textvariable=objetoCantidadQR).grid(row=2,column=1)

        Label(cuadro,text='Codigo: ').grid(row=3,column=0)
        Entry(cuadro,textvariable=objetoCodigoQR).grid(row=3,column=1)

        ttk.Button(cuadro,text='Agregar compra',command=lambda:self.agregarProducto(producto)).place(x=200,y=0,width=100,height=25)
        ttk.Button(cuadro,text='Devolucion',command=lambda:self.rembolso(producto)).place(x=200,y=25,width=100,height=25)
        ttk.Button(cuadro,text='Editar',command=lambda:self.edit_product(producto)).place(x=200,y=50,width=100,height=25)
        ttk.Button(cuadro,text='Eliminar',command=lambda:self.delete_product(producto)).place(x=200,y=75,width=100,height=25)


#TABLA DE LOS ARTICULOS
    #conectarme con la base de datos de los articulos
    def run_query(self,query,parameters=()):  #with
        with sqlite3.connect(self.db_name) as conn:
            cursor=conn.cursor()
            resultado=cursor.execute(query,parameters)
            conn.commit()
        return resultado
    def actualizarTabla(self):  #get_products
        self.borrar_ventanas()
        #limpiar los datos
        records=self.tree.get_children()
        for element in records:  #####
            self.tree.delete(element)

        #crear nuevos datos
        query="select id,name,price,cantidad,codigo from product"
        db_rows=self.run_query(query)

        #crear las nueva filas de las tablas
        for row in db_rows:
            self.tree.insert("",0,text=row[1],values=(row[2],row[3],row[4]),tags=("bg"))
            self.tree.tag_configure("bg",background="yellow")
     #comprobar si no estan basios
    def validation(self):
        return len(self.name.get())!=0 and len(self.price.get())!=0
     #agregar producto y eliminar producto
    def add_product(self):
         self.borrar_ventanas()
         if self.validation():
             query="insert into product (id,name,price,cantidad,codigo) values (NULL,?,?,?,?)"
             parameters=(self.name.get(),self.price.get(),self.cantidad.get(),self.codigo.get())
             self.run_query(query,parameters)
             self.message["text"]="Producto {} fue agregado".format(self.name.get())
             #limpiar los datos de interfazs
             self.name.delete(0,END)
             self.price.delete(0,END)
             self.cantidad.delete(0,END)
             self.codigo.delete(0,END)
             #actualizar
             self.actualizarTabla()

         else:
             self.message["text"]="El nombre y el precio son requeridos"
    def delete_product(self,IdDato):
        self.borrar_ventanas()
        self.message["text"]=""
        try:
            self.tree.item(IdDato)["text"][0]
        except IndexError as e:
            self.message["text"]="porfavor selecione un producto"
            return
        self.message["text"]=""
        name=self.tree.item(IdDato)["text"]
        query="DELETE FROM product WHERE name = ?"
        self.run_query(query,(name,))
        self.message["text"]="El dato {} fue eliminado correctamente".format(name)
        self.actualizarTabla()
    #editar dato
    def confirmarAutorizacionE(self):
        self.borrar_ventanas()
        self.autorizacion_wind=Toplevel()
        self.autorizacion_wind.title="Eliminar"
        self.autorizacion_wind.geometry("210x70")
        self.autorizacion_wind.resizable(0,0) #para que no se modifique las dimenciones
        Label(self.autorizacion_wind,text="............").grid(row=0,column=0)
        Label(self.autorizacion_wind,text="contaseña").grid(row=0,column=1)
        clave=Entry(self.autorizacion_wind,textvariable=StringVar(self.autorizacion_wind,value=""),show="*")
        clave.grid(row=1,column=1)
        Button(self.autorizacion_wind,text="Ingresar",command=lambda: self.comprobarC(clave.get(),1)).grid(row=3,column=1,sticky=E+W)
        Label(self.autorizacion_wind,text="............").grid(row=0,column=2)

    def comprobarC(self,clave,ventana):
        self.autorizacion_wind.destroy()
        if clave==paswordJ:
            if ventana==1:
                self.delete_product(self.tree.selection())
            else:
                self.edit_product(self.tree.selection())
        else:
            MessageBox.showwarning("Error","Pasword incorrecta")
            self.autorizacion_wind.destroy()

    def confirmarAutorizacionC(self):
        self.borrar_ventanas()
        self.autorizacion_wind=Toplevel()
        self.autorizacion_wind.title="autorizacion"
        self.autorizacion_wind.geometry("210x70")
        self.autorizacion_wind.resizable(0,0) #para que no se modifique las dimenciones
        Label(self.autorizacion_wind,text="............").grid(row=0,column=0)
        Label(self.autorizacion_wind,text="contaseña").grid(row=0,column=1)
        clave=Entry(self.autorizacion_wind,textvariable=StringVar(self.autorizacion_wind,value=""),show="*")
        clave.grid(row=1,column=1)
        Button(self.autorizacion_wind,text="Ingresar",command=lambda: self.comprobarC(clave.get(),2)).grid(row=3,column=1,sticky=E+W)
        Label(self.autorizacion_wind,text="............").grid(row=0,column=2)

    def edit_product(self,IdDato):
        self.borrar_ventanas()
        self.message["text"]=""

        try:
            self.tree.item(IdDato)["text"][0]
        except IndexError as e:
            self.message["text"]="porfavor selecione un producto"
            return

        name=self.tree.item(IdDato)["text"]
        old_price=self.tree.item(IdDato)["values"][0]
        old_cantidad=self.tree.item(IdDato)["values"][1]
        old_codigo=self.tree.item(IdDato)["values"][2]
        #caracteristicas de la ventana emergente
        self.edit_wind=Toplevel()
        self.edit_wind.title="Editar producto"
        self.edit_wind.geometry("320x200")
        self.edit_wind.resizable(0,0) #para que no se modifique las dimenciones

        #old name
        Label(self.edit_wind,text="Antiguo nombhre").grid(row=0,column=1)
        Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=name),state="readonly").grid(row=0,column=2)
        #new name
        Label(self.edit_wind,text="Nuevo nombre").grid(row=1,column=1)
        new_name=Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=name))
        new_name.grid(row=1,column=2)
        #old price
        Label(self.edit_wind,text="Antiguo precio").grid(row=2,column=1)
        Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_price),state="readonly").grid(row=2,column=2)
        #new price
        Label(self.edit_wind,text="Nuevo precio").grid(row=3,column=1)
        new_price=Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_price))
        new_price.grid(row=3,column=2)

        #old cantidad
        Label(self.edit_wind,text="Antigua cantidad").grid(row=4,column=1)
        Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_cantidad),state="readonly").grid(row=4,column=2)
        #Cantidad
        Label(self.edit_wind,text="Nueva cantidad").grid(row=5,column=1)
        new_cantidad=Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_cantidad))
        new_cantidad.grid(row=5,column=2)

        #old codigo
        Label(self.edit_wind,text="Antigua codigo").grid(row=6,column=1)
        Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_codigo),state="readonly").grid(row=6,column=2)
        #codigo
        Label(self.edit_wind,text="Nueva ccodigo").grid(row=7,column=1)
        self.new_codigo=Entry(self.edit_wind,textvariable=StringVar(self.edit_wind,value=old_codigo))
        self.new_codigo.grid(row=7,column=2)
        ttk.Button(self.edit_wind,text='Escanear',image=self.imgEscaner,command=lambda: self.guardarQRNewDato(2)).grid(row=7,column=3)

        #buton de guardado
        Button(self.edit_wind,text="Guardar",command=lambda: self.edit_records(new_name.get(),name,
        new_price.get(),old_price,new_cantidad.get(),old_cantidad,self.new_codigo.get(),old_codigo)).grid(row=8,column=2,sticky=W+E)

    def edit_records(self,new_name,name,new_price,old_price,new_cantidad,old_cantidad,new_codigo,old_codigo):

        self.borrar_ventanas()
        query="UPDATE product SET name=?, price=?,cantidad=?,codigo=? WHERE name=? AND price=? AND cantidad=? AND codigo=?"
        parameters=(new_name,new_price,new_cantidad,new_codigo,name,old_price,old_cantidad,old_codigo)
        self.run_query(query,parameters)
        self.message["text"]="El dato {} fue actualizado".format(name)
        self.actualizarTabla()

#TABLA DEL MANDADO
    #conectarme con la base de datos de las ventas
    def run_queryVentas(self,query,parameters=()):  #with
        with sqlite3.connect(self.db_compras) as conn:
            cursor=conn.cursor()
            resultado=cursor.execute(query,parameters) ##
            conn.commit()
        return resultado
    def actualizarTablaVentas(self):  #get_products

        #limpiar los datos
        self.total.set(0)   ###-------------------------
        records=self.troo.get_children()  ##aqui puedo eliminarla
        for element in records:
            self.troo.delete(element)

        #crear nuevos datos
        query="select id,name,price from ventas"
        db_rows=self.run_queryVentas(query)
        #crear las nueva filas de las tablas
        for row in db_rows:
            self.troo.insert("",0,text=row[1],values=(row[2],row[0]))
            #sumar el total de las compras
            self.total.set(self.total.get()+row[2])

    # agregar y eliminar
    def agregarProducto(self,IdDato):
        self.messageVentas["text"]=""
        try:
            self.tree.item(IdDato)["text"]
        except IndexError as e:
            self.message["text"]="porfavor selecione un producto"
            return

        #verificar si todavia existen productos en el inventario
        cantidad=self.tree.item(IdDato)["values"][1]
        cantidad=float(cantidad)
        if cantidad>0:
            query="insert into ventas (id,name,price) values (NULL,?,?)"
            name=self.tree.item(IdDato)["text"]
            price=self.tree.item(IdDato)["values"][0]
            parameters=(name,price)
            self.run_queryVentas(query,parameters)
            self.messageVentas["text"]="Producto {} fue agregado".format("gansito")
            #actualizar
            self.actualizarTablaVentas()
        elif cantidad<=0:
            self.message["text"]=""
            self.message["text"]="No hay suficiente producto"

    def agregarProductoQR(self,producto):
        self.messageVentas["text"]=""
        #verificar si todavia existen productos en el inventario
        cantidad=self.tree.item(producto)["values"][1]
        cantidad=float(cantidad)
        if cantidad>0:
            query="insert into ventas (id,name,price) values (NULL,?,?)"
            name=self.tree.item(producto)["text"]
            price=self.tree.item(producto)["values"][0]
            parameters=(name,price)
            self.run_queryVentas(query,parameters)
            self.messageVentas["text"]="Producto {} fue agregado".format("gansito")
            #actualizar
            self.actualizarTablaVentas()
        elif cantidad<=0:
            self.message["text"]=""
            self.message["text"]="No hay suficiente producto"

    def eliminarCompra(self):
        #ver si seleciono algo y si obtener el nombre del objeto
        self.messageVentas["text"]=""
        try:
            self.troo.item(self.troo.selection())["text"]
        except IndexError as e:
            self.messageVentas["text"]="porfavor selecione un producto"
            return
        self.messageVentas["text"]=""
        name=self.troo.item(self.troo.selection())["values"][1]

        #eliminar el dato seleccionado
        query="DELETE FROM ventas WHERE id = ?"
        self.run_queryVentas(query,(name,)) ##
        self.messageVentas["text"]="El dato {} fue eliminado correctamente".format(name)
        self.actualizarTablaVentas()

    #cobrar productos
    def cobrar(self):
        self.borrar_ventanas()
        self.cobrar_wind=Toplevel()
        self.cobrar_wind.title="Cobrar producto"
        self.cobrar_wind.geometry("320x200")
        #limpiar datos
        self.deposito.set(value=0)
        self.cambio.set(value=0)
        #total=self.troo.item(self.troo.selection())["text"]

        #interfa
        Label(self.cobrar_wind,text="TOTAL").grid(row=0,column=0)
        Entry(self.cobrar_wind,textvariable=self.total,state="readonly").grid(row=0,column=1)
        Label(self.cobrar_wind,text="Pago").grid(row=1,column=0)
        Entry(self.cobrar_wind,textvariable=self.deposito).grid(row=1,column=1)

        Label(self.cobrar_wind,text="Cambio").grid(row=2,column=0)
        Entry(self.cobrar_wind,textvariable=self.cambio,state="readonly").grid(row=2,column=1)

        Button(self.cobrar_wind,text="cobrar",command=self.cambioVenta).grid(row=3,column=1,sticky=W+E)
        self.imgCobrar2=Label(self.cobrar_wind,image=self.imgCarro).grid(row=3,column=0,sticky=W+E)

    def cambioVenta(self):
        diferencia=self.deposito.get()-self.total.get()
        if diferencia>=0:
            #dar cambio
            self.cambio.set(diferencia)

            #pasar por todos los datos del inventario
            listTienda=self.tree.get_children()
            for datoTienda in listTienda:
                #obtener los datos de cada objeto y ver si coinsiden
                productoTienda=self.tree.item(datoTienda)["text"]   #error
                precio=self.tree.item(datoTienda)["values"][0]
                cantidad=self.tree.item(datoTienda)["values"][1]
                codigoQR=self.tree.item(datoTienda)["values"][2]

                #pasar por todos los datos del la compra
                listVenta=self.troo.get_children()
                for datoVenta in listVenta:
                    #obtener el nombre del producto que estoy cobrando
                    productoVenta=self.troo.item(datoVenta)["text"]

                    if productoTienda==productoVenta:
                        #restarle una cantidad
                        precio=float(precio)
                        cantidad=float(cantidad)
                        new_cantidad=cantidad-1
                        codigoQR=str(codigoQR)

                        #checar si existe en el inventario
                        if (new_cantidad>=0):
                            #eliminar del deposito
                            query="UPDATE product SET name=?, price=?,cantidad=?,codigo=? WHERE name=? AND price=? AND cantidad=? AND codigo=?"
                            parameters=(productoTienda,precio,new_cantidad,codigoQR,productoTienda,precio,cantidad,codigoQR)
                            self.run_query(query,parameters)
                            #actualizar cantidad si todavia hay producto
                            cantidad=new_cantidad

                            #llevar esos productos al historial de venta
                            self.agregarProductoHistorial(productoTienda,precio,"Compra")



            self.actualizarTabla()
            #eliminar datos
            listVenta2=self.troo.get_children()
            for datoVenta2 in listVenta2:
                #name=self.troo.item(datoVenta2)["text"]
                id=self.troo.item(datoVenta2)["values"][1]
                #eliminar el dato seleccionado
                query="DELETE FROM ventas WHERE id = ?"
                self.run_queryVentas(query,(id,))
            self.actualizarTablaVentas()

        else:
            MessageBox.showwarning("Error","Deposite mas dinero")

#TABLA HISTORIAL
    #actualizar historial de ventas
    def run_queryHistorial(self,query,parameters=()):  #with
        with sqlite3.connect(self.db_historial) as conn:
            cursor=conn.cursor()
            resultado=cursor.execute(query,parameters)
            conn.commit()
        return resultado
    # agregar y editar
    def agregarProductoHistorial(self,nombre,precio,compra):

        query="insert into historial (id,name,price,fecha,compra) values (NULL,?,?,?,?)"

        fecha=datetime.now()
        #compra="Compra"
        parameters=(nombre,precio,fecha,compra)
        self.run_queryHistorial(query,parameters)

    def rembolso(self,IdDato):
        self.borrar_ventanas()
        self.message["text"]=""
        try:
            self.tree.item(IdDato)["text"][0]
        except IndexError as e:
            self.message["text"]="porfavor selecione un producto"
            return
        #caracteristicas de la ventana emergente
        self.edit_rembolso=Toplevel()
        self.edit_rembolso.title="Editar historial"
        self.edit_rembolso.geometry("320x200")

        #datos obtenidos
        name=self.tree.item(IdDato)["text"]
        price=self.tree.item(IdDato)["values"][0]
        cantidad=self.tree.item(IdDato)["values"][1]
        codigo=self.tree.item(IdDato)["values"][2]

        #Nombre del producto
        Label(self.edit_rembolso,text="Antiguo nombre").grid(row=0,column=1)
        Entry(self.edit_rembolso,textvariable=StringVar(self.edit_rembolso,value=name),state="readonly").grid(row=0,column=2)
        #precio
        Label(self.edit_rembolso,text="Antiguo precio").grid(row=1,column=1)
        Entry(self.edit_rembolso,textvariable=StringVar(self.edit_rembolso,value=price),state="readonly").grid(row=1,column=2)
        #cantidad
        Label(self.edit_rembolso,text="Antigua cantidad").grid(row=2,column=1)
        Entry(self.edit_rembolso,textvariable=StringVar(self.edit_rembolso,value=cantidad),state="readonly").grid(row=2,column=2)
        #Boton de goardado
        new_cantidad=float(cantidad)+1
        Button(self.edit_rembolso,text="Rembolsar",command=lambda: self.rembolso_actualizar(name,
        price,new_cantidad,cantidad,codigo)).grid(row=4,column=2,sticky=W+E)

    def rembolso_actualizar(self,name,price,new_cantidad,cantidad,codigo):
        #llamar a la funcion actualizar grafica de inventario
        self.edit_records(name,name,
        price,price,new_cantidad,cantidad,codigo,codigo)
        #llamar a la funcion para el historial
        self.agregarProductoHistorial(name,price,"rembolso")

    def actualizarHistorial(self,dinero):
        #------------------actualizar los datos de la tabla
        #limpiar los datos
        records=self.tree_historial.get_children()
        for element in records:
            self.tree_historial.delete(element)

        #crear nuevos datos
        query="select id,name,price,fecha,compra from historial"
        db_rows=self.run_queryHistorial(query)

        #aumentarle el valor del dinero
        dinero=float(dinero)
        self.total_caja.set(dinero)
        fecha=datetime.now()

        for row in db_rows:
            self.tree_historial.insert("",0,text=row[1],values=(row[2],row[4],row[3]))

            #comprobar si es una compra o un rembolso para sumar print(self.HoraInicio.get())
        #self.DiaInicio=StringVar(value=tm.day)
        #self.HoraInicio=StringVar(value=tm.hour)
        #self.MinutoInicio=StringVar(value=tm.minute)
            if str(row[4])=="Compra":
                self.total_caja.set(self.total_caja.get()+row[2])


    #abir historial de venta
    def historial_ventas(self,dinero,usuario):

        self.wind_historial=Toplevel()
        self.wind_historial.geometry("1100x400")
        self.wind_historial.resizable(0,0) #para que no se modifique las dimenciones
        self.wind_historial.title("Historial de ventas")


        #tabla de historial
        self.tree_historial=ttk.Treeview(self.wind_historial,height=2,columns=("name","price",""))
        self.tree_historial.place(x=20,y=10,width=1030,height=300)

        #encabezado de tabla
        self.tree_historial.heading('#0',text='Producto',anchor=CENTER)
        self.tree_historial.heading('#1',text='Precio',anchor=CENTER)
        self.tree_historial.heading('#2',text='devolucion o compra',anchor=CENTER)
        self.tree_historial.heading('#3',text='fecha',anchor=CENTER)

        #scroollbar
        scrollbarO_historial = ttk.Scrollbar(self.wind_historial,orient=tk.VERTICAL, command=self.tree_historial.yview)
        scrollbarO_historial.place(x=1050,y=10,width=20,height=300)
        self.tree_historial.configure(yscrollcommand=scrollbarO_historial.set)

        #------------------actualizar los datos de la tabla
        self.actualizarHistorial(dinero)
        #El total que tengo en caja
        Label(self.wind_historial,text="TOTAL",fg="blue",font=("verdana",16)).place(x=20,y=340,width=94,height=30)
        Entry(self.wind_historial,textvariable=self.total_caja,state="readonly",fg="blue",font=("verdana",16)).place(x=114,y=340,width=94,height=30)

        #corte
        ttk.Button(self.wind_historial,text='Corte',command= lambda: self.corteCaja(usuario,self.total_caja,dinero)).place(x=930,y=360,width=94,height=30)

    def borrar_historial(self,dinero):
        #limpiar los datos
        records=self.tree_historial.get_children()
        for element in records:
            #self.tree_historial.delete(element)
            name=self.tree_historial.item(element)["text"]
            print(name)
            query="DELETE FROM historial WHERE name = ?"
            self.run_queryHistorial(query,(name,))

        self.actualizarHistorial(dinero)
#TABLA CLIENTES
    def run_queryClientes(self,query,parameters=()):  #with
        with sqlite3.connect(self.db_clientes) as conn:
            cursor=conn.cursor()
            resultado=cursor.execute(query,parameters) ##
            conn.commit()
        return resultado

    def ventana_clientes_actualizar(self):
        #limpiar los datos
        records=self.tree_clientes.get_children()
        for element in records:  #####
            self.tree_clientes.delete(element)

        #crear nuevos datos
        query="select id,name,celular,pedido,fecha_pedido,fecha_entrega,anticipo from clientesAgenda"
        db_rows=self.run_queryClientes(query)

        #crear las nueva filas de las tablas
        for row in db_rows:
            self.tree_clientes.insert("",0,text=row[1],values=(row[2],row[3],row[4],row[5],row[6]),tags=("bg"))

    def guardar_cliente(self,name,celular,pedido,fecha_pedido,fecha_entrega,anticipo):
        #borrar todo registro del cliente
        self.nameCliente.delete(0,END)
        self.celularCliente.delete(0,END)
        self.pedidoCliente.delete(0,END)
        self.fecha_pedidoCliente.delete(0,END)
        self.fecha_entregaCliente.delete(0,END)
        self.anticipoCliente.delete(0,END)
        #insertar dato
        query="insert into clientesAgenda (id,name,celular,pedido,fecha_pedido,fecha_entrega,anticipo) values (NULL,?,?,?,?,?,?)"
        parameters=(name,celular,pedido,fecha_pedido,fecha_entrega,anticipo)
        self.run_queryClientes(query,parameters)
        #actualizar
        self.ventana_clientes_actualizar()

    def eliminar_clientes(self):
        try:
            self.tree_clientes.item(self.tree_clientes.selection())["text"]
        except IndexError as e:
            return MessageBox.showwarning("Error",'Elige a un cliente')

        self.message["text"]=""
        name=self.tree_clientes.item(self.tree_clientes.selection())["text"]
        query="DELETE FROM clientesAgenda WHERE name = ?"
        self.run_queryClientes(query,(name,))

        self.ventana_clientes_actualizar()

    def ventana_clientes(self):
        self.ventana_clientes=Toplevel()
        self.ventana_clientes.geometry("540x400")
        self.ventana_clientes.resizable(0,0) #para que no se modifique las dimenciones
        self.ventana_clientes.title("ventana de clientes")

        #crear un frame
        frame=LabelFrame(self.ventana_clientes,text='Añadir Clientes')
        frame.place(x=0,y=0,width=500,height=150)
        #nombre
        Label(frame,text='Nombre: ').place(x=60,y=2,width=60,height=10)
        self.nameCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.nameCliente.place(x=120,y=0,width=120,height=20)
        self.nameCliente.focus()
        #celular
        Label(frame,text='Celular: ').place(x=60,y=32,width=60,height=10)
        self.celularCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.celularCliente.place(x=120,y=30,width=120,height=20)
        #pedido
        Label(frame,text='Pedido: ').place(x=60,y=62,width=60,height=10)
        self.pedidoCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.pedidoCliente.place(x=120,y=60,width=120,height=20)
        #fecha pedido
        Label(frame,text='Fecha pedido: ').place(x=250,y=2,width=100,height=10)
        self.fecha_pedidoCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.fecha_pedidoCliente.place(x=340,y=0,width=120,height=20)
        #fecha entrega
        Label(frame,text='Fecha entrega: ').place(x=250,y=32,width=100,height=10)
        self.fecha_entregaCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.fecha_entregaCliente.place(x=340,y=30,width=120,height=20)
        #fecha entrega
        Label(frame,text='Antisipo: ').place(x=250,y=62,width=100,height=10)
        self.anticipoCliente=Entry(frame,textvariable=StringVar(self.ventana_clientes))
        self.anticipoCliente.place(x=340,y=60,width=120,height=20)
        #Boton de guardado
        ttk.Button(frame,text='Guardar',command=lambda: self.guardar_cliente(self.nameCliente.get(),
        self.celularCliente.get(),self.pedidoCliente.get(),self.fecha_pedidoCliente.get(),self.fecha_entregaCliente.get(),self.anticipoCliente.get())).place(x=165,y=90,width=210,height=30)
        self.imgE2=Label(self.ventana_clientes,image=self.imgEnviar)
        self.imgE2.place(x=222,y=112,width=16,height=17)

        #tabla
        self.tree_clientes=ttk.Treeview(self.ventana_clientes,height=6,columns=('name'))
        self.tree_clientes.place(x=0,y=160,width=500,height=200)
        #encabezado de tabla
        self.tree_clientes.heading('#0',text='Nombre',anchor=CENTER)
        self.tree_clientes.heading('#1',text='celular',anchor=CENTER)
        #scroollbar
        self.scrollbarO = ttk.Scrollbar(self.ventana_clientes,orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.scrollbarO.place(x=505,y=160,width=30,height=200)
        self.tree_clientes.configure(yscrollcommand=self.scrollbarO.set)
        self.ventana_clientes_actualizar()
        #boton de edicion
        ttk.Button(self.ventana_clientes,text='Revisar',command=self.ventana_clientes_editar).place(x=10,y=360,width=240,height=30)
        self.img6=Label(self.ventana_clientes,image=self.imgEdit)
        self.img6.place(x=80,y=364,width=20,height=20)
        #boton de eliminar
        ttk.Button(self.ventana_clientes,text='Eliminar',command=self.eliminar_clientes).place(x=250,y=360,width=250,height=30)
        self.imgEliminar3=Label(self.ventana_clientes,image=self.imgBasura)
        self.imgEliminar3.place(x=325,y=364,width=20,height=20)

    def ventana_clientes_editar(self):
        try:
            self.tree_clientes.item(self.tree_clientes.selection())["text"]


        except IndexError as e:
            return MessageBox.showwarning("Error",'Elige a un cliente')
        #obtener los datos del cliente
        name=self.tree_clientes.item(self.tree_clientes.selection())["text"] #nombre
        celular=self.tree_clientes.item(self.tree_clientes.selection())["values"][0] #celular
        pedido=self.tree_clientes.item(self.tree_clientes.selection())["values"][1] #pedido
        fecha_pedido=self.tree_clientes.item(self.tree_clientes.selection())["values"][2] #Fecha pedido
        fecha_entrega=self.tree_clientes.item(self.tree_clientes.selection())["values"][3] #Fecha entrega
        anticipo=self.tree_clientes.item(self.tree_clientes.selection())["values"][4] #anticipo

        #crear interfaz
        self.ventana_clientes_edit=Toplevel()
        self.ventana_clientes_edit.geometry("500x150")
        self.ventana_clientes_edit.resizable(0,0) #para que no se modifique las dimenciones
        self.ventana_clientes_edit.title("Revision de clientes")

        #crear un frame
        frame=LabelFrame(self.ventana_clientes_edit,text='Revision Clientes')
        frame.place(x=0,y=0,width=500,height=150)
        #nombre
        Label(frame,text='Nombre: ').place(x=60,y=2,width=60,height=10)
        new_name=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=name))
        new_name.place(x=120,y=0,width=120,height=20)
        #celular
        Label(frame,text='Celular: ').place(x=60,y=32,width=60,height=10)
        new_celular=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=celular))
        new_celular.place(x=120,y=30,width=120,height=20)
        #pedido
        Label(frame,text='Pedido: ').place(x=60,y=62,width=60,height=10)
        new_pedido=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=pedido))
        new_pedido.place(x=120,y=60,width=120,height=20)
        #fecha pedido
        Label(frame,text='Fecha pedido: ').place(x=250,y=2,width=100,height=10)
        new_fecha_pedido=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=fecha_pedido))
        new_fecha_pedido.place(x=340,y=0,width=120,height=20)
        #fecha entrega
        Label(frame,text='Fecha entrega: ').place(x=250,y=32,width=100,height=10)
        new_fecha_entrega=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=fecha_entrega))
        new_fecha_entrega.place(x=340,y=30,width=120,height=20)
        #fecha entrega
        Label(frame,text='Antisipo: ').place(x=250,y=62,width=100,height=10)
        new_anticipo=Entry(frame,textvariable=StringVar(self.ventana_clientes_edit,value=anticipo))
        new_anticipo.place(x=340,y=60,width=120,height=20)

        #Boton de actualizar
        botonG=ttk.Button(self.ventana_clientes_edit,text='Actualizar',command=lambda: self.actualizarCliente(name,celular,pedido,fecha_pedido,fecha_entrega,anticipo,new_name.get(),new_celular.get(),new_pedido.get(),new_fecha_pedido.get(),new_fecha_entrega.get(),new_anticipo.get()))
        botonG.place(x=200,y=107,width=100,height=30)

    def actualizarCliente(self,name,celular,pedido,fecha_pedido,fecha_entrega,anticipo,new_name,new_celular,new_pedido,new_fecha_pedido,new_fecha_entrega,new_anticipo):
        query="UPDATE clientesAgenda SET name=?, celular=?,pedido=?,fecha_pedido=?,fecha_entrega=?,anticipo=? WHERE name=? AND celular=? AND pedido=? AND fecha_pedido=? AND fecha_entrega=? AND anticipo=?"
        parameters=(new_name,new_celular,new_pedido,new_fecha_pedido,new_fecha_entrega,new_anticipo,name,celular,pedido,fecha_pedido,fecha_entrega,anticipo)
        self.run_queryClientes(query,parameters)
        self.ventana_clientes_actualizar()
        self.ventana_clientes_edit.destroy()

    #usuarios
    def agregar_Usuario(self):
        self.ventana_addUsuario=Toplevel()
        self.ventana_addUsuario.geometry("540x300")
        self.ventana_addUsuario.resizable(0,0) #para que no se modifique las dimenciones
        self.ventana_addUsuario.title("Caracteristicas de usuarios")

        #crear un frame
        frame=LabelFrame(self.ventana_addUsuario,text='Añadir usuario')
        frame.place(x=0,y=0,width=500,height=80)
        #nombre
        Label(frame,text='Usuario: ').place(x=60,y=2,width=80,height=10)
        self.usuario=Entry(frame,textvariable=StringVar(self.ventana_addUsuario))
        self.usuario.place(x=140,y=0,width=120,height=20)
        self.usuario.focus()
        #celular
        Label(frame,text='Contraseña: ').place(x=60,y=32,width=80,height=10)
        self.pasword=Entry(frame,textvariable=StringVar(self.ventana_addUsuario))
        self.pasword.place(x=140,y=30,width=120,height=20)

        ttk.Button(frame,text='+',command=lambda: self.agregarU(self.usuario.get(),self.pasword.get())).place(x=270,y=-5,width=30,height=25)

        #crear la tabla de usuarios que tengo
        frameT=LabelFrame(self.ventana_addUsuario,text='Usuarios')
        frameT.place(x=0,y=90,width=500,height=200)
        self.trooUsuarios=ttk.Treeview(frameT,height=2,columns=2)
        self.trooUsuarios.place(x=0,y=0,width=480,height=130)
        #encabezado de tabla
        self.trooUsuarios.heading('#0',text='Usuario',anchor=CENTER)
        self.trooUsuarios.heading('#1',text='Pasword',anchor=CENTER)
        #scrolbar
        self.scrollbarU = ttk.Scrollbar(self.ventana_addUsuario,orient=tk.VERTICAL, command=self.troo.yview)
        self.scrollbarU.place(x=505,y=90,width=30,height=200)
        self.trooUsuarios.configure(yscrollcommand=self.scrollbarU.set)

        self.ActualizarTablaUsuario()
        #crear botones
        ttk.Button(frameT,text="Editar").place(x=0,y=130,width=240,height=30)
        ttk.Button(frameT,text="Eliminar").place(x=240,y=130,width=240,height=30)

    def run_queryUsuarios(self,query,parameters=()):
         with sqlite3.connect(self.db_usuarios) as conn:
             cursor=conn.cursor()
             resultado=cursor.execute(query,parameters) ##
             conn.commit()
         return resultado

    def ActualizarTablaUsuario(self):
        #limpiar los datos
        records=self.trooUsuarios.get_children()
        for element in records:  #####
            self.trooUsuarios.delete(element)

        #crear nuevos datos
        query="select id,usuario,pasword from baseUsuarios"
        db_rows=self.run_queryUsuarios(query)

        #crear las nueva filas de las tablas
        for row in db_rows:
            self.trooUsuarios.insert("",0,text=row[1],values=row[2])


    def agregarU(self,usuario,pasword):
        #eliminar datos
        self.usuario.delete(0,END)
        self.pasword.delete(0,END)
        #añadir a usuario
        query="insert into baseUsuarios (id,usuario,pasword) values (NULL,?,?)"
        parameters=(usuario,pasword)
        self.run_queryUsuarios(query,parameters)
        #actualizar tabla
        self.ActualizarTablaUsuario()

    #borrar ventanas abiertas
    def borrar_ventanas(self):
        try:
            self.edit_wind.destroy()
        except:
            try:
                self.autorizacion_wind.destroy()
            except:
                try:
                    self.edit_rembolso.destroy()
                except:
                    return

#CORTE DE CAJA
    def corteCaja(self,usuario,total,dinero):

        self.wind_corteCaja=Toplevel()
        self.wind_corteCaja.geometry("400x200")
        self.wind_corteCaja.resizable(0,0) #para que no se modifique las dimenciones
        self.wind_corteCaja.title("corte")

        #
        frame=LabelFrame(self.wind_corteCaja,text="Tabla de compras")
        frame.place(x=0,y=0,width=400,height=120)

        nameUsuario=StringVar(value=usuario)
        Entry(frame,textvariable=nameUsuario,state="readonly").place(x=5,y=5)
        Label(frame,text="Total de caja",fg="blue",font=("verdana",12)).place(x=5,y=30,width=141,height=30)
        Entry(frame,textvariable=total,fg="blue",font=("verdana",12),state="readonly").place(x=162,y=30,width=120,height=30)

        #
        dinero=float(dinero)
        self.dinero_caja=DoubleVar(value=0)
        self.dinero_caja.set(dinero)
        self.dinero_caja.set(self.total_caja.get()-self.dinero_caja.get())
        Label(frame,text="Dinero ganado",fg="blue",font=("verdana",12)).place(x=5,y=60,width=141,height=30)
        Entry(frame,textvariable=self.dinero_caja,fg="blue",font=("verdana",12),state="readonly").place(x=162,y=60,width=120,height=30)

        ttk.Button(frame,text="corte",command=lambda:self.guardarCorte(dinero)).place(x=290,y=60,width=94,height=30)

    def guardarCorte(self,dinero):
        #crear carpeta donde estaran los datos
        Datos='historial'
        if not os.path.exists(Datos):
            os.makedirs(Datos)

        #crear archivo de text y agregarle el usuario que la esta usando
        fecha=datetime.now()
        fechaMes=str(fecha.month)
        fechaDia=str(fecha.day)
        fechaYear=str(fecha.year)
        fechaHora=str(fecha.hour)
        fechaMinuto=str(fecha.minute)

        archivo=open('historial_'+fechaMes+'_'+fechaDia+'_'+fechaYear+'_'+fechaHora+'_'+fechaMinuto+'.txt','w')
        archivo.write(str(self.usuario.get()))

        #agregar informacion al fichero
        records=self.tree_historial.get_children()
        query="select id,name,price,fecha,compra from historial"
        db_rows=self.run_queryHistorial(query)

        for row in db_rows:
            archivo.write(":\n")
            archivo.write(str(row))

        archivo.write("\nTotal: ")
        archivo.write(str(self.dinero_caja.get()))
        archivo.close()
        #mover el archivo a la carpeta
        shutil.move('historial_'+fechaMes+'_'+fechaDia+'_'+fechaYear+'_'+fechaHora+'_'+fechaMinuto+'.txt',Datos)

        #borrar historial
        self.borrar_historial(dinero)

    def tablaHistorialOld(self):
        #interfaz de abrir archivo
        nombreArchivo=fd.askopenfilename(title="Seleciona un archivo",filetypes=(("txt file","*.txt"),("todos los archivos","*.*")))

        #abrir archivo si lo seleciono
        if nombreArchivo!='':
            archivo=open(nombreArchivo,"r")
            textoLista=archivo.readlines() #leer la informacion y almacenarla en una lista
            archivo.close()
            #crear interfaz
            self.wind_historialOld=Toplevel()
            self.wind_historialOld.geometry("820x400")
            self.wind_historialOld.resizable(0,0) #para que no se modifique las dimenciones
            self.wind_historialOld.title("Historiales pasados")

            #crear la tabla
            self.treeOld=ttk.Treeview(self.wind_historialOld,height=0,columns=0)
            self.treeOld.place(x=10,y=10,width=800,height=500)

            #encabezado de tabla
            self.treeOld.heading('#0',text='Ventas del dia',anchor=CENTER)

            #scroollbar
            self.scrollbarOOld = ttk.Scrollbar(self.wind_historialOld,orient=tk.VERTICAL, command=self.treeOld.yview)
            self.scrollbarOOld.place(x=790,y=10,width=30,height=500)
            self.treeOld.configure(yscrollcommand=self.scrollbarOOld.set)

            #insertar datos en la tabla
            for row in textoLista:
                self.treeOld.insert("",0,text=row)

#crear base de datos

#base de datos
def crearBaseDatos():
    conexion=sqlite3.connect("mydatabase.db")
    try:
        conexion.execute("""CREATE TABLE "product"(
           'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
           'name' TEXT NOT NULL,
           'price' REAL NOT NULL,
           'cantidad' REAL NOT NULL,
           'codigo' REAL NOT NULL
        )""")

        cursor=conexion.execute("select id,name,price from product") #'SELECT*FROM product ORDER BY name DESC'
        for fila in cursor:
            print(fila)
        conexion.close()
        print("Se creo la tabla de articulos")
    except sqlite3.OperationalError:
        print("La tabla de articulos ya existe")
    conexion.close()
def crearBaseDatosClientes():
    conexion=sqlite3.connect("mydatabaseClientes.db")
    try:
        conexion.execute("""CREATE TABLE "clientesAgenda"(
           'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
           'name' TEXT NOT NULL,
           'celular' REAL NOT NULL,
           'pedido' REAL NOT NULL,
           'fecha_pedido' REAL NOT NULL,
           'fecha_entrega' REAL NOT NULL,
           'anticipo' REAL NOT NULL
        )""")

        cursor=conexion.execute("select id,name,price,fecha,compra from ventas") #'SELECT*FROM product ORDER BY name DESC'
        for fila in cursor:
            print(fila)
        conexion.close()
        print("Se creo la tabla de articulos")
    except sqlite3.OperationalError:
        print("La tabla de articulos ya existe")
    conexion.close()
def crearBaseDatosCompras():
    conexion=sqlite3.connect("mydatabaseCOMPRAS.db")
    try:
        conexion.execute("""CREATE TABLE "ventas"(
           'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
           'name' TEXT NOT NULL,
           'price' REAL NOT NULL
        )""")

        cursor=conexion.execute("select id,name,price from ventas") #'SELECT*FROM product ORDER BY name DESC'
        for fila in cursor:
            print(fila)
        conexion.close()
        print("Se creo la tabla de articulos")
    except sqlite3.OperationalError:
        print("La tabla de articulos ya existe")
    conexion.close()
def crearBaseDatosHistorial():
    conexion=sqlite3.connect("mydatabaseHistorial.db")
    try:
        conexion.execute("""CREATE TABLE "historial"(
           'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
           'name' TEXT NOT NULL,
           'price' REAL NOT NULL,
           'fecha' REAL NOT NULL,
           'compra' REAL NOT NULL
        )""")

        cursor=conexion.execute("select id,name,price,fecha,compra from ventas") #'SELECT*FROM product ORDER BY name DESC'
        for fila in cursor:
            print(fila)
        conexion.close()
        print("Se creo la tabla de articulos")
    except sqlite3.OperationalError:
        print("La tabla de articulos ya existe")
    conexion.close()
def crearBaseDatosUsuarios():
    conexion=sqlite3.connect("mydatabaseUsuarios.db")
    try:
        conexion.execute("""CREATE TABLE "baseUsuarios"(
           'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
           'usuario' TEXT NOT NULL,
           'pasword' REAL NOT NULL
        )""")

        cursor=conexion.execute("select id,name,price from product") #'SELECT*FROM product ORDER BY name DESC'
        for fila in cursor:
            print(fila)
        conexion.close()
        print("Se creo la tabla de articulos")
    except sqlite3.OperationalError:
        print("La tabla de articulos ya existe")
    conexion.close()
#USUARIOS
def ingresarUsuario(usuario,pasword,conf_usuario,confi_pasword,dinero):
    #comprobar que pusiste bien el dinero
    try:
        dinero=float(dinero)
    except:
        window_pas.message["text"]="Ingrese mas dinero"
        return
    #pasar por todos los usuarios
    i=0
    for name in conf_usuario:
        i=i+1
        #si coinsides con un usuario
        if usuario==name:
            #si tu contraseña es igual a la del usuario
            if pasword==confi_pasword[i-1]:
                window_pas.destroy()
                #crear pantalla usuario
                window = Tk()
                window.geometry("1500x700")
                application=Product(window,usuario,dinero)
                window.mainloop()
            else:
                #si no coinside parrar todo
                window_pas.message["text"]="{} no tiene esta contraseña".format(usuario)
                break

def run_queryUsuarios1(query,parameters=()):
     with sqlite3.connect('mydatabaseUsuarios.db') as conn:
         cursor=conn.cursor()
         resultado=cursor.execute(query,parameters) ##
         conn.commit()
     return resultado

if __name__=="__main__":
    #crear base de datos
    crearBaseDatos()
    crearBaseDatosClientes()
    crearBaseDatosCompras()
    crearBaseDatosHistorial()
    crearBaseDatosUsuarios()
    #pantalla de iniciar sesion
    window_pas=Tk()
    window_pas.geometry("250x150")
    window_pas.title("Usuario")
    window_pas.resizable(0,0) #para que no se modifique las dimenciones
    #hacer la conexion con la base de datos de usuario
    query="select id,usuario,pasword from baseUsuarios"
    db_rows=run_queryUsuarios1(query)
    USUARIOS_CAJA=["Administrador"]
    PASWORD_CAJA=["bob"]
    for row in db_rows:
        USUARIOS_CAJA.append(row[1])
        PASWORD_CAJA.append(row[2])

    #mensaje de usuario incorrecto
    window_pas.message=Label(text="",fg="red",font=("verdana",8))
    window_pas.message.place(x=0,y=10,width=250,height=30)

    Label(window_pas,text='Usuario').place(x=10,y=40)
    usuario=ttk.Combobox(window_pas,state="readonly")
    usuario['values']=(USUARIOS_CAJA)
    usuario.place(x=80,y=40)

    Label(window_pas,text='Pasword').place(x=10,y=60)
    pasword=Entry(window_pas,textvariable=StringVar(window_pas,value=''),show="*")
    pasword.place(x=80,y=60)

    Label(window_pas,text='Dinero en caja').place(x=0,y=80)
    dinero=Entry(window_pas,textvariable=StringVar(window_pas,value='0'))
    dinero.place(x=80,y=80)

    ttk.Button(window_pas,text="Ingresar",command=lambda: ingresarUsuario(usuario.get(),pasword.get(),USUARIOS_CAJA,PASWORD_CAJA,dinero.get())).place(x=80,y=100,width=126,height=30)


    window_pas.mainloop()
