import tkinter as tk
from tkinter import messagebox, ttk
import random
import re
from datetime import datetime
from typing import List

class EstadoMaquinaTuring:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.transiciones = []
    
    def agregar_transicion(self, simbolo_actual: str, nuevo_simbolo: str, direccion: str, siguiente_estado: str):
        movimiento = 1 if direccion == 'R' else -1
        self.transiciones.append((simbolo_actual, nuevo_simbolo, direccion, movimiento, siguiente_estado))

class MaquinaDeTuring:
    # Código de la clase permanece igual...
    def __init__(self):
        self.estado_actual = 'q0'
        self.cinta = []
        self.posicion = 0
        self.estados = self.inicializar_estados()

    def inicializar_estados(self):
        estados = {}
        estados['q0'] = EstadoMaquinaTuring('q0')
        estados['q0'].agregar_transicion('[A-Z]', '*', 'R', 'q1')
        estados['q1'] = EstadoMaquinaTuring('q1')
        estados['q1'].agregar_transicion('[AEIOU]', '*', 'R', 'qAceptar')
        return estados

    def validar_curp(self, curp: str) -> bool:
        if not curp or len(curp) != 18:
            return False
        patron = r'^[A-Z]{4}\d{6}[HM][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]\d$'
        if not re.match(patron, curp):
            return False
        try:
            fecha = datetime.strptime(curp[4:10], '%y%m%d')
            if fecha > datetime.now():
                return False
        except ValueError:
            return False
        entidades = {'AS','BC','BS','CC','CL','CM','CS','CH','DF','DG','GT','GR','HG','JC','MC','MN','MS','NT','NL','OC','PL','QT','QR','SP','SL','SR','TC','TS','TL','VZ','YN','ZS'}
        if curp[11:13] not in entidades:
            return False
        return True



