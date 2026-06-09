CREATE DATABASE IF NOT EXISTS control_alumnos;
USE control_alumnos;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS alumnos (
    matricula VARCHAR(20) PRIMARY KEY,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    nombres VARCHAR(50) NOT NULL,
    curp VARCHAR(18) NOT NULL UNIQUE,
    especialidad VARCHAR(100) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    ciudad_origen VARCHAR(100) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    disciplinas VARCHAR(255),
    foto_ruta VARCHAR(255)
);

INSERT INTO usuarios (usuario, password_hash) 
VALUES ('admin', '240aa35a7e08414b43c96821449219731531776a5a92d809f4dd47e73130d951')
ON DUPLICATE KEY UPDATE usuario=usuario;