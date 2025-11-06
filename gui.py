import tkinter as tk
from tkinter import scrolledtext

class CompiladorGUI:
    def __init__(self, root, compilador):
        self.root = root
        self.compilador = compilador
        self.root.title("🌴 Compilador Costeñol")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f4f8')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f4f8')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # HEADER
        self.crear_header(main_frame)
        
        # PANELES
        panel_container = tk.Frame(main_frame, bg='#f0f4f8')
        panel_container.pack(fill=tk.BOTH, expand=True)
        
        self.crear_panel_editor(panel_container)
        self.crear_panel_consola(panel_container)
    
    def crear_header(self, parent):
        """Crea el encabezado con título y estadísticas"""
        header_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_label = tk.Label(header_frame, text="🌴 Compilador Costeñol", 
                               font=('Arial', 24, 'bold'), bg='white', fg='#2c3e50')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle_label = tk.Label(header_frame, text="¡Dale pues, escribe tu código y dale al botón!", 
                                 font=('Arial', 11), bg='white', fg='#7f8c8d')
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Estadísticas
        self.stats_frame = tk.Frame(header_frame, bg='white')
        self.stats_frame.pack(side=tk.RIGHT, padx=20)
        
        self.aciertos_label = tk.Label(self.stats_frame, text="0\nAciertos", 
                                       font=('Arial', 14, 'bold'), bg='#d4edda', fg='#155724',
                                       width=10, relief=tk.RAISED, bd=2)
        self.aciertos_label.pack(side=tk.LEFT, padx=5)
        
        self.errores_label = tk.Label(self.stats_frame, text="0\nErrores", 
                                      font=('Arial', 14, 'bold'), bg='#f8d7da', fg='#721c24',
                                      width=10, relief=tk.RAISED, bd=2)
        self.errores_label.pack(side=tk.LEFT, padx=5)
    
    def crear_panel_editor(self, parent):
        """Crea el panel del editor de código"""
        left_panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Header del editor
        editor_header = tk.Frame(left_panel, bg='#3498db')
        editor_header.pack(fill=tk.X)
        
        tk.Label(editor_header, text="📝 Editor de Código", font=('Arial', 14, 'bold'),
                bg='#3498db', fg='white').pack(side=tk.LEFT, padx=15, pady=10)
        
        # Botón analizar
        self.analizar_btn = tk.Button(editor_header, text="▶ Analizar", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#2ecc71', fg='white', 
                                      activebackground='#27ae60',
                                      relief=tk.RAISED, bd=3,
                                      cursor='hand2',
                                      command=self.analizar_codigo)
        self.analizar_btn.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # Área de código
        self.codigo_text = scrolledtext.ScrolledText(left_panel, 
                                                     font=('Consolas', 11),
                                                     bg='#2c3e50', fg='#ecf0f1',
                                                     insertbackground='white',
                                                     relief=tk.FLAT,
                                                     padx=10, pady=10)
        self.codigo_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Código de ejemplo
        #codigo_ejemplo = '''saludo Texto;
