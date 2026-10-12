
"""
    Título: Proyecto de Tienda de Futbol
    Autor: Carlos Chávez
    Fecha: 2024-06-10
    Descripcion: Esta API permite gestionar productos de una tienda de futbol.
"""

import asyncio
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Inventario de productos
inventario = [
    {"id": 1, "nombre": "Jersey de futbol", "precio": 1500, "cantidad": 40},
    {"id": 2, "nombre": "Balon de futbol", "precio": 800, "cantidad": 25},
    {"id": 3, "nombre": "Gorra New Era", "precio": 600, "cantidad": 20}
]

# Control de identificadores
siguiente_id = 4


# Modelos de Pydantic
class crearProducto(BaseModel):
    nombre: str = Field(
        ..., min_length=2, max_length=100,
        description="Nombre del producto"
    )
    precio: float = Field(
        ..., ge=0, description="Precio del producto"
    )
    cantidad: int = Field(
        ..., ge=0, description="Cantidad del producto"
    )


class respuestaProducto(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int


# GET: Pagina principal
@app.get("/")
def home():
    return {"Message": "Hola bienvenido"}


# 1. GET: Consultar productos
# Async con await para simular una espera asincrona
@app.get("/productos", response_model=List[respuestaProducto])
async def getProductos():
    await asyncio.sleep(1)
    return inventario


# 2. POST: Agregar producto
# Async sin await porque se trabaja con una lista en memoria
@app.post(
    "/productos",
    response_model=respuestaProducto,
    status_code=status.HTTP_201_CREATED
)
async def addProducto(producto: crearProducto):
    global siguiente_id

    nuevo_producto = {
        "id": siguiente_id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "cantidad": producto.cantidad
    }

    inventario.append(nuevo_producto)
    siguiente_id += 1

    return respuestaProducto(**nuevo_producto)


# 3. DELETE: Eliminar producto
# Async sin await porque se elimina de una lista en memoria
@app.delete("/productos/{producto_id}")
async def deleteProducto(producto_id: int):
    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}

    raise HTTPException(
        status_code=404,
        detail="No fue encontrado el producto"
    )
