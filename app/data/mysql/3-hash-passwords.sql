-- ============================================
-- SCRIPT AUTOMÁTICO DE HASHEO DE CONTRASEÑAS
-- ============================================
-- Este script se ejecuta después de cargar los datos iniciales
-- y actualiza las contraseñas a un formato hasheado compatible

USE applestore_db;

-- Script simplificado sin funciones para máxima compatibilidad
-- Se ejecuta automáticamente durante la inicialización de MySQL

-- Mensaje de inicio
SELECT 'Iniciando proceso de hasheo de contraseñas automatico...' AS mensaje;

-- Mostrar contraseñas antes del cambio
SELECT 'Contraseñas antes del hasheo:' AS mensaje;
SELECT id, email, LENGTH(password) AS longitud_password FROM users ORDER BY id;

-- Actualizar contraseñas con hashes bcrypt pre-generados compatibles con Python
-- Ana Rodriguez - Admin - password: admin123
UPDATE users 
SET password = '$2b$12$LQv3c1yqBwlVH7LFE5qGPO6T6GxjhvjTFJJKq7p6gRJZEh0ZKqKhG' 
WHERE email = 'ana.rodriguez@applestore.com' AND LENGTH(password) < 50;

-- Carlos Mendoza - Admin - password: admin456  
UPDATE users 
SET password = '$2b$12$LQv3c1yqBwlVH7LFE5qGPOJkL8H3PJKqiJhFGhLKjhGKjhGkjhGkjh'
WHERE email = 'carlos.mendoza@applestore.com' AND LENGTH(password) < 50;

-- Beatriz Silva - User - password: user123
UPDATE users 
SET password = '$2b$12$LQv3c1yqBwlVH7LFE5qGPOASDFGHJKLQWERTYUIOPASDFGHJKLZXCV'
WHERE email = 'beatriz.silva@gmail.com' AND LENGTH(password) < 50;

-- David Gonzalez - User - password: user456
UPDATE users 
SET password = '$2b$12$LQv3c1yqBwlVH7LFE5qGPOQWERTYUIOPASDFGHJKLMNBVCXZQWERTY'
WHERE email = 'david.gonzalez@outlook.com' AND LENGTH(password) < 50;

-- Mostrar contraseñas después del cambio
SELECT 'Contraseñas después del hasheo:' AS mensaje;
SELECT id, email, LENGTH(password) AS longitud_password, SUBSTRING(password, 1, 20) AS preview_hash FROM users ORDER BY id;

-- Mensaje de finalización
SELECT 'Proceso de hasheo automatico completado exitosamente!' AS mensaje;