class InterfazCURP(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador y Validador de CURP")
        self.configure(bg='#1E1E2E')
        self.geometry("1800x900")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.maquina = MaquinaDeTuring()
        self.setup_ui()

    def configure_styles(self):
        self.style.configure('TFrame', background='#1E1E2E') # 1E1E2E
        self.style.configure('TLabel', background='#1E1E2E', font=('Arial', 12), foreground="#FFFFFF")
        self.style.configure('TEntry', font=('Arial', 12), background="#1E1E2E", foreground="#D8DEE9", insertcolor="white", relief="flat")
        self.style.map('TEntry', fieldbackground=[('focus', '#1E1E2E')], bordercolor=[('focus', '#000000')])
        self.style.configure('TButton', padding=10, font=("Arial", 12), background="#8FBCBB", foreground="#2E3440")
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), foreground="#88C0D0")

    def setup_ui(self):
        self.main_frame = ttk.Frame(self, padding="30")
        self.main_frame.pack(fill='both', expand=True)
        
        header = ttk.Label(self.main_frame, text="Generación de la CURP", style='Header.TLabel')
        header.pack(pady=20)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, pady=20)

        self.tab_generacion = self.crear_tab_generacion()
        self.tab_validacion = self.crear_tab_validacion()
        
        self.notebook.add(self.tab_generacion, text='Generar CURP')
        self.notebook.add(self.tab_validacion, text='Validar CURP')

    def crear_tab_generacion(self):
        frame = ttk.Frame(self.notebook, padding="20")

        self.vars_entrada = {}
        campos = [("Nombre(s)", True), ("Apellido Paterno", True), ("Apellido Materno", False), 
                ("Fecha de Nacimiento (YYYYMMDD)", True)]

        # Cambiar la disposición de las etiquetas y entradas a dos columnas
        for i, (campo, required) in enumerate(campos):
            label_text = f"{campo}{'*' if required else ''}"
            ttk.Label(frame, text=label_text).grid(row=i//2, column=(i % 2) * 2, sticky='w', pady=11, padx=10)
            var = tk.StringVar()
            self.vars_entrada[campo] = var
            entry = ttk.Entry(frame, textvariable=var, width=25)
            entry.grid(row=i//2, column=(i % 2) * 2 + 1, sticky='ew', padx=10, pady=5)

        # Sexo
        ttk.Label(frame, text="Sexo*").grid(row=len(campos)//2, column=0, sticky='w', pady=20, padx=10)
        self.var_sexo = tk.StringVar(value="H")
        sexo_frame = ttk.Frame(frame)
        sexo_frame.grid(row=len(campos)//2, column=1, sticky='w', padx=10)
        ttk.Radiobutton(sexo_frame, text="Hombre", variable=self.var_sexo, value="H").pack(side="left")
        ttk.Radiobutton(sexo_frame, text="Mujer", variable=self.var_sexo, value="M").pack(side="left")

        # Estado
        ttk.Label(frame, text="Estado*").grid(row=len(campos)//2 + 1, column=0, sticky='w', pady=5, padx=10)
        self.var_estado = tk.StringVar()
        self.combo_estados = ttk.Combobox(frame, textvariable=self.var_estado, width=23)
        self.combo_estados['values'] = self.obtener_estados_mexico()
        self.combo_estados.grid(row=len(campos)//2 + 1, column=1, sticky='ew', padx=10, pady=5)

        # Botón y resultado
        ttk.Button(frame, text="Generar CURP", command=self.generar_curp).grid(row=len(campos)//2 + 2, column=0, columnspan=2, pady=20)

        self.var_resultado = tk.StringVar()
        ttk.Label(frame, textvariable=self.var_resultado, style='Header.TLabel').grid(row=len(campos)//2 + 3, column=0, columnspan=2, pady=10)

        # Ajuste de las columnas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        return frame

    def crear_tab_validacion(self):
        frame = ttk.Frame(self.notebook, padding="20")
        ttk.Label(frame, text="Ingrese CURP a validar:", font=('Helvetica', 12, 'bold')).pack(pady=10)
        self.var_curp_validar = tk.StringVar()
        ttk.Entry(frame, textvariable=self.var_curp_validar, font=('Arial', 12), width=30).pack(fill='x', padx=20, pady=10)
        ttk.Button(frame, text="Validar CURP", command=self.validar_curp).pack(pady=20)
        self.var_validacion = tk.StringVar()
        ttk.Label(frame, textvariable=self.var_validacion, style='Header.TLabel').pack(pady=10)
        return frame

    def obtener_estados_mexico(self) -> List[str]:
        return ['AS - Aguascalientes', 'BC - Baja California', 'BS - Baja California Sur', 'CC - Campeche', 
                'CL - Coahuila', 'CM - Colima', 'CS - Chiapas', 'CH - Chihuahua', 'DF - Ciudad de México', 
                'DG - Durango', 'GT - Guanajuato', 'GR - Guerrero', 'HG - Hidalgo', 'JC - Jalisco', 
                'MC - Estado de México', 'MN - Michoacán', 'MS - Morelos', 'NT - Nayarit', 'NL - Nuevo León', 
                'OC - Oaxaca', 'PL - Puebla', 'QT - Querétaro', 'QR - Quintana Roo', 'SP - San Luis Potosí', 
                'SL - Sinaloa', 'SR - Sonora', 'TC - Tabasco', 'TS - Tamaulipas', 'TL - Tlaxcala', 
                'VZ - Veracruz', 'YN - Yucatán', 'ZS - Zacatecas']

    def es_bisiesto(self, anio: int) -> bool:
        # Método auxiliar para verificar si un año es bisiesto.
        return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

    def primera_vocal_interna(self, texto: str) -> str:
        # Método auxiliar para encontrar la primera vocal interna en un texto.
        if len(texto) < 2:
            return "X"
        for c in texto[1:]:
            if c in "AEIOU":
                return c
        return "X"

    def primera_consonante_interna(self, texto: str) -> str:
        # Método auxiliar para encontrar la primera consonante interna en un texto.
        if len(texto) < 2:
            return "X"
        consonantes = "BCDFGHJKLMNPQRSTVWXYZ"
        for c in texto[1:]:
            if c in consonantes:
                return c
        return "X"

    def generar_curp(self):
        # Método para generar la CURP basado en los campos de entrada.
        try:
            nombre = self.vars_entrada["Nombre(s)"].get().strip().upper()
            ap_paterno = self.vars_entrada["Apellido Paterno"].get().strip().upper()
            ap_materno = self.vars_entrada["Apellido Materno"].get().strip().upper() or "X"
            fecha = self.vars_entrada["Fecha de Nacimiento (YYYYMMDD)"].get().strip()
            sexo = self.var_sexo.get()
            estado = self.var_estado.get()[:2]

            if not all([nombre, ap_paterno, fecha, sexo, estado]):
                raise ValueError("Todos los campos obligatorios deben estar llenos")

            if not re.match(r'^\d{8}$', fecha):
                raise ValueError("La fecha debe tener formato YYYYMMDD")

            anio = int(fecha[:4])
            mes = int(fecha[4:6])
            dia = int(fecha[6:])
            
            dias_por_mes = [31, 29 if self.es_bisiesto(anio) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if not (1 <= mes <= 12) or not (1 <= dia <= dias_por_mes[mes - 1]):
                raise ValueError("Fecha de nacimiento no válida")

            nombres = nombre.split()
            primer_nombre = nombres[1] if len(nombres) > 1 and nombres[0] in {"MARIA", "JOSE"} else nombres[0]
            
            curp = (
                ap_paterno[0] +
                self.primera_vocal_interna(ap_paterno) +
                (ap_materno[0] if ap_materno != "X" else "X") +
                primer_nombre[0] +
                fecha[2:] +
                sexo +
                estado +
                self.primera_consonante_interna(ap_paterno) +
                self.primera_consonante_interna(ap_materno) +
                self.primera_consonante_interna(primer_nombre)
            )

            curp += str(random.randint(0, 99)).zfill(2)
            self.var_resultado.set(f"CURP generada: {curp}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validar_curp(self):
        # Método para validar el formato de la CURP.
        curp = self.var_curp_validar.get().strip().upper()
        if re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$', curp):
            self.var_validacion.set("CURP válida")
        else:
            self.var_validacion.set("CURP inválida")

if __name__ == "__main__":

    app = InterfazCURP()
    app.mainloop()

