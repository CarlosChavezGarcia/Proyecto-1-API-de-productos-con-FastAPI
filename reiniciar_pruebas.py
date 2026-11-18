from pathlib import Path
import shutil

# Carpeta donde se encuentra este archivo
carpeta = Path(__file__).resolve().parent

# Restaurar el inventario original
shutil.copyfile(
    carpeta / "productos_original.csv",
    carpeta / "productos.csv"
)

# Eliminar las ventas de prueba
ventas = carpeta / "ventas.csv"

if ventas.exists():
    ventas.unlink()

print("Inventario restaurado correctamente.")
print("Ventas de prueba eliminadas.")
