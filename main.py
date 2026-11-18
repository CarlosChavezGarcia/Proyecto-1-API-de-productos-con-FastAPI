"""
    Título: Proyecto de Tienda de Futbol
    Autor: Carlos Chávez
    Fecha: 2024-06-10
    Descripcion: Esta API permite gestionar productos de una tienda de futbol.
"""

import csv
from datetime import datetime
import os
from datos import productos_mas_vendidos, indicadores_ventas, ingresos_por_fecha

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio 
from pydantic import BaseModel, Field


app = FastAPI(
    title="API de Tienda de Futbol",
    version="1.0.0"
)

# Permite comunicacion entre el backend y el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#Inicializamos variable lock (Condición de carrera)
lock = asyncio.Lock()

#Modelos de Pydantic
#Pedir al cliente que su petición debe estructurarse de esta manera.
class crearProducto(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")
    cantidad: int = Field(..., ge=0, description="stock del producto")


#La salida de datos de la API debe de estructurarse de esta manera.
class respuestaProducto(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int


#Estructura mensaje al cliente despues de hacer una operación
class respuestaMensaje(BaseModel):
    Message: str


#Ejemplo de API - GET para obtener mensaje inicial
@app.get("/")
def home():
    try:
        print("hola1") 
        resultado = 1 + 1
        print("hola2")
        return {"Message": "Hola bienvenido"}
    except Exception as error:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al hacer la operación: {str(error)}"
        )
       
   


#GET Obtiene lista de productos de mi inventario
@app.get("/productos")
def getProductos():
    try:
        inventario = cargar_inventario_csv()

        return inventario
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar productos: {str(error)}"
    )

#POST Agrega producto a mi inventario
@app.post("/productos", response_model=respuestaProducto, status_code=status.HTTP_201_CREATED)
def addProducto(producto: crearProducto):
    try:

        inventario = cargar_inventario_csv()
        nuevo_id = max((p["id"] for p in inventario), default=0) + 1
        nuevo_producto = {
            "id": nuevo_id,    
            "nombre": producto.nombre,
            "precio": producto.precio,
            "cantidad": producto.cantidad
        }

        inventario.append(nuevo_producto)

        guardar_inventario_CSV(inventario)

        return nuevo_producto
    
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar el producto: {str(error)}"
        )

    
#DELETE Borra producto de mi inventario
@app.delete("/productos/{producto_id}")
def deleteProducto(producto_id: int):
    try:
        inventario = cargar_inventario_csv()
        for producto in inventario:
            if producto["id"] == producto_id:
                inventario.remove(producto)
                guardar_inventario_CSV(inventario)
                return {"Message": "El producto fue eliminado"}
        return {"Message": "No fue encontrado el producto"}
    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el producto: {str(error)}"
        )

#POST - Comprar un producto de mi inventario
@app.post("/productos/{producto_id}", response_model=respuestaMensaje)
async def comprarProducto(producto_id: int):
    try:
        async with lock:
            inventario = cargar_inventario_csv()

            for objeto in inventario:
                if objeto["id"] == producto_id:
                    if objeto["cantidad"] > 0:
                        await asyncio.sleep(0.05)
                        objeto["cantidad"] = objeto["cantidad"] - 1

                        guardar_inventario_CSV(inventario)

                        registrar_venta_csv(
                            producto_nombre=objeto["nombre"],
                            precio=objeto["precio"],
                            cantidad=1
                        )

                        return respuestaMensaje(Message="Producto comprado")

                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No hay stock de ese producto"
                        )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe el ID de ese producto"
            )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comprar producto: {str(error)}"
        )

#cargar inventario desde un archivo CSV
def cargar_inventario_csv():
    productos = []

    if not os.path.exists("productos.csv"):
        return productos

    with open("productos.csv", mode= "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            productos.append({
                    "id": int(row["id"]),
                    "nombre": row["nombre"],
                    "precio": float(row["precio"]),
                    "cantidad": int(row["cantidad"])
                })

    return productos

#guardar inventario en un archivo CSV
def guardar_inventario_CSV(inventario):
    with open("productos.csv", mode="w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["id", "nombre", "precio", "cantidad"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for producto in inventario:
            writer.writerow(producto)

#registrar venta en un archivo CSV
def registrar_venta_csv(producto_nombre: str, precio: float, cantidad: int = 1):

    ruta = "ventas.csv"
    file_exists = os.path.exists(ruta) and os.path.getsize(ruta) > 0

    with open("ventas.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["id_venta", "fecha", "producto", "precio", "cantidad", "monto_total"])
            nuevo_id = 1
        else:
            with open("ventas.csv", "r", encoding="utf-8") as f:
                nuevo_id = sum(1 for line in f)

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        monto_total = precio * cantidad

        writer.writerow([nuevo_id, fecha_actual, producto_nombre, precio, cantidad, monto_total])


# Endpoints analíticos: Pandas se utiliza en datos.py
@app.get("/api/analisis/mas_vendidos")
def obtener_mas_vendidos():
    return productos_mas_vendidos()


@app.get("/api/analisis/kpis")
def obtener_kpis():
    return indicadores_ventas()


@app.get("/api/analisis/ventas_fecha")
def obtener_ventas_fecha():
    return ingresos_por_fecha()
