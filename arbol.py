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
        self.root.title("Mapa de materias LMA-26")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.materias = {}
        self.num_niveles = 6  
        self.margin = 10
        self.center = (0, 0)

        self.crear_materias()

        self.root.bind("<Configure>", self.redibujar) 
        self.canvas.bind("<Button-1>", self.click_materia)
        self.canvas.bind('<Button-3>', self.click_materia_borrar)
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        archivo_menu = tk.Menu(menu, tearoff=0)
        menu.add_command(label='Como usar este árbol', comman = self.instrucciones)
        menu.add_command(label="Limpiar", command=self.limpiar)
        self.cargar_estado()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_programa)

    def cerrar_programa(self):
        self.guardar_estado()
        self.root.destroy()

    def crear_materias(self):
        # Nivel 1
        self.materias["Matemática Básica"] = Materia("Matemática Básica", 1, [], 180)
        self.materias["Álgebra"] = Materia("Álgebra", 1, [], 310)
        self.materias["Ciencia de Datos 1"] = Materia("Ciencia de Datos 1", 1, [], 60)

        # Nivel 2
        self.materias["Cálculo 1"] = Materia("Cálculo 1", 2, ["Matemática Básica"], 160)
        self.materias["Álgebra Lineal"] = Materia("Álgebra Lineal", 2, ["Matemática Básica"], 210)
        self.materias["Ciencia de Datos 2"] = Materia("Ciencia de Datos 2", 2, ["Ciencia de Datos 1"], 60)
        self.materias["Matemática Discreta"] = Materia("Matemática Discreta", 2, ["Álgebra"], 340)

        # Nivel 3
        self.materias["Ciencia de Datos 3"] = Materia("Ciencia de Datos 3", 3, ["Ciencia de Datos 2"], 60)
        self.materias['Cálculo 2'] = Materia('Cálculo 2', 3, ['Álgebra Lineal', 'Cálculo 1'],170)
        self.materias['Análisis Matricial'] = Materia('Análisis Matricial', 3, ['Álgebra Lineal'],95)
        self.materias['Física'] = Materia('Física', 3, ['Álgebra', 'Álgebra Lineal', 'Cálculo 1'],220)
        self.materias['Modelos y PL'] = Materia('Modelos y PL', 3, ['Álgebra Lineal', 'Cálculo 1', 'Ciencia de Datos 2', 'Matemática Discreta'],0)
        self.materias['Estructuras Algebraicas'] = Materia('Estructuras Algebraicas', 3, ['Matemática Discreta', 'Álgebra Lineal'],255)

        #Nivel 4
        self.materias['Probabilidad'] = Materia('Probabilidad', 4, ['Matemática Discreta', 'Cálculo 2','Ciencia de Datos 3'], 145)
        self.materias['Estructuras Topológicas'] = Materia('Estructuras Topológicas', 4, ['Álgebra Lineal', 'Cálculo 2'], 200)
        self.materias['EDOs'] = Materia('EDOs', 4, ['Álgebra Lineal', 'Cálculo 2', 'Física'], 180)
        self.materias['Metodos Numéricos 1'] = Materia('Metodos Numéricos 1', 4, ['Ciencia de Datos 2', 'Cálculo 2'], 90)
        self.materias['Optimización y TD'] = Materia('Optimización y TD', 4, ['Modelos y PL'],0)

        #Nivel 5
        self.materias['EDPs'] = Materia('EDPs', 5, ['EDOs'], 170)
        self.materias['Análisis Complejo'] = Materia('Análisis Complejo', 5, ['Estructuras Topológicas'],210)
        self.materias['Medida e integración'] = Materia('Medida e integración', 5, ['Estructuras Topológicas'], 190)
        self.materias['Estadística'] = Materia('Estadiística', 5, ['Análisis Matricial', 'Probabilidad'], 115)
        self.materias['Metodos Numéricos 2'] = Materia ('Metodos Numéricos 2', 5, ['Cálculo 2', 'Ciencia de Datos 3', 'Metodos Numéricos 1'],90)

        #Nivel 6 
        self.materias['Análisis Funcional'] = Materia('Análisis Funcional', 6, ['Medida e integración'],200)

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

    def instrucciones(self):
        ventana = tk.Toplevel(root)
        ventana.title("Instrucciones")
        ventana.geometry("400x300+600+200")

        frame = tk.Frame(ventana)
        frame.pack(expand=True, fill="both")

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            width=50,
            height=20
        )
        text.pack(expand=True, fill="both")

        scrollbar.config(command=text.yview)

        text.insert("1.0", "COMO INTERPRETAR ESTE ÁRBOL ?\n\n En la ventana principal se alza, ante sus ojos atentos, un árbol de saberes: " \
        " allí reposan los nombres de todas las materias de la LMA – Plan 2026, cada una como un destino escrito, cada una aguardando su hora. " \
        " Estas materias no flotan al azar: habitan seis anillos grises concéntricos, trazados con líneas discretas, como estaciones de un viaje " \
        " que no admite atajos. Debéis comprender su ley secreta: Si una materia mora en cierto anillo, es porque antes debéis haber vencido " \
        " una prueba del anillo inmediatamente anterior. Así, por ejemplo ¡oh, Métodos Numéricos I! no se os concederá sin antes haber " \
        " rendido homenaje a Ciencia de Datos II y a Cálculo II. Y puesto que Cálculo II habita el tercer anillo, Métodos Numéricos I, " \
        " fiel a la jerarquía del destino, se sitúa en el cuarto. Las correlatividades se revelan mediante líneas grises, delgadas como " \
        " hilos del destino, que unen unas materias con otras. Leed siempre estas líneas hacia afuera, como quien lee el porvenir: " \
        " Si una línea une a A con B, y A pertenece a un anillo más cercano al centro, entonces A es la llave sin la cual B jamás abrirá " \
        " sus puertas. \n\n CÓDIGO DE COLORES: \n\n * Gris claro :  Materia aún lejana, casi indiferente. No poseéis las correlativas necesarias. " \
        " Podéis hacer clic… pero el árbol, impasible, no responderá. El destino aún no os reconoce. \n\n * Gris oscuro : ¡Aquí hay esperanza! " \
        " Dadas las materias que ya habéis marcado como hechas, esta materia puede ser cursada. Con un clic izquierdo, la declararéis " \
        " vencida y se teñirá del color de la sangre académica: rojo. \n\n * Rojo Victoria :  La materia ha sido cursada, domada, superada. " \
        " Pero recordad: incluso las conquistas pueden deshacerse. Con clic derecho podéis desmarcarla, y el árbol entero como una " \
        " ciudad que despierta reorganizará sus colores y destinos al instante. \n\n Pero incluso en las epopeyas más largas, llega " \
        " el momento del olvido misericordioso. En lo alto del menú descansa el botón Limpiar, discreto, severo y absoluto, " \
        " como una noche que borra las huellas del día. Al pulsarlo, todas las materias regresarán a su estado original:  los " \
        " rojos se apagarán, los grises recuperarán su silencio inicial, y el árbol quedará desnudo otra vez, como en el primer " \
        " amanecer del plan de estudios, cuando aún todo era posible y ninguna correlativa había sido traicionada. \n\n\n\n Diego. \n\n " )

        text.config(state="disabled")

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

    def click_materia_borrar(self, event):
        for m in self.materias.values():
            x, y = m.pos
            r = 30
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= r ** 2:
                if m.estado == "aprobada":
                    m.estado = "disponible"
                    self.actualizar_estados()
                break

    def limpiar(self):
        for m in self.materias.values():
            if m.estado == 'aprobada':
                m.estado = "disponible"
            self.actualizar_estados()
            

    def guardar_estado(self, archivo="estado_materias.json"):
        estado = {nombre: m.estado for nombre, m in self.materias.items()}
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=4)
        print("✅ Estado guardado en", archivo)

    def cargar_estado(self, archivo="estado_materias.json"):
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                estado = json.load(f)
            for nombre, st in estado.items():
                if nombre in self.materias:
                    self.materias[nombre].estado = st
            print("📂 Estado cargado desde", archivo)
        else:
            print("ℹ️ No se encontró archivo de estado.")


from pathlib import Path
import sys

root = tk.Tk()
root.geometry("1400x1200")
app = MapaCarrera(root)
    
def resource_path(relative_path):
    """ Funciona tanto en desarrollo como en el .exe """
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = Path(__file__).parent
    return Path(base_path) / relative_path

icon_path = resource_path("arbol-verde.ico")
root.iconbitmap(icon_path)
root.mainloop()



   
