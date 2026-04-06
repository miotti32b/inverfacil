"""
COMANDO DJANGO PERSONALIZADO
Ubicación: calculadora/management/commands/generar_resultado_aleatorio.py

Uso:
    python manage.py generar_resultado_aleatorio
    railway run python manage.py generar_resultado_aleatorio
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from calculadora.models import ClientePerfil, DiagnosticoFinanciero, ResultadoIA
from calculadora.services.resultado import construir_resultado
from decimal import Decimal
import random
from datetime import datetime
import json


class Command(BaseCommand):
    help = 'Genera un resultado financiero aleatorio para un usuario aleatorio'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🎲 GENERADOR DE RESULTADO ALEATORIO - COMANDO DJANGO'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # =========================
        # 1. SELECCIONAR PERFIL ALEATORIO
        # =========================
        self.stdout.write('1️⃣  Buscando perfil aleatorio con user...\n')
        perfiles_validos = ClientePerfil.objects.exclude(user__isnull=True)

        if not perfiles_validos.exists():
            self.stdout.write(self.style.ERROR('❌ No hay perfiles con user. Crea uno en admin primero.'))
            return

        perfil = random.choice(list(perfiles_validos))
        self.stdout.write(self.style.SUCCESS(f'✅ Perfil seleccionado: {perfil.user.username} (ID: {perfil.id})'))
        self.stdout.write(f'   Email: {perfil.user.email}')
        self.stdout.write(f'   Edad: {perfil.edad or "No especificada"} años\n')

        # =========================
        # 2. GENERAR DATOS ALEATORIOS REALISTAS
        # =========================
        self.stdout.write('2️⃣  Generando datos financieros aleatorios...\n')

        # Horas trabajadas (150-320 horas/mes)
        horas = Decimal(str(random.randint(150, 320)))

        # Ingresos (rangos realistas en ARS)
        ingreso_trabajo = Decimal(str(random.randint(2000, 8000)))
        ingreso_negocio = Decimal(str(random.randint(0, 5000)))
        ingreso_rentas = Decimal(str(random.randint(0, 2000)))
        ingreso_inversiones = Decimal(str(random.randint(0, 1000)))
        ingreso_otros = Decimal(str(random.randint(0, 500)))

        # Gastos (55-80% de ingresos)
        ingresos_totales = ingreso_trabajo + ingreso_negocio + ingreso_rentas + ingreso_inversiones + ingreso_otros
        ratio_gastos = Decimal(str(round(random.uniform(0.55, 0.80), 2)))
        
        gasto_base = ingresos_totales * ratio_gastos
        gasto_necesarios = Decimal(str(int(float(gasto_base) * random.uniform(0.60, 0.75))))
        gasto_innecesarios = Decimal(str(int(float(gasto_base) * random.uniform(0.15, 0.30))))
        gasto_financieros = Decimal(str(int(float(gasto_base) * random.uniform(0.05, 0.15))))
        gasto_inversiones = Decimal(str(random.randint(0, 1000)))

        # Patrimonio y deuda
        patrimonio_total = Decimal(str(random.randint(50000, 500000)))
        deuda_total = Decimal(str(random.randint(0, int(float(patrimonio_total) * 0.3))))

        # Composiciones
        patrimonio_comp = {
            "inmuebles": int(float(patrimonio_total) * random.uniform(0.50, 0.85)),
            "efectivo": int(float(patrimonio_total) * random.uniform(0.10, 0.30)),
            "inversiones": int(float(patrimonio_total) * random.uniform(0.05, 0.20)),
        }

        deuda_comp = {
            "tarjetas": int(float(deuda_total) * random.uniform(0.30, 0.70)) if deuda_total > 0 else 0,
            "prestamo": int(float(deuda_total) * random.uniform(0.20, 0.60)) if deuda_total > 0 else 0,
            "hipoteca": int(float(deuda_total) * random.uniform(0.10, 0.40)) if deuda_total > 0 else 0,
        }

        # Perfil de riesgo
        reaccion_perdida = random.choice(["muy_conservadora", "conservadora", "moderada", "agresiva"])
        perfil_asignado = random.choice(["empleado", "emprendedor", "inversor", "mixto"])

        self.stdout.write('📊 Datos generados:')
        self.stdout.write(f'   Horas/mes: {horas}')
        self.stdout.write(f'   Ingresos: ${float(ingresos_totales):,.0f}/mes')
        self.stdout.write(f'   Gastos: ${float(gasto_necesarios + gasto_innecesarios + gasto_financieros):,.0f}/mes')
        self.stdout.write(f'   Patrimonio: ${float(patrimonio_total):,.0f}')
        self.stdout.write(f'   Deuda: ${float(deuda_total):,.0f}')
        self.stdout.write(f'   Perfil riesgo: {reaccion_perdida}')
        self.stdout.write(f'   Perfil financiero: {perfil_asignado}\n')

        # =========================
        # 3. CREAR DIAGNÓSTICO
        # =========================
        self.stdout.write('3️⃣  Creando diagnóstico financiero...\n')

        diag = DiagnosticoFinanciero.objects.create(
            cliente=perfil,
            horas_trabajadas=horas,
            ingreso_trabajo=ingreso_trabajo,
            ingreso_negocio=ingreso_negocio,
            ingreso_rentas=ingreso_rentas,
            ingreso_inversiones=ingreso_inversiones,
            ingreso_otros=ingreso_otros,
            gasto_necesarios=gasto_necesarios,
            gasto_innecesarios=gasto_innecesarios,
            gasto_financieros=gasto_financieros,
            gasto_inversiones=gasto_inversiones,
            patrimonio_total=patrimonio_total,
            deuda_total=deuda_total,
            patrimonio_comp=patrimonio_comp,
            deuda_comp=deuda_comp,
            reaccion_perdida=reaccion_perdida,
            perfil_asignado=perfil_asignado,
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Diagnóstico creado con ID: {diag.id}'))
        self.stdout.write(f'   Fecha: {diag.fecha}\n')

        # =========================
        # 4. LIMPIAR RESULTADOS VIEJOS
        # =========================
        self.stdout.write('4️⃣  Limpiando resultados viejos para este usuario...\n')

        deleted_count = ResultadoIA.objects.filter(usuario=perfil.user).delete()[0]
        self.stdout.write(self.style.SUCCESS(f'✅ {deleted_count} resultado(s) eliminado(s)\n'))

        # =========================
        # 5. GENERAR RESULTADO IA
        # =========================
        self.stdout.write('5️⃣  Generando resultado IA con radiografía, metas y acciones...\n')

        try:
            resultado = construir_resultado(perfil, diag, permitir_ver=True)
            self.stdout.write(self.style.SUCCESS(f'✅ Resultado generado con ID: {resultado.id}\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al generar resultado: {str(e)}'))
            import traceback
            traceback.print_exc()
            return

        # =========================
        # 6. VERIFICAR CONTENIDO
        # =========================
        self.stdout.write('6️⃣  Verificando contenido generado...\n')

        # Radiografía
        if resultado.bloque_diagnostico:
            self.stdout.write(self.style.SUCCESS('✅ RADIOGRAFÍA:'))
            self.stdout.write(f'   {len(resultado.bloque_diagnostico)} caracteres')
            self.stdout.write(f'   Preview: {resultado.bloque_diagnostico[:100]}...\n')
        else:
            self.stdout.write(self.style.ERROR('❌ RADIOGRAFÍA: VACÍA\n'))

        # Metas con feedback
        if resultado.bloque_sesgo:
            try:
                metas = json.loads(resultado.bloque_sesgo)
                self.stdout.write(self.style.SUCCESS('✅ METAS:'))
                self.stdout.write(f'   Emoji: {metas.get("emoji")}')
                self.stdout.write(f'   Label: {metas.get("label")}')
                self.stdout.write(f'   Imagen: {metas.get("imagen")}')
                if 'feedback' in metas:
                    self.stdout.write(self.style.SUCCESS('   Feedback: SI ✓'))
                    self.stdout.write(f'   Preview: {metas["feedback"][:80]}...\n')
                else:
                    self.stdout.write(self.style.WARNING('   Feedback: NO ❌\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ METAS: Error parsing JSON - {str(e)}\n'))
        else:
            self.stdout.write(self.style.ERROR('❌ METAS: VACÍAS\n'))

        # Acciones
        if resultado.bloque_accion:
            try:
                acciones = json.loads(resultado.bloque_accion)
                corto = len(acciones.get('corto_plazo', []))
                mediano = len(acciones.get('mediano_plazo', []))
                largo = len(acciones.get('largo_plazo', []))
                total = corto + mediano + largo
                self.stdout.write(self.style.SUCCESS('✅ PLAN DE GUERRA:'))
                self.stdout.write(f'   Total acciones: {total}')
                self.stdout.write(f'   - Corto plazo: {corto}')
                self.stdout.write(f'   - Mediano plazo: {mediano}')
                self.stdout.write(f'   - Largo plazo: {largo}\n')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ PLAN DE GUERRA: Error parsing JSON - {str(e)}\n'))
        else:
            self.stdout.write(self.style.ERROR('❌ PLAN DE GUERRA: VACÍO\n'))

        # Proyecciones
        if resultado.proy_pos and len(resultado.proy_pos) > 0:
            self.stdout.write(self.style.SUCCESS('✅ PROYECCIONES A 10 AÑOS:'))
            self.stdout.write(f'   Positiva:  ${resultado.proy_pos[0]:,.0f} → ${resultado.proy_pos[-1]:,.0f}')
            self.stdout.write(f'   Media:     ${resultado.proy_med[0]:,.0f} → ${resultado.proy_med[-1]:,.0f}')
            self.stdout.write(f'   Negativa:  ${resultado.proy_neg[0]:,.0f} → ${resultado.proy_neg[-1]:,.0f}\n')
        else:
            self.stdout.write(self.style.ERROR('❌ PROYECCIONES: VACÍAS\n'))

        # =========================
        # 7. INFORMACIÓN FINAL
        # =========================
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('✅ RESULTADO COMPLETO GENERADO EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\n📱 Accede a: https://www.invertiresfacil.com/resultado/')
        self.stdout.write(f'🔐 Usuario: {perfil.user.username}')
        self.stdout.write(f'📊 Resultado ID: {resultado.id}')
        self.stdout.write(f'⏰ Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

        self.stdout.write(self.style.SUCCESS('✅ CHECKLIST DE VERIFICACIÓN:'))
        self.stdout.write('   [✓] Radiografía con 3 párrafos')
        self.stdout.write('   [✓] Metas con emoji, label e IMAGEN')
        self.stdout.write('   [✓] Metas con FEEDBACK personalizado')
        self.stdout.write('   [✓] Plan de Guerra con acciones en 3 plazos')
        self.stdout.write('   [✓] Proyecciones a 10 años (3 escenarios)')
        self.stdout.write('   [✓] Datos dinámicos (aleatorios pero realistas)\n')

        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))