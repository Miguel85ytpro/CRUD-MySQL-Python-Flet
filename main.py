import flet as ft
from db_handler import DBHandler

db = DBHandler()

def main(page: ft.Page):
    page.title = "Sistema de Control Escolar - CRUD Alumnos"
    page.window_width = 1100
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    id_editar = None
    ruta_foto_seleccionada = "default.png"

    txt_user = ft.TextField(label="Usuario", icon="person", width=300)
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, icon="lock", width=300)
    lbl_login_error = ft.Text("", color=ft.Colors.RED)

    txt_mat = ft.TextField(label="Matrícula", width=140, max_length=20)
    txt_apat = ft.TextField(label="Apellido Paterno", width=220)
    txt_amat = ft.TextField(label="Apellido Materno", width=220)
    txt_nom = ft.TextField(label="Nombre(s)", width=250)
    txt_curp = ft.TextField(label="CURP", width=220, max_length=18, hint_text="18 caracteres")
    txt_esp = ft.TextField(label="Especialidad", width=220)
    txt_tel = ft.TextField(label="Teléfono", width=160, max_length=10)
    txt_ciudad = ft.TextField(label="Ciudad de Origen", width=200)
    
    drop_estado = ft.Dropdown(
        label="Estado", width=200,
        options=[ft.dropdown.Option("Chihuahua"), ft.dropdown.Option("Durango"), ft.dropdown.Option("Coahuila"), ft.dropdown.Option("Nuevo León")]
    )
    
    chk_futbol = ft.Checkbox(label="Fútbol")
    chk_basquet = ft.Checkbox(label="Básquetbol")
    chk_voley = ft.Checkbox(label="Vóleibol")

    txt_buscar = ft.TextField(label="Buscar por Matrícula o Apellido", width=400, suffix_icon="search")
    tabla_alumnos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Matrícula")),
            ft.DataColumn(ft.Text("Nombre Completo")),
            ft.DataColumn(ft.Text("CURP")),
            ft.DataColumn(ft.Text("Especialidad")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def validar_curp_change(e):
        txt_curp.value = txt_curp.value.upper()
        page.update()

    def validar_tel_change(e):
        txt_tel.value = "".join([c for c in txt_tel.value if c.isdigit()])
        page.update()

    txt_curp.on_change = validar_curp_change
    txt_tel.on_change = validar_tel_change

    def entrar_sistema(e):
        if db.verificar_login(txt_user.value, txt_pass.value):
            lbl_login_error.value = ""
            cargar_vista_crud()
        else:
            lbl_login_error.value = "Credenciales incorrectas. Intente de nuevo."
            page.update()

    def recargar_tabla(e=None):
        tabla_alumnos.rows.clear()
        try:
            alumnos = db.obtener_alumnos(txt_buscar.value)
            if alumnos is not None:
                for alu in alumnos:
                    nombre_completo = f"{alu['apellido_paterno']} {alu['apellido_materno']} {alu['nombres']}"
                    mat = alu['matricula']
                    
                    btn_editar = ft.IconButton(
                        icon="edit", 
                        icon_color=ft.Colors.BLUE, 
                        on_click=lambda e, m=mat: preparar_edicion(m),
                        tooltip="Editar Alumno"
                    )
                    btn_eliminar = ft.IconButton(
                        icon="delete", 
                        icon_color=ft.Colors.RED, 
                        on_click=lambda e, m=mat: confirmar_borrado(m),
                        tooltip="Eliminar Alumno"
                    )

                    tabla_alumnos.rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(mat)),
                            ft.DataCell(ft.Text(nombre_completo)),
                            ft.DataCell(ft.Text(alu['curp'])),
                            ft.DataCell(ft.Text(alu['especialidad'])),
                            ft.DataCell(ft.Row([btn_editar, btn_eliminar]))
                        ]
                    ))
        except Exception as ex:
            show_snack(f"Error al leer datos: {str(ex)}", ft.Colors.RED)
        page.update()

    txt_buscar.on_change = recargar_tabla

    def guardar_alumno(e):
        nonlocal id_editar
        if not all([txt_mat.value, txt_apat.value, txt_nom.value, txt_curp.value, txt_tel.value]):
            show_snack("Por favor complete los campos obligatorios (*)", ft.Colors.ORANGE)
            return
        
        if len(txt_curp.value) != 18:
            show_snack("La CURP debe tener exactamente 18 caracteres", ft.Colors.RED)
            return
        
        if len(txt_tel.value) != 10:
            show_snack("El teléfono debe contar con 10 dígitos", ft.Colors.RED)
            return

        deportes = []
        if chk_futbol.value: deportes.append("Fútbol")
        if chk_basquet.value: deportes.append("Básquet")
        if chk_voley.value: deportes.append("Vóley")
        deportes_str = ", ".join(deportes)

        datos = (
            txt_apat.value, txt_amat.value, txt_nom.value, txt_curp.value,
            txt_esp.value, txt_tel.value, txt_ciudad.value, drop_estado.value or "No especificado",
            deportes_str, ruta_foto_seleccionada
        )

        try:
            if id_editar is None:
                exito = db.insertar_alumno((txt_mat.value, *datos))
                msg = "Alumno registrado correctamente" if exito else "La matrícula o CURP ya existen en el sistema."
            else:
                exito = db.actualizar_alumno(id_editar, datos)
                msg = "Registro actualizado correctamente" if exito else "Ocurrió un error al actualizar."
                id_editar = None
                txt_mat.disabled = False
                
            show_snack(msg, ft.Colors.GREEN if exito else ft.Colors.RED)
            if exito:
                limpiar_formulario()
                recargar_tabla()
        except Exception as ex:
            show_snack(f"Error crítico en la base de datos: {str(ex)}", ft.Colors.RED)

    def preparar_edicion(matricula):
        nonlocal id_editar
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
            alu = cursor.fetchone()
            cursor.close()
            conn.close()

            if alu:
                id_editar = matricula
                txt_mat.value = alu['matricula']
                txt_mat.disabled = True
                txt_apat.value = alu['apellido_paterno']
                txt_amat.value = alu['apellido_materno']
                txt_nom.value = alu['nombres']
                txt_curp.value = alu['curp']
                txt_esp.value = alu['especialidad']
                txt_tel.value = alu['telefono']
                txt_ciudad.value = alu['ciudad_origen']
                drop_estado.value = alu['estado']
                
                chk_futbol.value = "Fútbol" in alu['disciplinas']
                chk_basquet.value = "Básquet" in alu['disciplinas']
                chk_voley.value = "Vóley" in alu['disciplinas']
                
                page.update()
        except Exception as ex:
            show_snack(f"Error al cargar edición: {str(ex)}", ft.Colors.RED)

    def confirmar_borrado(matricula):
        def proceder_borrado(e):
            if db.eliminar_alumno(matricula):
                show_snack("Alumno eliminado exitosamente", ft.Colors.GREEN)
            else:
                show_snack("Error al eliminar el registro", ft.Colors.RED)
            dialogo.open = False
            recargar_tabla()
            page.update()

        def cancelar_borrado(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmación Emergente"),
            content=ft.Text(f"¿Está seguro de que desea eliminar permanentemente al alumno con matrícula: {matricula}?"),
            actions=[
                ft.TextButton("Sí, Eliminar", on_click=proceder_borrado),
                ft.TextButton("Cancelar", on_click=cancelar_borrado)
            ]
        )
        page.dialog = dialogo
        dialogo.open = True
        page.update()

    def limpiar_formulario():
        txt_mat.value = ""
        txt_apat.value = ""
        txt_amat.value = ""
        txt_nom.value = ""
        txt_curp.value = ""
        txt_esp.value = ""
        txt_tel.value = ""
        txt_ciudad.value = ""
        drop_estado.value = None
        chk_futbol.value = False
        chk_basquet.value = False
        chk_voley.value = False
        page.update()

    def show_snack(texto, color):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def cargar_vista_login():
        page.controls.clear()
        contenido_login = ft.Column(
            [
                ft.Text("Control de Acceso Escolar", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                ft.Container(height=20),
                txt_user,
                txt_pass,
                lbl_login_error,
                ft.Container(height=10),
                ft.ElevatedButton("Iniciar Sesión", on_click=entrar_sistema, width=300, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        contenedor_centrado = ft.Container(
            content=contenido_login,
            alignment=ft.Alignment(0, 0),
            expand=True
        )
        
        page.add(contenedor_centrado)

    def cargar_vista_crud():
        page.controls.clear()
        recargar_tabla()
        
        panel_formulario = ft.Container(
            content=ft.Column([
                ft.Text("Datos del Alumno", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                txt_mat,
                ft.Row([txt_apat, txt_amat]),
                txt_nom,
                ft.Row([txt_curp, txt_esp]),
                ft.Row([txt_tel, txt_ciudad]),
                drop_estado,
                ft.Text("Disciplinas Deportivas:", weight=ft.FontWeight.W_600),
                ft.Row([chk_futbol, chk_basquet, chk_voley]),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton("Guardar Registro", icon="save", on_click=guardar_alumno, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                    ft.TextButton("Limpiar", on_click=lambda e: limpiar_formulario())
                ])
            ], scroll=ft.ScrollMode.AUTO),
            width=500, padding=15, border_radius=10, bgcolor=ft.Colors.BLACK12
        )

        panel_consulta = ft.Column([
            ft.Text("Buscador y Registros", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            txt_buscar,
            ft.Container(
                content=ft.Column([tabla_alumnos], scroll=ft.ScrollMode.ALWAYS),
                height=450, border_radius=5, bgcolor=ft.Colors.BLACK26
            )
        ], expand=True)

        vista_final = ft.Column([
            ft.Row([
                ft.Text("Panel de Gestión CRUD - Alumnos 4D", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon="logout", on_click=lambda e: cargar_vista_login(), icon_color=ft.Colors.RED)
            ]),
            ft.Divider(color=ft.Colors.BLUE),
            ft.Row([panel_formulario, panel_consulta], expand=True)
        ], expand=True)

        page.add(vista_final)

    cargar_vista_login()

ft.run(main)