#saludo = Captura.Texto("Hola, Mundo!");
#saludo2 Texto;
#saludo2 = "Hola"
#edad Entero;
#edad = 25;'''
        #self.codigo_text.insert('1.0', codigo_ejemplo)
        
        # Ejemplos
        self.crear_ejemplos(left_panel)
    
    def crear_ejemplos(self, parent):
        """Crea el área de ejemplos"""
        ejemplos_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.SUNKEN, bd=1)
        ejemplos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(ejemplos_frame, text="💡 Ejemplos válidos:", 
                font=('Arial', 9, 'bold'), bg='#ecf0f1').pack(anchor=tk.W, padx=10, pady=5)
        
        ejemplo_text = tk.Text(ejemplos_frame, height=4, font=('Consolas', 9),
                              bg='#ecf0f1', relief=tk.FLAT)
        ejemplo_text.pack(fill=tk.X, padx=10, pady=(0, 5))
        ejemplo_text.insert('1.0', 'nombre Texto;\nnombre = "Carlos";\nedad Entero;\nedad = 25;')
        ejemplo_text.config(state=tk.DISABLED)
    
    def crear_panel_consola(self, parent):
        """Crea el panel de la consola de resultados"""
        right_panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Header consola
        console_header = tk.Frame(right_panel, bg='#e74c3c')
        console_header.pack(fill=tk.X)
        
        tk.Label(console_header, text="🖥️ Consola de Resultados", 
                font=('Arial', 14, 'bold'),
                bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=15, pady=10)
        
        # Área de consola
        console_frame = tk.Frame(right_panel, bg='#1e1e1e')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.consola_text = scrolledtext.ScrolledText(console_frame, 
                                                      font=('Consolas', 10),
                                                      bg='#1e1e1e', fg='#d4d4d4',
                                                      relief=tk.FLAT,
                                                      padx=10, pady=10,
                                                      state=tk.DISABLED)
        self.consola_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de colores
        self.consola_text.tag_config('exito', foreground='#4ade80', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('error', foreground='#f87171', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('advertencia', foreground='#fbbf24', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('linea', foreground='#60a5fa', font=('Consolas', 9))
        self.consola_text.tag_config('resumen', foreground='#c084fc', font=('Consolas', 11, 'bold'))
        
        # Frame de resumen
        self.resumen_frame = tk.Frame(right_panel, bg='#d1d5db', relief=tk.SUNKEN, bd=2)
        self.resumen_label = tk.Label(self.resumen_frame, text="", 
                                     font=('Arial', 10), bg='#d1d5db', 
                                     justify=tk.LEFT, anchor=tk.W)
        self.resumen_label.pack(fill=tk.X, padx=10, pady=10)

    def analizar_codigo(self):
        """Ejecuta el análisis del código"""
        codigo = self.codigo_text.get('1.0', tk.END)
        
        # Limpiar consola
        self.consola_text.config(state=tk.NORMAL)
        self.consola_text.delete('1.0', tk.END)
        
        # Analizar con el compilador
        resultado = self.compilador.analizar(codigo)
        
        # Mostrar mensajes
        self.mostrar_mensajes(resultado['mensajes'])
        
        # Actualizar estadísticas
        stats = resultado['estadisticas']
        self.actualizar_estadisticas(stats['aciertos'], stats['errores'])
        
        self.consola_text.config(state=tk.DISABLED)
    
    def mostrar_mensajes(self, mensajes):
        """Muestra los mensajes en la consola"""
        for msg in mensajes:
            linea_text = f"[Línea {msg['linea']}] "
            self.consola_text.insert(tk.END, linea_text, 'linea')
            
            if msg['tipo'] == 'exito':
                self.consola_text.insert(tk.END, f"✅ {msg['mensaje']}\n", 'exito')
            elif msg['tipo'] == 'error':
                self.consola_text.insert(tk.END, f"❌ {msg['mensaje']}\n", 'error')
            else:
                self.consola_text.insert(tk.END, f"⚠️  {msg['mensaje']}\n", 'advertencia')
        
        # Resumen final
        if mensajes:
            self.mostrar_resumen(mensajes)
    
    def mostrar_resumen(self, mensajes):
        """Muestra el resumen de compilación"""
        aciertos = sum(1 for m in mensajes if m['tipo'] == 'exito')
        errores = sum(1 for m in mensajes if m['tipo'] == 'error')
        
        self.consola_text.insert(tk.END, f"\n{'='*50}\n", 'resumen')
        self.consola_text.insert(tk.END, f"📊 RESUMEN FINAL\n", 'resumen')
        self.consola_text.insert(tk.END, f"{'='*50}\n", 'resumen')
        
        if errores == 0 and aciertos > 0:
            self.consola_text.insert(tk.END, "¡Quedó chevere parce! Todo bien 🎉\n", 'exito')
        
        resumen_text = f"📋 {aciertos} líneas correctas | {errores} con errores"
        self.resumen_label.config(text=resumen_text)
        self.resumen_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def actualizar_estadisticas(self, aciertos, errores):
        """Actualiza las estadísticas en el header"""
        self.aciertos_label.config(text=f"{aciertos}\nAciertos")
        self.errores_label.config(text=f"{errores}\nErrores")