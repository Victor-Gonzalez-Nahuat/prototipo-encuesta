import flet as ft
import pymysql
import base64
import requests
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = 51558
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )



def obtener_gps():
    try:
        r = requests.get("https://ipapi.co/json/")
        data = r.json()
        return str(data.get("latitude", "")), str(data.get("longitude", ""))
    except:
        return "", ""


class EncuestaApp:
    def __init__(self, page: ft.Page):
        self.page = page

        self.page.title = "Encuesta Telchac Puerto"
        self.page.scroll = "auto"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE_700,
        )

        self.secciones = [
            self.datos_generales,
            self.basura,
            self.agua,
            self.predio_construccion
        ]

        self.content_column = ft.Column(
            controls=[],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.page.add(
            ft.AppBar(
                title=ft.Text("Encuesta de Propiedades - Telchac", weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            ),
            ft.Container(
                content=self.content_column,
                padding=20,
                alignment=ft.alignment.center
            )
        )

        self.iniciar_nueva_encuesta()

    def iniciar_nueva_encuesta(self, e=None):

        if hasattr(self, 'mensaje_exito') and self.mensaje_exito in self.page.controls:
            self.page.remove(self.mensaje_exito)

        self.folio = f"TP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.lat, self.lon = obtener_gps()
        self.foto_base64 = None
        self.data = {}
        self.seccion = 0

        self.content_column.visible = True
        self.content_column.controls.clear()

        self.mostrar_seccion()
        self.page.update()

    def mostrar_seccion(self):
        self.content_column.controls.clear()
        titulo_secciones = [
            "Datos Generales",
            "Servicio de Recolección de Basura",
            "Servicio de Suministro de Agua",
            "Detalles del Predio y Construcción"
        ]

        self.content_column.controls.append(
            ft.Text(
                titulo_secciones[self.seccion],
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700
            )
        )

        self.secciones[self.seccion]()

        botones_nav = []
        if self.seccion > 0:
            botones_nav.append(ft.ElevatedButton("Anterior", on_click=self.anterior_seccion, icon=ft.Icons.ARROW_BACK))

        if self.seccion < len(self.secciones) - 1:
            botones_nav.append(
                ft.ElevatedButton("Siguiente", on_click=self.siguiente_seccion, icon=ft.Icons.ARROW_FORWARD))
        else:
            botones_nav.append(
                ft.ElevatedButton(
                    "💾 Guardar Encuesta",
                    on_click=self.guardar_encuesta,
                    icon=ft.Icons.SAVE,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE
                )
            )

        self.content_column.controls.append(
            ft.Row(
                controls=botones_nav,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        )
        self.page.update()

    def siguiente_seccion(self, e):
        self.seccion += 1
        self.mostrar_seccion()

    def anterior_seccion(self, e):
        if self.seccion > 0:
            self.seccion -= 1
            self.mostrar_seccion()


    def _crear_tarjeta_seccion(self, titulo, icon, campos):
        return ft.Card(
            elevation=10,
            content=ft.Container(
                padding=20,
                width=600,
                content=ft.Column(
                    controls=[
                        ft.Row([
                            ft.Icon(icon, color=ft.Colors.BLUE_GREY_700),
                            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(),
                        *campos
                    ],
                    spacing=15
                )
            )
        )


    def datos_generales(self):
        self.tx_nombre = ft.TextField(label="Nombre", icon=ft.Icons.PERSON, value=self.data.get("nombre", None))
        self.tx_direccion = ft.TextField(label="Dirección", icon=ft.Icons.HOME_WORK,
                                         value=self.data.get("direccion", None))
        self.tx_colonia = ft.TextField(label="Colonia", icon=ft.Icons.LOCATION_CITY,
                                       value=self.data.get("colonia", None))
        self.tx_telefono = ft.TextField(label="Teléfono", icon=ft.Icons.PHONE, value=self.data.get("telefono", None))

        campos = [
            ft.Text(f"Folio de Encuesta: {self.folio}",
                    style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_400)),
            self.tx_nombre,
            self.tx_direccion,
            self.tx_colonia,
            self.tx_telefono,
        ]

        self.content_column.controls.append(
            self._crear_tarjeta_seccion("Información del Residente", ft.Icons.PERSON_PIN, campos)
        )


    def basura(self):
        self.cmb_basura = ft.Dropdown(label="Problema basura", options=[
            ft.dropdown.Option("Bien"), ft.dropdown.Option("Mal"),
            ft.dropdown.Option("Muy mal"), ft.dropdown.Option("No pasa el camión")
        ], width=280)
        self.cmb_frec = ft.Dropdown(label="Frecuencia recolección", options=[
            ft.dropdown.Option("Diario"), ft.dropdown.Option("Cada 2 días"),
            ft.dropdown.Option("Semanal"), ft.dropdown.Option("Nunca")
        ], width=280)
        self.cmb_cont_basura = ft.Dropdown(label="Contrato basura", options=[
            ft.dropdown.Option("Sí"), ft.dropdown.Option("No")
        ], width=280)
        self.tx_num_cont_basura = ft.TextField(label="Número contrato basura", width=280,
                                               keyboard_type=ft.KeyboardType.NUMBER)

        campos = [
            ft.Row([ft.Column([self.cmb_basura, self.cmb_frec, self.cmb_cont_basura, self.tx_num_cont_basura])], alignment=ft.MainAxisAlignment.CENTER),
        ]

        self.content_column.controls.append(
            self._crear_tarjeta_seccion("Servicio de Recolección de Basura", ft.Icons.DELETE, campos)
        )

    def agua(self):
        self.cmb_agua = ft.Dropdown(label="Problema agua", options=[
            ft.dropdown.Option("Bien"), ft.dropdown.Option("Mal"),
            ft.dropdown.Option("A veces"), ft.dropdown.Option("No tiene servicio")
        ], width=280)
        self.cmb_servicio_agua = ft.Dropdown(label="Servicio agua", options=[
            ft.dropdown.Option("Red municipal"), ft.dropdown.Option("Pipas"),
            ft.dropdown.Option("Pozo"), ft.dropdown.Option("Otro")
        ], width=280)
        self.cmb_cont_agua = ft.Dropdown(label="Contrato agua", options=[
            ft.dropdown.Option("Sí"), ft.dropdown.Option("No")
        ], width=280)
        self.tx_num_cont_agua = ft.TextField(label="Número contrato agua", width=280,
                                             keyboard_type=ft.KeyboardType.NUMBER)

        campos = [
            ft.Row([ft.Column([self.cmb_agua, self.cmb_servicio_agua, self.cmb_cont_agua, self.tx_num_cont_agua])], alignment=ft.MainAxisAlignment.CENTER),
        ]

        self.content_column.controls.append(
            self._crear_tarjeta_seccion("Servicio de Suministro de Agua", ft.Icons.WATER_DROP, campos)
        )


    def predio_construccion(self):
        self.cmb_tiene_const = ft.Dropdown(label="¿Tiene construcción?", options=[
            ft.dropdown.Option("Sí"), ft.dropdown.Option("No")
        ], width=280)
        self.cmb_tipo_const = ft.Dropdown(label="Tipo de construcción", options=[
            ft.dropdown.Option("Casa"), ft.dropdown.Option("Cuarto"),
            ft.dropdown.Option("Ampliación"), ft.dropdown.Option("Negocio"), ft.dropdown.Option("Otro")
        ], width=280)
        self.cmb_niveles = ft.Dropdown(label="Niveles", options=[
            ft.dropdown.Option("1"), ft.dropdown.Option("2"), ft.dropdown.Option("3"), ft.dropdown.Option("Más de 3")
        ], width=280)
        self.cmb_material = ft.Dropdown(label="Material", options=[
            ft.dropdown.Option("Block"), ft.dropdown.Option("Madera"), ft.dropdown.Option("Lámina"),
            ft.dropdown.Option("Mixto")
        ], width=280)
        self.cmb_estado = ft.Dropdown(label="Estado construcción", options=[
            ft.dropdown.Option("Bueno"), ft.dropdown.Option("Regular"), ft.dropdown.Option("Malo")
        ], width=280)
        self.cmb_uso = ft.Dropdown(label="Uso del predio", options=[
            ft.dropdown.Option("Habitacional"), ft.dropdown.Option("Comercial"), ft.dropdown.Option("Mixto"),
            ft.dropdown.Option("Servicio"), ft.dropdown.Option("Bodega"), ft.dropdown.Option("Taller"),
            ft.dropdown.Option("Abandonado"), ft.dropdown.Option("Baldío")
        ], width=280)
        self.tx_obs_const = ft.TextField(label="Observaciones (detalles relevantes)", multiline=True, min_lines=3,
                                         max_lines=5, width=280)

        campos = [
            ft.Row([ft.Column([
                self.cmb_tiene_const, self.cmb_tipo_const, self.cmb_niveles,
                self.cmb_material, self.cmb_estado,
                self.cmb_uso,
                self.tx_obs_const,


            ])]),

        ]

        self.content_column.controls.append(
            self._crear_tarjeta_seccion("Predio y Características de la Construcción", ft.Icons.HOUSE, campos)
        )

    def guardar_encuesta(self, e):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            nombre = self.tx_nombre.value
            direccion = self.tx_direccion.value
            colonia = self.tx_colonia.value
            telefono = self.tx_telefono.value
            agua = self.cmb_agua.value if hasattr(self, "cmb_agua") else None
            basura = self.cmb_basura.value if hasattr(self, "cmb_basura") else None
            frec = self.cmb_frec.value if hasattr(self, "cmb_frec") else None
            serv_agua = self.cmb_servicio_agua.value if hasattr(self, "cmb_servicio_agua") else None
            tiene_const = self.cmb_tiene_const.value if hasattr(self, "cmb_tiene_const") else None
            tipo_const = self.cmb_tipo_const.value if hasattr(self, "cmb_tipo_const") else None
            niveles = self.cmb_niveles.value if hasattr(self, "cmb_niveles") else None
            material = self.cmb_material.value if hasattr(self, "cmb_material") else None
            estado = self.cmb_estado.value if hasattr(self, "cmb_estado") else None
            obs = self.tx_obs_const.value if hasattr(self, "tx_obs_const") else None
            uso = self.cmb_uso.value if hasattr(self, "cmb_uso") else None
            cont_agua = self.cmb_cont_agua.value if hasattr(self, "cmb_cont_agua") else None
            num_cont_agua = self.tx_num_cont_agua.value if hasattr(self, "tx_num_cont_agua") else None
            cont_basura = self.cmb_cont_basura.value if hasattr(self, "cmb_cont_basura") else None
            num_cont_basura = self.tx_num_cont_basura.value if hasattr(self, "tx_num_cont_basura") else None
            foto_blob = base64.b64decode(self.foto_base64) if self.foto_base64 else None

            sql = """
                INSERT INTO ENCUESTAS_TELCHAC (
                    folio, fecha, nombre, direccion, colonia, telefono, problema_agua, problema_basura, 
                    frecuencia_recoleccion, servicio_agua, tiene_construccion, tipo_construccion, niveles, 
                    material_predominante, estado_construccion, observacion_construccion, uso_predio, 
                    tiene_contrato_agua, numero_contrato_agua, tiene_contrato_basura, numero_contrato_basura, 
                    latitud, longitud, foto, encuestador
                )
                VALUES (
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(sql, (
                self.folio,
                nombre, direccion, colonia, telefono, agua, basura, frec, serv_agua,
                tiene_const, tipo_const, niveles, material, estado, obs, uso,
                cont_agua, num_cont_agua, cont_basura, num_cont_basura,
                self.lat, self.lon, foto_blob, "ENCUESTADOR MUNICIPAL"
            ))

            conn.commit()
            conn.close()

            self.content_column.visible = False

            self.mensaje_exito = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=100),
                        ft.Text("✅ Encuesta Guardada con Éxito", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Folio: {self.folio}"),
                        ft.ElevatedButton("Comenzar Nueva Encuesta", on_click=self.iniciar_nueva_encuesta),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                expand=True,
                alignment=ft.alignment.center
            )

            self.page.add(self.mensaje_exito)
            self.page.update()

        except Exception as err:
            print(f"Error al guardar: {err}")
            snack = ft.SnackBar(
                ft.Text(f"❌ Error al guardar la encuesta: {err}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700
            )
            self.page.open(snack)
            self.page.update()

def main(page: ft.Page):
    EncuestaApp(page)


ft.app(target=main, view=ft.WEB_BROWSER)
