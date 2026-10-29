
from locust import HttpUser, task, between
import random


class testing(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def comprarProducto(self):
        self.client.post("/productos/1")

    @task
    def getProductos(self):
        self.client.get("/")

    # POST - Agregar un producto nuevo
    @task
    def agregarProducto(self):
        self.client.post("/productos", json={
            "nombre": "Balon Adidas",
            "precio": 900,
            "cantidad": 15
        })

    # DELETE - Eliminar un producto
    @task
    def eliminarProducto(self):
        self.client.delete("/productos/2")
