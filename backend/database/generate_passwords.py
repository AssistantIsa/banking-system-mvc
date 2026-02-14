# generate_passwords.py
from werkzeug.security import generate_password_hash

print("=== GENERADOR DE HASHES DE CONTRASEÑAS ===")
print()
print("john / password1234:")
print(generate_password_hash("password1234"))
print()
print("admin / admin1234:")
print(generate_password_hash("admin1234"))
print()
print("=== INSTRUCCIONES ===")
print("1. Copia los hashes generados arriba")
print("2. Reemplaza los valores en seed_data.sql")
print("3. Ejecuta seed_data.sql en PostgreSQL")
