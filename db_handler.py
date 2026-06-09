import mysql.connector
import hashlib

class DBHandler:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "control_alumnos"

    def get_connection(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as e:
            print(f"Error de conexión a la base de datos: {e}")
            return None

    def verificar_login(self, usuario, password_plana):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT password_hash FROM usuarios WHERE usuario = %s"
            cursor.execute(query, (usuario,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()

            if resultado:
                hash_ingresado = hashlib.sha256(password_plana.encode('utf-8')).hexdigest()
                hash_almacenado = resultado['password_hash']
                return hash_ingresado == hash_almacenado
            return False
        except Exception as e:
            print(f"Error en verificar_login: {e}")
            return False

    def obtener_alumnos(self, busqueda=""):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            if busqueda and busqueda.strip():
                query = """
                    SELECT * FROM alumnos 
                    WHERE matricula LIKE %s OR apellido_paterno LIKE %s OR apellido_materno LIKE %s
                """
                like_val = f"%{busqueda}%"
                cursor.execute(query, (like_val, like_val, like_val))
            else:
                query = "SELECT * FROM alumnos"
                cursor.execute(query)
            
            alumnos = cursor.fetchall()
            cursor.close()
            conn.close()
            return alumnos
        except Exception as e:
            print(f"Error en obtener_alumnos: {e}")
            return []

    def insertar_alumno(self, datos):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO alumnos 
                (matricula, apellido_paterno, apellido_materno, nombres, curp, especialidad, telefono, ciudad_origen, estado, disciplinas, foto_ruta) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, datos)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en insertar_alumno: {e}")
            return False

    def actualizar_alumno(self, matricula, datos):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            query = """
                UPDATE alumnos SET 
                apellido_paterno = %s, apellido_materno = %s, nombres = %s, curp = %s, 
                especialidad = %s, telefono = %s, ciudad_origen = %s, estado = %s, 
                disciplinas = %s, foto_ruta = %s 
                WHERE matricula = %s
            """
            cursor.execute(query, (*datos, matricula))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en actualizar_alumno: {e}")
            return False

    def eliminar_alumno(self, matricula):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            query = "DELETE FROM alumnos WHERE matricula = %s"
            cursor.execute(query, (matricula,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en eliminar_alumno: {e}")
            return False