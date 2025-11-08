import ply.yacc as yacc
from lexer import tokens, analizador_lexico

class Compilador:
    def __init__(self):
        self.tabla_simbolos = {}
        self.mensajes_consola = []
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
    tokens = tokens
    
    def reset(self):
        """Limpia el estado del compilador"""
        self.tabla_simbolos.clear()
        self.mensajes_consola.clear()
    
    def agregar_mensaje(self, tipo, linea, mensaje):
        """Agrega un mensaje a la consola"""
        self.mensajes_consola.append({
            'tipo': tipo,
            'linea': linea,
            'mensaje': mensaje
        })
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de compilación"""
        aciertos = sum(1 for m in self.mensajes_consola if m['tipo'] == 'exito')
        errores = sum(1 for m in self.mensajes_consola if m['tipo'] == 'error')
        return {'aciertos': aciertos, 'errores': errores}
    
    def analizar(self, codigo):
        """Analiza el código y retorna los resultados"""
        self.reset()
        analizador_lexico.lineno = 1
        try:
            resultado = self.parser.parse(codigo, lexer=analizador_lexico, tracking=True)
            return {
                'exito': True,
                'resultado': resultado,
                'mensajes': self.mensajes_consola,
                'estadisticas': self.obtener_estadisticas()
            }
        except Exception as e:
            self.agregar_mensaje('error', '?', f"¡Qué desastre! Algo se dañó en el análisis: {str(e)}")
            return {
                'exito': False,
                'resultado': None,
                'mensajes': self.mensajes_consola,
                'estadisticas': self.obtener_estadisticas()
            }
    
    # ============ VALIDACIÓN DE TIPOS ============
    def obtener_tipo_expresion(self, expresion):
        """Determina el tipo de una expresión con validación estricta"""
        if expresion[0] == 'numero':
            valor = expresion[1]
            return 'Entero' if isinstance(valor, int) else 'Real'
        elif expresion[0] == 'cadena':
            return 'Texto'
        elif expresion[0] == 'variable':
            variable = expresion[1]
            if variable not in self.tabla_simbolos:
                return 'Desconocido'
            
            # ⭐ VALIDAR SI LA VARIABLE TIENE VALOR ASIGNADO
            if self.tabla_simbolos[variable]['valor'] is None:
                return f'Error: La variable "{variable}" no tiene valor todavía, asígnale algo primero'
            
            return self.tabla_simbolos.get(variable, {}).get('tipo', 'Desconocido')
        elif expresion[0] == 'capturar':
            tipo_captura = expresion[1]
            parametro = expresion[2]
            tipo_parametro = self.obtener_tipo_expresion(parametro)
        
            if tipo_captura == 'Entero' and tipo_parametro != 'Entero':
                return f'Error: Captura.Entero espera Entero, pero le mandaste {tipo_parametro}'
            elif tipo_captura == 'Real' and tipo_parametro not in ['Entero', 'Real']:
                return f'Error: Captura.Real espera un número, pero le mandaste {tipo_parametro}'
            elif tipo_captura == 'Texto' and tipo_parametro != 'Texto':
                return f'Error: Captura.Texto espera texto, pero le mandaste {tipo_parametro}'
        
            return tipo_captura

        elif expresion[0] == 'operacion_binaria':
            op, izq, der = expresion[1], expresion[2], expresion[3]
            tipo_izq = self.obtener_tipo_expresion(izq)
            tipo_der = self.obtener_tipo_expresion(der)

            # Si ya hay error en subexpresiones
            if 'Error:' in str(tipo_izq) or 'Error:' in str(tipo_der):
                return tipo_izq if 'Error:' in str(tipo_izq) else tipo_der

            # Validar suma con texto (solo permitida entre Texto + Texto)
            if op == '+':
                if tipo_izq == 'Texto' or tipo_der == 'Texto':
                    if tipo_izq == 'Texto' and tipo_der == 'Texto':
                        return 'Texto'
                    else:
                        return f'Error: No puedes sumar Texto con {tipo_izq if tipo_izq != "Texto" else tipo_der}'
                else:
                    return 'Real'
            else:
                # Para -, *, / → solo números
                if tipo_izq not in ['Entero', 'Real'] or tipo_der not in ['Entero', 'Real']:
                    return f'Error: La operación "{op}" solo funciona con números, no con {tipo_izq} y {tipo_der}'
                return 'Real'

        return 'Desconocido'
    
    def tipos_compatibles(self, tipo_declarado, tipo_expresion):
        """Verifica si los tipos son compatibles"""
        if 'Error:' in str(tipo_expresion):
            return False
        
        compatibilidad = {
            'Entero': ['Entero'],
            'Real': ['Entero', 'Real'],
            'Texto': ['Texto']
        }
        return tipo_expresion in compatibilidad.get(tipo_declarado, [])
    
    # ============ GRAMÁTICA PLY ============
    precedence = (
        ('left', 'MAS', 'MENOS'),
        ('left', 'POR', 'DIVIDIDO'),
    )
    
    def p_programa(self, t):
        'programa : lista_sentencias'
        t[0] = t[1]
    
    def p_lista_sentencias(self, t):
        '''lista_sentencias : lista_sentencias sentencia
                            | sentencia'''
        if len(t) == 3:
            t[0] = t[1] + [t[2]] if t[2] is not None else t[1]
        else:
            t[0] = [t[1]] if t[1] is not None else []
    
    def p_tipo(self, t):
        '''tipo : ENTERO
                | REAL
                | TEXTO'''
        t[0] = t[1]
    
    def p_sentencia_declaracion(self, t):
        'sentencia : IDENTIFICADOR tipo PUNTO_Y_COMA'
        var, tipo_var = t[1], t[2]
        linea = t.lineno(1)
        
        if var in self.tabla_simbolos:
            self.agregar_mensaje('error', linea, f"¡Epa! La variable '{var}' ya la declaraste mano, no la repitas.")
            t[0] = None
        else:
            self.tabla_simbolos[var] = {'tipo': tipo_var, 'valor': None, 'linea': linea}
            self.agregar_mensaje('exito', linea, f"¡Bien ahí! Variable '{var}' quedó como {tipo_var}")
            t[0] = ('declarar', var, tipo_var)
    
    def p_sentencia_asignacion(self, t):
        'sentencia : IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA'
        var, expr = t[1], t[3]
        linea = t.lineno(1)
        
        if var not in self.tabla_simbolos:
            self.agregar_mensaje('error', linea, f"¡Ombe! La variable '{var}' no existe, declárala primero pues.")
            t[0] = None
        else:
            tipo_declarado = self.tabla_simbolos[var]['tipo']
            tipo_expresion = self.obtener_tipo_expresion(expr)
            
            if 'Error:' in str(tipo_expresion):
                self.agregar_mensaje('error', linea, tipo_expresion)
                t[0] = None
            elif not self.tipos_compatibles(tipo_declarado, tipo_expresion):
                self.agregar_mensaje('error', linea,
                    f"¡Eso no cuadra parce! No puedes meter {tipo_expresion} en '{var}' que es {tipo_declarado}")
                t[0] = None
            else:
                self.tabla_simbolos[var]['valor'] = expr
                self.agregar_mensaje('exito', linea, f"¡Tá bueno! {tipo_expresion} → {var}({tipo_declarado})")
                t[0] = ('asignar', var, expr)
    
    def p_sentencia_mensaje(self, t):
        '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO PARENTESIS_DER PUNTO_Y_COMA
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA'''
        linea = t.lineno(1)
        self.agregar_mensaje('exito', linea, "Mensaje listo pa' mostrar")
        t[0] = ('mensaje_texto', t[5])
    
    def p_expresion_binaria(self, t):
        '''expresion : expresion MAS expresion
                     | expresion MENOS expresion
                     | expresion POR expresion
                     | expresion DIVIDIDO expresion'''
        t[0] = ('operacion_binaria', t[2], t[1], t[3])
    
    def p_expresion_grupo(self, t):
        'expresion : PARENTESIS_IZQ expresion PARENTESIS_DER'
        t[0] = t[2]
    
    def p_expresion_valor(self, t):
        '''expresion : NUMERO_ENTERO
                     | NUMERO_REAL'''
        t[0] = ('numero', t[1])
    
    def p_expresion_identificador(self, t):
        'expresion : IDENTIFICADOR'
        var = t[1]
        linea = t.lineno(1)
        if var not in self.tabla_simbolos:
            self.agregar_mensaje('advertencia', linea, f"¡Ajá! La variable '{var}' no existe todavía.")
            t[0] = ('error', var)
        else:
            t[0] = ('variable', var)
    
    def p_expresion_cadena(self, t):
        'expresion : CADENA_TEXTO'
        t[0] = ('cadena', t[1])
    
    def p_expresion_captura(self, t):
        'expresion : CAPTURA PUNTO tipo PARENTESIS_IZQ expresion PARENTESIS_DER'
        t[0] = ('capturar', t[3], t[5])
    
    def p_error(self, t):
        if t:
            linea = t.lineno
            if t.type in ['IDENTIFICADOR', 'MENSAJE', 'CAPTURA']:
                self.agregar_mensaje('error', linea, "¡Ey cole! Te faltó el punto y coma (;) en la línea anterior.")
            else:
                self.agregar_mensaje('error', linea, f"¡Qué vaina! Hay un error con '{t.value}' aquí mano")
            
            # Mejor recuperación de errores
            while True:
                tok = self.parser.token()
                if not tok or tok.type == 'PUNTO_Y_COMA':
                    break
            self.parser.errok()
            return tok
        else:
            self.agregar_mensaje('error', '?', "¡Ombe! El archivo se acabó pero falta algo, revísalo completo.")
