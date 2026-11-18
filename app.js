const API_URL = "http://127.0.0.1:8000/productos";
const API_URL_ANALISIS = "http://127.0.0.1:8000/api/analisis";

const formProducto = document.getElementById("formProducto");
const tablaProductos = document.getElementById("tablaProductos");
const totalProductos = document.getElementById("totalProductos");

let graficaProductos = null;
let graficaFechas = null;
const formatoPesos = new Intl.NumberFormat("es-MX", {
    style: "currency", currency: "MXN", maximumFractionDigits: 2
});

// Consulta una ruta y muestra un error si FastAPI no respondió correctamente.
async function consultarJSON(url, opciones) {
    const respuesta = await fetch(url, opciones);
    const contenido = await respuesta.json();
    if (!respuesta.ok) {
        throw new Error(contenido.detail || `Error HTTP ${respuesta.status}`);
    }
    return contenido;
}

// Evita que nombres de productos se interpreten como código HTML.
function escaparHTML(texto) {
    return String(texto).replace(/[&<>"']/g, caracter => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[caracter]);
}

// GET: mostrar los productos de productos.csv
async function cargarProductos() {
    try {
        const productos = await consultarJSON(API_URL);
        tablaProductos.innerHTML = "";
        totalProductos.textContent = `${productos.length} productos`;

        if (productos.length === 0) {
            tablaProductos.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">No hay productos registrados.</td></tr>';
            return;
        }

        productos.forEach(p => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td class="fw-bold text-secondary">#${p.id}</td>
                <td>${escaparHTML(p.nombre)}</td>
                <td class="fw-bold text-success">${formatoPesos.format(p.precio)}</td>
                <td><span class="badge ${p.cantidad < 10 ? 'bg-danger' : 'bg-success'}">${p.cantidad} unidades</span></td>
                <td class="text-end">
                    <button type="button" class="btn btn-outline-primary btn-sm me-1" onclick="comprarProducto(${p.id})">Comprar</button>
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="eliminarProducto(${p.id})">Eliminar</button>
                </td>`;
            tablaProductos.appendChild(fila);
        });
    } catch (error) {
        tablaProductos.innerHTML = '<tr><td colspan="5" class="text-danger py-3">Error al cargar productos. Revisa Uvicorn.</td></tr>';
        console.error("Error al cargar productos:", error);
    }
}

// POST: registrar un producto nuevo
async function agregarProducto(event) {
    event.preventDefault();
    const nuevoProducto = {
        nombre: document.getElementById("nombre").value.trim(),
        precio: Number(document.getElementById("precio").value),
        cantidad: Number(document.getElementById("cantidad").value)
    };
    try {
        await consultarJSON(API_URL, {
            method: "POST", headers: {"Content-Type": "application/json"},
            body: JSON.stringify(nuevoProducto)
        });
        formProducto.reset();
        await cargarProductos();
    } catch (error) {
        alert(`No se pudo registrar el producto: ${error.message}`);
    }
}

// DELETE: eliminar del inventario
async function eliminarProducto(id_producto) {
    try {
        await consultarJSON(`${API_URL}/${id_producto}`, {method: "DELETE"});
        await cargarProductos();
    } catch (error) {
        alert(`No se pudo eliminar el producto: ${error.message}`);
    }
}

// POST: comprar, actualizar inventario y refrescar el dashboard sin recargar.
async function comprarProducto(id_producto) {
    try {
        await consultarJSON(`${API_URL}/${id_producto}`, {method: "POST"});
        await cargarProductos();
        await cargarAnalisis();
    } catch (error) {
        alert(`No se pudo comprar el producto: ${error.message}`);
    }
}

// GET: KPIs y dos series de datos calculadas con Pandas en FastAPI.
async function cargarAnalisis() {
    const estado = document.getElementById("estadoDashboard");
    try {
        const [kpis, productos, fechas] = await Promise.all([
            consultarJSON(`${API_URL_ANALISIS}/kpis`),
            consultarJSON(`${API_URL_ANALISIS}/mas_vendidos`),
            consultarJSON(`${API_URL_ANALISIS}/ventas_fecha`)
        ]);

        document.getElementById("ingresosTotales").textContent = formatoPesos.format(kpis.ingresos_totales);
        document.getElementById("totalTransacciones").textContent = kpis.total_transacciones;
        document.getElementById("ticketPromedio").textContent = formatoPesos.format(kpis.ticket_promedio);
        document.getElementById("productoEstrella").textContent = kpis.producto_estrella;

        if (typeof Chart === "undefined") {
            throw new Error("No se cargó Chart.js; revisa tu conexión o la etiqueta script.");
        }
        // Chart.js requiere destruir la instancia anterior antes de redibujar.
        if (graficaProductos) graficaProductos.destroy();
        if (graficaFechas) graficaFechas.destroy();

        graficaProductos = new Chart(document.getElementById("myChart"), {
            type: "bar",
            data: {
                labels: productos.map(item => item.producto),
                datasets: [{
                    label: "Unidades vendidas",
                    data: productos.map(item => item.unidades),
                    backgroundColor: "rgba(22, 163, 74, 0.72)",
                    borderColor: "rgb(21, 128, 61)", borderWidth: 1, borderRadius: 5
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {legend: {display: false}},
                scales: {y: {beginAtZero: true, ticks: {precision: 0}}}
            }
        });

        graficaFechas = new Chart(document.getElementById("graficaFechas"), {
            type: "line",
            data: {
                labels: fechas.map(item => item.fecha),
                datasets: [{
                    label: "Ingresos diarios (MXN)",
                    data: fechas.map(item => item.monto_total),
                    borderColor: "rgb(37, 99, 235)",
                    backgroundColor: "rgba(37, 99, 235, 0.1)",
                    fill: true, tension: 0.25, pointRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {y: {beginAtZero: true}},
                plugins: {tooltip: {callbacks: {
                    label: contexto => formatoPesos.format(contexto.parsed.y)
                }}}
            }
        });

        estado.textContent = kpis.total_transacciones
            ? "Información actualizada con ventas.csv"
            : "Todavía no hay ventas. Las gráficas se llenarán al comprar productos.";
    } catch (error) {
        estado.textContent = `No se pudieron cargar las estadísticas: ${error.message}`;
        console.error("Error al cargar análisis:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();
    cargarAnalisis();
    formProducto.addEventListener("submit", agregarProducto);
});