"""Análisis del historial de ventas utilizando Pandas."""
from pathlib import Path
import pandas as pd

ARCHIVO_VENTAS = Path(__file__).resolve().parent / "ventas.csv"
COLUMNAS = ["id_venta", "fecha", "producto", "precio", "cantidad", "monto_total"]


def cargar_ventas():
    """Lee el CSV en cada consulta para que las gráficas usen las ventas recientes."""
    if not ARCHIVO_VENTAS.exists() or ARCHIVO_VENTAS.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNAS)

    try:
        ventas = pd.read_csv(ARCHIVO_VENTAS, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNAS)

    faltantes = set(COLUMNAS) - set(ventas.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en ventas.csv: {', '.join(sorted(faltantes))}")

    if ventas.empty:
        return ventas

    ventas["cantidad"] = pd.to_numeric(ventas["cantidad"], errors="coerce")
    ventas["monto_total"] = pd.to_numeric(ventas["monto_total"], errors="coerce")
    ventas["producto"] = ventas["producto"].astype("string").str.strip()
    ventas = ventas.dropna(subset=["producto", "cantidad", "monto_total"])
    ventas = ventas[ventas["producto"] != ""].copy()
    return ventas


def productos_mas_vendidos():
    """Agrupa por producto: unidades vendidas e ingresos obtenidos."""
    ventas = cargar_ventas()
    if ventas.empty:
        return []

    resultado = (
        ventas.groupby("producto", as_index=False)
        .agg(unidades=("cantidad", "sum"), monto_total=("monto_total", "sum"))
        .sort_values(["unidades", "monto_total"], ascending=[False, False])
    )
    resultado["unidades"] = resultado["unidades"].astype(int)
    resultado["monto_total"] = resultado["monto_total"].round(2)
    return resultado.to_dict(orient="records")


def indicadores_ventas():
    """KPIs para las cuatro tarjetas del dashboard."""
    ventas = cargar_ventas()
    if ventas.empty:
        return {
            "ingresos_totales": 0.0,
            "total_transacciones": 0,
            "ticket_promedio": 0.0,
            "producto_estrella": "Sin ventas",
            "unidades_producto_estrella": 0,
        }

    ingresos = float(ventas["monto_total"].sum())
    transacciones = len(ventas)
    top = productos_mas_vendidos()[0]
    return {
        "ingresos_totales": round(ingresos, 2),
        "total_transacciones": transacciones,
        "ticket_promedio": round(ingresos / transacciones, 2),
        "producto_estrella": top["producto"],
        "unidades_producto_estrella": top["unidades"],
    }


def ingresos_por_fecha():
    """Agrupa por día para mostrar la evolución de ingresos."""
    ventas = cargar_ventas()
    if ventas.empty:
        return []

    ventas["fecha"] = pd.to_datetime(
        ventas["fecha"], format="%Y-%m-%d %H:%M", errors="coerce"
    )
    ventas = ventas.dropna(subset=["fecha"])
    if ventas.empty:
        return []

    ventas["fecha"] = ventas["fecha"].dt.strftime("%Y-%m-%d")
    resultado = (
        ventas.groupby("fecha", as_index=False)
        .agg(monto_total=("monto_total", "sum"), transacciones=("id_venta", "count"))
        .sort_values("fecha")
    )
    resultado["monto_total"] = resultado["monto_total"].round(2)
    return resultado.to_dict(orient="records")
