import tkinter as tk
import math
import json
import os

class Materia:
    def __init__(self, nombre, nivel, prereqs=None, angulo=None):
        if prereqs is None:
            prereqs = []
        self.nombre = nombre
        self.nivel = nivel
        self.prereqs = prereqs
        self.estado = "bloqueada"
        self.angulo = angulo
        self.pos = None
        self.circle = None
        self.text = None


class MapaCarrera:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa de Materias - Carrera")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.materias = {}
        self.num_niveles = 7
        self.margin = 10
        self.center = (0, 0)

        self.crear_materias()

        self.root.bind("<Configure>", self.redibujar) 
        self.canvas.bind("<Button-1>", self.click_materia)
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        archivo_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Guardar", command=self.guardar_estado)
        archivo_menu.add_command(label="Cargar", command=self.cargar_estado)
        self.cargar_estado()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_programa)

    def cerrar_programa(self):
        self.guardar_estado()
        self.root.destroy()

    def crear_materias(self):
        # Nivel 1
        self.materias["Informática"] = Materia("Informática", 1, [], 0 )
        self.materias["Álgebra Lineal"] = Materia("Álgebra Lineal", 1, [], 72)
        self.materias["Cálculo 1"] = Materia("Cálculo 1", 1, [], 144)
        self.materias['Química'] = Materia('Química',1,[], 216)
        self.materias['Intro a Ing'] = Materia('Intro a Ing', 1,[],288)

        # Nivel 2
        self.materias['Mate Discreta'] = Materia('Mate Discreta', 2,['Álgebra Lineal'],72)
        self.materias["Sis. Representación"] = Materia("Sis. Representación", 2, ["Informática"], 0)
        self.materias["Física 1"] = Materia("Física 1", 2, ['Cálculo 1'], 175)
        self.materias["Cálculo 2"] = Materia("Cálculo 2", 2, ["Álgebra Lineal", 'Cálculo 1'], 108)
        
        # Nivel 3
        self.materias["Programación"] = Materia("Programación", 3, ["Mate Discreta", 'Álgebra Lineal', 'Informática'], 36)
        self.materias['EDOs'] = Materia('EDOs', 3, ['Cálculo 2'],108)
        self.materias['P y E'] = Materia('P y E', 3, ['Cálculo 2'],90)
        self.materias['Física 2'] = Materia('Física 2', 3, ['Cálculo 2', 'Física 1'],126)
        self.materias['Materiales'] = Materia('Materiales', 3, ['Física 1', 'Cálculo 2', 'Química'],180)
        self.materias['Economía'] = Materia('Economía', 3, ['Intro a Ing', 'Cálculo 2'],216)
        self.materias['Modelos y PL'] = Materia('Modelos y PL', 3, ['Mate Discreta', 'Cálculo 2', 'Programación'],72)
        self.materias['Procesos de manufactura'] = Materia('Procesos de Manufactura', 3, ['Sis. Representación', 'Materiales'],252)

        
        #Nivel 4
        self.materias['Termodinámica'] = Materia('termodinámica', 4, ['EDOs', 'Física 2','Química'], 135)
        self.materias['Costos y presupuestos'] = Materia('Costos y presupuestos', 4, ['Economía', 'P y E'], 180)
        self.materias['Electrotecnia'] = Materia('Electrotecnia', 4, ['Física 2'], 117)
        self.materias['Administración O.'] = Materia('Administración O.', 4, ['Procesos de manufactura','Modelos y PL', 'Economía'], 330)
        self.materias['Sistemas complejos'] = Materia('Sistemas complejos', 4, ['EDOs','P y E'], 99)
        self.materias['Trabajo, Ética y Legislación'] = Materia('Trabajo, Ética y Legislación', 4, ['Procesos de manufactura'],252)
    

        #Nivel 5
        self.materias['Operaciones industriales'] = Materia('Operaciones industriales', 5, ['Termodinámica','Materiales'], 157.5)
        self.materias['Higiene y seguridad'] = Materia('Higiene y seguridad', 5, ['Termodinámica'], 135)
        self.materias['Cadena de suministros'] = Materia('Cadena de suministros', 5, ['Administración O.'], 330)
        self.materias['Modelado y simulación'] = Materia('Modelado y simulación', 5, ['Administración O.', 'Programación', 'P y E'], 36)
        self.materias['Control avanzado'] = Materia('Control avanzado', 5, ['Sistemas complejos'], 99)
        
        #Nivel 6 
        self.materias['Sist. Inf. Manufactura'] = Materia('Sist. Inf. Manufactura', 6, ['Cadena de suministros'], 330)
        self.materias['Diseño'] = Materia('Diseño', 6, ['Cadena de suministros', 'Electrotecnia', 'Operaciones industriales'], 90)
        self.materias['TD bajo incertidumbre'] = Materia('TD bajo incertidumbre', 6, ['Modelado y simulación', 'Control avanzado'], 65)
        self.materias['Calidad'] = Materia('Calidad', 6, ['Higiene y seguridad', 'Trabajo, Ética y Legislación'], 170)


        #Nivel 7
        self.materias['Man. inteligente'] = Materia('Man. Inteligente', 7, ['Sist. Inf. Manufactura', 'Diseño', 'Sistemas complejos'], 50)
        self.materias['Proy. inversión'] = Materia('Proy. inversión', 7, ['Trabajo, Ética y Legislación', 'Diseño', 'Costos y presupuestos'], 200)
        self.materias['Proy. Final'] = Materia('Proy. Final', 7, ['Sist. Inf. Manufactura', 'Diseño'], 30)

    def redibujar(self, event=None):
        """ Redibuja todo proporcionalmente al tamaño del Canvas """
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.center = (w / 2, h / 2)

        # Calcular radios según tamaño disponible
        max_radio = min(w, h) / 2 - self.margin
        paso = max_radio / self.num_niveles
        self.radio_niveles = {i: paso * i for i in range(1, self.num_niveles + 1)}

        for i in range(1, self.num_niveles + 1):
            r = self.radio_niveles[i]
            self.canvas.create_oval(
                self.center[0] - r, self.center[1] - r,
                self.center[0] + r, self.center[1] + r,
                outline="#a1a1a1", width=1, dash=(3, 5)
            )
        

        # Calcular posiciones
        for m in self.materias.values():
            r = self.radio_niveles[m.nivel]
            ang_rad = math.radians(m.angulo)
            x = self.center[0] + r * math.cos(ang_rad)
            y = self.center[1] - r * math.sin(ang_rad)
            m.pos = (x, y)

        # Dibujar aristas (líneas de correlatividad)
        for m in self.materias.values():
            for p in m.prereqs:
                if p in self.materias:
                    x1, y1 = self.materias[p].pos
                    x2, y2 = m.pos
                    self.canvas.create_line(x1, y1, x2, y2, fill="#cccccc", width=1.2)

        # Dibujar materias
        self.dibujar_materias()
        self.actualizar_estados()

    def dibujar_materias(self):
        for m in self.materias.values():
            x, y = m.pos
            r = 30
            color = {
                "bloqueada": "#eeeeee",
                "disponible": "#a1a1a1",
                "aprobada": "#ff5b5b"
            }[m.estado]
            m.circle = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="", width=0  
            )
            m.text = self.canvas.create_text(
                x, y, text=m.nombre, width=72, justify="center", font=("Arial", 9)
            )

    def actualizar_estados(self):
        for m in self.materias.values():
            if m.estado == "aprobada":
                continue
            if all(self.materias[p].estado == "aprobada" for p in m.prereqs):
                m.estado = "disponible"
            else:
                m.estado = "bloqueada"

        # Actualizar color visual
        for m in self.materias.values():
            color = {
                "bloqueada": "#eeeeee",
                "disponible": "#a1a1a1",
                "aprobada": "#ff5b5b"
            }[m.estado]
            self.canvas.itemconfig(m.circle, fill=color)

    def click_materia(self, event):
        for m in self.materias.values():
            x, y = m.pos
            r = 30
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= r ** 2:
                if m.estado == "disponible":
                    m.estado = "aprobada"
                    self.actualizar_estados()
                break

    def guardar_estado(self, archivo="estado_materias_industrial.json"):
        estado = {nombre: m.estado for nombre, m in self.materias.items()}
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=4)
        print("✅ Estado guardado en", archivo)

    def cargar_estado(self, archivo="estado_materias_industrial.json"):
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                estado = json.load(f)
            for nombre, st in estado.items():
                if nombre in self.materias:
                    self.materias[nombre].estado = st
            print("📂 Estado cargado desde", archivo)
        else:
            print("ℹ️ No se encontró archivo de estado.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x1200")
    app = MapaCarrera(root)
    root.mainloop()