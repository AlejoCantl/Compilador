import ply.yacc as yacc
from lexer import tokens, analizador_lexico, errores_lexicos, limpiar_errores_lexicos

class Compilador:
    def __init__(self):
        self.tabla_simbolos = {}
        self.mensajes_consola = []
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
        self.ultima_linea_completa = 0
        self.linea_actual = 0
        self.ultima_linea_error_semicolon = -1
    
    tokens = tokens
    
    def reset(self):
        """Limpia el estado del compilador"""
        self.tabla_simbolos.clear()
        self.mensajes_consola.clear()
        self.ultima_linea_completa = 0
        self.linea_actual = 0
        self.ultima_linea_error_semicolon = -1
    
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
        limpiar_errores_lexicos()  # ⭐ Limpiar errores léxicos anteriores
        analizador_lexico.lineno = 1
        
        try:
            resultado = self.parser.parse(codigo, lexer=analizador_lexico, tracking=True)
            
            # ⭐ Agregar errores léxicos a los mensajes
            for error in errores_lexicos:
                self.mensajes_consola.append(error)
            
            # ⭐ Ordenar mensajes por línea
            self.mensajes_consola.sort(key=lambda x: x['linea'] if isinstance(x['linea'], int) else 999999)
            
            return {
                'exito': True,
                'resultado': resultado,
                'mensajes': self.mensajes_consola,
                'estadisticas': self.obtener_estadisticas()
            }
        except Exception as e:
            # ⭐ Agregar errores léxicos incluso si hubo excepción
            for error in errores_lexicos:
                self.mensajes_consola.append(error)
            
            self.mensajes_consola.sort(key=lambda x: x['linea'] if isinstance(x['linea'], int) else 999999)
            
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
        # ⭐ FIX: Detectar expresiones de error
        if expresion[0] == 'error':
            return 'Error'
        
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
    
    def obtener_valor_expresion(self, expresion):
        """Obtiene el valor real de una expresión (para mostrar en mensajes)"""
        # ⭐ FIX: No intentar obtener valor de expresiones de error
        if expresion[0] == 'error':
            return None
        
        if expresion[0] == 'operacion_binaria':
            resultado = self.evaluar_operacion(expresion)
            if resultado is not None:
                # Mostrar como Entero si es decimal exacto, sino como Real
                if isinstance(resultado, float) and resultado == int(resultado):
                    return str(int(resultado))
                return str(resultado)
            return "[operación no evaluable]"
        elif expresion[0] == 'cadena':
            return expresion[1]
        elif expresion[0] == 'variable':
            variable = expresion[1]
            if variable in self.tabla_simbolos and self.tabla_simbolos[variable]['valor'] is not None:
                valor_almacenado = self.tabla_simbolos[variable]['valor']
                return self.obtener_valor_expresion(valor_almacenado)
            return f"[{variable}]"
        elif expresion[0] == 'numero':
            return str(expresion[1])
        else:
            return str(expresion)
    
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
        self.ultima_linea_completa = linea
    
    def p_sentencia_declaracion_sin_punto_y_coma(self, t):
        'sentencia : IDENTIFICADOR tipo'
        var, tipo_var = t[1], t[2]
        linea = t.lineno(1)
        self.agregar_mensaje('error', linea, f"¡Ey cole! Te faltó el punto y coma (;) en la línea {linea}. ¡Todo está mal a partir de aquí!")
        t[0] = None
    
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
                    f"¡Esa vaina que cole! No puedes meter {tipo_expresion} en '{var}' que es {tipo_declarado}")
                t[0] = None
            else:
                self.tabla_simbolos[var]['valor'] = expr
                self.agregar_mensaje('exito', linea, f"¡Tá bueno! {tipo_expresion} → {var}({tipo_declarado})")
                t[0] = ('asignar', var, expr)
        self.ultima_linea_completa = linea
    
    def p_sentencia_asignacion_sin_punto_y_coma(self, t):
        'sentencia : IDENTIFICADOR IGUAL expresion'
        var, expr = t[1], t[3]
        linea = t.lineno(1)
        self.agregar_mensaje('error', linea, f"¡Ey cole! Te faltó el punto y coma (;) en la línea {linea}. ¡Todo está mal a partir de aquí!")
        t[0] = None
    
    def p_sentencia_mensaje(self, t):
        '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO PARENTESIS_DER PUNTO_Y_COMA
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA'''
        linea = t.lineno(1)
        valor_texto = t[5]
        
        es_error = False
        error_mensaje = None
        valor_mostrar = None
        
        # ⭐ FIX: Detectar expresiones de error primero
        if isinstance(valor_texto, tuple) and valor_texto[0] == 'error':
            var_nombre = valor_texto[1]
            self.agregar_mensaje('error', linea, f"¡Ombe! La variable '{var_nombre}' no existe, no puedo mostrar un fantasma.")
            t[0] = None
            self.ultima_linea_completa = linea
            return
        
        # Check if it's an empty string
        if isinstance(valor_texto, str) and valor_texto == "":
            es_error = True
            error_mensaje = "¡Ombe! Mensaje.Texto está vacío, ponle algo pues."
        elif isinstance(valor_texto, tuple) and valor_texto[0] == 'operacion_binaria':
            tipo_expresion = self.obtener_tipo_expresion(valor_texto)
            if 'Error:' in str(tipo_expresion):
                es_error = True
                error_mensaje = tipo_expresion
            else:
                valor_mostrar = self.obtener_valor_expresion(valor_texto)
        # Check if it's a variable
        elif isinstance(valor_texto, tuple) and valor_texto[0] == 'variable':
            var_nombre = valor_texto[1]
            # Check if variable exists
            if var_nombre not in self.tabla_simbolos:
                es_error = True
                error_mensaje = f"¡Ombe! La variable '{var_nombre}' no existe, no puedo mostrar un fantasma."
            # Check if variable has a value assigned
            elif self.tabla_simbolos[var_nombre]['valor'] is None:
                es_error = True
                error_mensaje = f"¡Eche! La variable '{var_nombre}' no tiene valor, asígnale algo primero."
            else:
                valor_mostrar = self.obtener_valor_expresion(valor_texto)
        elif isinstance(valor_texto, tuple) and valor_texto[0] == 'cadena':
            valor_mostrar = valor_texto[1]
            if valor_mostrar == "":
                es_error = True
                error_mensaje = "¡Ombe! Mensaje.Texto está vacío, ponle algo pues."
        else:
            valor_mostrar = str(valor_texto)
        
        if es_error:
            self.agregar_mensaje('error', linea, error_mensaje)
        elif valor_mostrar is not None:
            self.agregar_mensaje('exito', linea, f"Nojoda monstruo está bueno el valor es \"{valor_mostrar}\"")
        
        t[0] = ('mensaje_texto', t[5])
        self.ultima_linea_completa = linea
    
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
            # ⭐ NO agregar mensaje aquí, solo marcar como error
            # El mensaje se mostrará donde se use la variable
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
            
            if linea > self.ultima_linea_completa + 1:
                # Check if this is a new error (not duplicate)
                if linea != self.ultima_linea_error_semicolon:
                    # Only report if there's actual code on the previous line
                    linea_anterior_tiene_codigo = False
                    for msg in self.mensajes_consola:
                        if msg['linea'] == linea - 1 and msg['tipo'] in ['exito', 'error']:
                            linea_anterior_tiene_codigo = True
                            break
                    
                    if linea_anterior_tiene_codigo:
                        self.agregar_mensaje('error', linea, f"¡Ey cole! Te faltó el punto y coma (;) en la línea {linea - 1}. ¡Todo está mal a partir de aquí!")
                        self.ultima_linea_error_semicolon = linea
            else:
                # If it's in the same line, it's a syntax error
                self.agregar_mensaje('error', linea, f"¡Qué vaina! Hay un error con '{t.value}' aquí mano")
            
            # Better error recovery
            while True:
                tok = self.parser.token()
                if not tok or tok.type == 'PUNTO_Y_COMA':
                    break
            self.parser.errok()
            return tok
        else:
            self.agregar_mensaje('error', '?', "¡Ombe! El archivo se acabó pero falta algo, revísalo completo.")
    
    def evaluar_operacion(self, expresion):
        """Evalúa una operación binaria y retorna el resultado numérico"""
        if expresion[0] == 'operacion_binaria':
            op, izq, der = expresion[1], expresion[2], expresion[3]
            
            # Evaluar operandos recursivamente
            val_izq = self.evaluar_operacion(izq)
            val_der = self.evaluar_operacion(der)
            
            if val_izq is None or val_der is None:
                return None
            
            try:
                if op == '+':
                    return val_izq + val_der
                elif op == '-':
                    return val_izq - val_der
                elif op == '*':
                    return val_izq * val_der
                elif op == '/':
                    if val_der == 0:
                        return None
                    return val_izq / val_der
            except:
                return None
        elif expresion[0] == 'numero':
            return expresion[1]
        elif expresion[0] == 'variable':
            var = expresion[1]
            if var in self.tabla_simbolos and self.tabla_simbolos[var]['valor'] is not None:
                return self.evaluar_operacion(self.tabla_simbolos[var]['valor'])
        return None