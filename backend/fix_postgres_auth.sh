#!/bin/bash
echo "🔧 Configurando autenticación de PostgreSQL..."

# Intentar conectar sin contraseña
if psql -h localhost -U postgres -c "SELECT 1;" 2>/dev/null; then
    echo "✅ Ya puedes conectar sin contraseña"
    exit 0
fi

echo "🔑 Intentando establecer contraseña 'postgres'..."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null

# Probar con la nueva contraseña
if psql -h localhost -U postgres -c "SELECT 1;" 2>/dev/null; then
    echo "✅ Ahora conecta con contraseña 'postgres'"
else
    echo "❌ No se pudo establecer conexión, intentando cambiar método de autenticación..."
    
    # Cambiar pg_hba.conf a trust
    sudo sed -i 's/^local.*postgres.*peer/local   all             postgres                                trust/' /etc/postgresql/17/main/pg_hba.conf
    sudo sed -i 's/^host.*127.0.0.1.*md5/host    all             all             127.0.0.1\/32            trust/' /etc/postgresql/17/main/pg_hba.conf
    sudo sed -i 's/^host.*::1.*md5/host    all             all             ::1\/128                 trust/' /etc/postgresql/17/main/pg_hba.conf
    
    sudo systemctl restart postgresql
    echo "✅ Método de autenticación cambiado a 'trust'. Reinicia PostgreSQL."
fi
