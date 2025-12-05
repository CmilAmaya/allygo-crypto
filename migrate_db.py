# migrate_db.py
"""
Script para agregar las columnas de recuperación de contraseña a la tabla users existente
"""
import asyncio
import os
from databases import Database
from sqlalchemy import create_engine, text

async def add_password_reset_columns():
    """Agrega las columnas reset_password_token y reset_password_expires a la tabla users"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL no está configurada")
        return False
    
    database = Database(DATABASE_URL)
    
    try:
        # Conectar a la base de datos
        await database.connect()
        print("✅ Conectado a la base de datos")
        
        # Verificar si las columnas ya existen
        check_columns_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name IN ('reset_password_token', 'reset_password_expires');
        """
        
        existing_columns = await database.fetch_all(check_columns_query)
        existing_column_names = [row[0] for row in existing_columns]
        
        # Agregar columna reset_password_token si no existe
        if 'reset_password_token' not in existing_column_names:
            add_token_column = """
            ALTER TABLE users 
            ADD COLUMN reset_password_token VARCHAR(10);
            """
            await database.execute(add_token_column)
            print("✅ Columna 'reset_password_token' agregada")
        else:
            print("ℹ️  Columna 'reset_password_token' ya existe")
        
        # Agregar columna reset_password_expires si no existe
        if 'reset_password_expires' not in existing_column_names:
            add_expires_column = """
            ALTER TABLE users 
            ADD COLUMN reset_password_expires TIMESTAMP;
            """
            await database.execute(add_expires_column)
            print("✅ Columna 'reset_password_expires' agregada")
        else:
            print("ℹ️  Columna 'reset_password_expires' ya existe")
        
        print("🎉 Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        return False
        
    finally:
        await database.disconnect()
        print("🔌 Desconectado de la base de datos")

async def verify_migration():
    """Verifica que las columnas se hayan agregado correctamente"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    database = Database(DATABASE_URL)
    
    try:
        await database.connect()
        
        # Verificar estructura de la tabla
        verify_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
        """
        
        columns = await database.fetch_all(verify_query)
        
        print("\n📋 Estructura actual de la tabla 'users':")
        print("-" * 50)
        for column in columns:
            nullable = "NULL" if column[2] == "YES" else "NOT NULL"
            print(f"  {column[0]:<25} {column[1]:<15} {nullable}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando la migración: {str(e)}")
        return False
        
    finally:
        await database.disconnect()

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    print("=" * 60)
    
    # Ejecutar migración
    success = asyncio.run(add_password_reset_columns())
    
    if success:
        print("\n🔍 Verificando migración...")
        asyncio.run(verify_migration())
    else:
        print("\n❌ La migración falló")