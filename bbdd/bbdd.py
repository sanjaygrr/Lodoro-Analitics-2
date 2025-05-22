import pymysql
import pandas as pd

# Conexión a la base de datos
conn = pymysql.connect(
    host='34.174.37.175',
    user='u16uxkx6gdqb2',
    password='31|(533])1g&',
    database='db5skbdigd2nxo',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# Obtener todas las tablas de la base de datos
cursor.execute("SHOW TABLES")
tablas = [row[f'Tables_in_db5skbdigd2nxo'] for row in cursor.fetchall()]

# Exportar cada tabla completa a JSON
for tabla in tablas:
    try:
        print(f"🔄 Exportando tabla: {tabla}")
        df = pd.read_sql(f"SELECT * FROM {tabla}", conn)
        df.to_json(f"{tabla}.json", orient="records", indent=2, force_ascii=False)
        print(f"✅ Archivo creado: {tabla}.json")
    except Exception as e:
        print(f"❌ Error al exportar {tabla}: {e}")

conn.close()
