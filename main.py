
"""
    Título: Proyecto de Tienda de Futbol
    Autor: Carlos Chávez
    Fecha: 2024-06-10
    Descripcion: Esta API permite gestionar productos de una tienda de futbol.
"""

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


# Inventario de productos de nuestra tienda de futbol (Simulación)
inventario = [
    {"id": 1, "nombre": "Jersey de futbol", "precio": 1500, "cantidad": 40},
    {"id": 2, "nombre": "Balon de futbol", "precio": 800, "cantidad": 25},
    {"id": 3, "nombre": "Gorra New Era", "precio": 600, "cantidad": 20}
]

# Control de identificadores
siguiente_id = 4


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
        return inventario
    except Exception as error:
        return  {str(error)} 

#POST Agrega producto a mi inventario
@app.post("/productos", response_model=respuestaProducto, status_code=status.HTTP_201_CREATED)
def addProducto(producto: crearProducto):
    try:

        nuevo_id = max((p["id"] for p in inventario), default=0) + 1
        nuevo_producto = {
            "id": nuevo_id,    
            "nombre": producto.nombre,
            "precio": producto.precio,
            "cantidad": producto.cantidad
        }

        inventario.append(nuevo_producto)

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
        for producto in inventario:
            if producto["id"] == producto_id:
                inventario.remove(producto) #Elimina el producto del inventario ya que encontró el id correspondiente
                return {"Message": "El producto fue eliminado"}
        return {"Message": "No fue encontrado el producto"}
    except HTTPException as errorHTTP:
        return {str(errorHTTP)}

    except Exception as error:
        return  {str(error)} 


@app.post("/productos/{producto_id}")
async def comprarProducto(producto_id: int):
    try:
        async with lock:
            for objeto in inventario:
                if objeto["id"] == producto_id:
                    if objeto["cantidad"] > 0:
                        await asyncio.sleep(0.05)
                        objeto["cantidad"] = objeto["cantidad"]-1
                        return {"Mensaje":"Producto comprado"}
                    else:
                        raise HTTPException(
                            status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "No hay stock de ese producto"
                        )

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "No existe el ID de ese producto"
            )

    except Exception as error:
        raise HTTPException (
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error al comprar producto: {str(error)}"
        )