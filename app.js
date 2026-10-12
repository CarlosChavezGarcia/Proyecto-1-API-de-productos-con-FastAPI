
const API_URL = "http://127.0.0.1:8000/productos";

// Seleccion de elementos del DOM
const formProducto = document.getElementById("formProducto");
const tablaProductos = document.getElementById("tablaProductos");
const totalProductos = document.getElementById("totalProductos");


// 1. Funcion para cargar productos (GET)
async function cargarProductos() {
    try {
        const respuesta = await fetch(API_URL);

        if (!respuesta.ok) {
            throw new Error("Error al cargar productos");
        }

        const productos = await respuesta.json();

        tablaProductos.innerHTML = "";
        totalProductos.textContent = `${productos.length} productos`;

        if (productos.length === 0) {
            tablaProductos.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        No hay productos registrados en la tienda.
                    </td>
                </tr>`;
            return;
        }

        productos.forEach(p => {
            const fila = document.createElement("tr");

            const celdaId = fila.insertCell();
            const celdaNombre = fila.insertCell();
            const celdaPrecio = fila.insertCell();
            const celdaCantidad = fila.insertCell();
            const celdaAcciones = fila.insertCell();

            celdaId.textContent = `#${p.id}`;
            celdaId.className = "fw-bold text-secondary";

            celdaNombre.textContent = p.nombre;

            celdaPrecio.textContent = `$${p.precio}`;
            celdaPrecio.className = "text-success fw-bold";

            const cantidad = document.createElement("span");
            cantidad.className = `badge ${
                p.cantidad < 10 ? "bg-danger" : "bg-success"
            }`;
            cantidad.textContent = `${p.cantidad} unidades`;
            celdaCantidad.appendChild(cantidad);

            celdaAcciones.className = "text-end";

            const boton = document.createElement("button");
            boton.className = "btn btn-outline-danger btn-sm";
            boton.textContent = "Eliminar";
            boton.addEventListener("click", () => eliminarProducto(p.id));

            celdaAcciones.appendChild(boton);
            tablaProductos.appendChild(fila);
        });

    } catch (error) {
        console.error("Error al cargar productos:", error);
    }
}


// 2. Funcion para agregar productos (POST)
async function agregarProducto(event) {
    event.preventDefault();

    const nombre = document.getElementById("nombre").value;
    const precio = Number(document.getElementById("precio").value);
    const cantidad = Number(document.getElementById("cantidad").value);

    const nuevoProducto = {
        nombre,
        precio,
        cantidad
    };

    try {
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevoProducto)
        });

        if (!respuesta.ok) {
            throw new Error("Error al guardar producto");
        }

        formProducto.reset();
        await cargarProductos();

    } catch (error) {
        console.error("Error al agregar producto:", error);
    }
}


// 3. Funcion para eliminar productos (DELETE)
async function eliminarProducto(id_producto) {
    try {
        const respuesta = await fetch(
            `${API_URL}/${id_producto}`,
            {
                method: "DELETE"
            }
        );

        if (!respuesta.ok) {
            throw new Error("Error al eliminar producto");
        }

        await cargarProductos();

    } catch (error) {
        console.error("Error al eliminar producto:", error);
    }
}


// Cargar productos al abrir la pagina
document.addEventListener("DOMContentLoaded", cargarProductos);


// Registrar el evento del formulario una sola vez
formProducto.addEventListener("submit", agregarProducto);
