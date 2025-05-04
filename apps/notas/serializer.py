from rest_framework import serializers
from apps.notas.models import Nota, ImportacionNotas
from apps.users.models import Usuario

class NotaSerializer(serializers.ModelSerializer):
    fecha_importacion = serializers.SerializerMethodField()

    class Meta:
        model = Nota
        fields = [
            'id', 'estudiante', 'puntaje', 'porcentaje', 'correctas', 'incorrectas', 'no_respuesta',
            'act', 'hm', 'hv', 'arit', 'geo', 'alge', 'trigo', 'lengua', 'lit', 'psi', 'civ', 'hp', 'hu', 'geo_l',
            'eco', 'filo', 'fis', 'qui', 'bio', 'descripcion', 'modo', 'fecha_importacion'
        ]

    def get_fecha_importacion(self, obj):
        return obj.importacion.fecha_importacion.isoformat() if obj.importacion else None


class NotaBulkImportWithImportacionSerializer(serializers.Serializer):
    nombre_archivo = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField())
    tipo_importacion = serializers.IntegerField(required=False, default=40)
    salon_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get('nombre_archivo'):
            raise serializers.ValidationError("El nombre del archivo es requerido")
        if not data.get('data'):
            raise serializers.ValidationError("Los datos son requeridos")
        return data

    def create(self, validated_data):
        try:
            request = self.context.get('request')
            usuario = request.user if request else None
            nombre_archivo = validated_data['nombre_archivo']
            data = validated_data['data']
            tipo_importacion = validated_data.get('tipo_importacion', 40)
            salon_id = validated_data.get('salon_id')
            print(f"[DEBUG] Tipo de importación recibido: {tipo_importacion}")
            importacion = ImportacionNotas.objects.create(
                importado_por=usuario,
                nombre_archivo=nombre_archivo,
                salon_id=salon_id
            )
            notas_creadas = []
            if tipo_importacion == 100:
                print("[DEBUG] Entrando al bloque de 100 preguntas")
                DISTRIBUCION_100 = [
                    ('act', 10), ('hm', 10), ('hv', 10), ('arit', 4), ('geo', 3), ('alge', 3), ('trigo', 2),
                    ('lengua', 7), ('lit', 4), ('psi', 6), ('civ', 4), ('hp', 3), ('hu', 2), ('geo_l', 4),
                    ('eco', 4), ('filo', 4), ('fis', 5), ('qui', 7), ('bio', 8)
                ]
                AREAS_ORDENADAS = [a for a, n in DISTRIBUCION_100 for _ in range(n)]
                import builtins  # Asegura que la función len original esté disponible
                for idx, row in enumerate(data):
                    dni = str(row.get('Student Dni') or row.get('DNI')).strip()
                    print(f"[DEBUG] Procesando fila {idx+1} con DNI: '{dni}'")
                    if not dni:
                        print(f"[DEBUG] Fila {idx+1} sin DNI, se omite")
                        continue
                    try:
                        estudiante = Usuario.objects.get(dni=dni)
                    except Usuario.DoesNotExist:
                        print(f"[DEBUG] Usuario con DNI '{dni}' no encontrado, se omite la fila {idx+1}")
                        continue
                    puntaje = row.get('Earned Points', 0)
                    porcentaje = row.get('Percent Correct', 0)
                    correctas = incorrectas = no_respuesta = 0
                    puntos = []
                    descripcion = []
                    area_puntajes = {a: 0 for a, _ in DISTRIBUCION_100}
                    area_puntajes['mis'] = 0
                    for i in range(1, 101):
                        pts = row.get(f'#{i} Points Earned')
                        resp = row.get(f'#{i} Student Response', '')
                        puntos.append(pts)
                        if pts == 20:
                            correctas += 1
                        elif pts == -1.125:
                            incorrectas += 1
                            descripcion.append(f'{i}:{resp}')
                        elif pts in [None, '', ' ']:
                            no_respuesta += 1
                        area = AREAS_ORDENADAS[i-1] if i-1 < builtins.len(AREAS_ORDENADAS) else 'mis'
                        if pts == 20:
                            area_puntajes[area] = area_puntajes.get(area, 0) + 1
                    print(f"[DEBUG] Resumen fila {idx+1}: correctas={correctas}, incorrectas={incorrectas}, no_respuesta={no_respuesta}, area_puntajes={area_puntajes}")
                    nota = Nota.objects.create(
                        estudiante=estudiante,
                        puntaje=puntaje,
                        porcentaje=porcentaje,
                        correctas=correctas,
                        incorrectas=incorrectas,
                        no_respuesta=no_respuesta,
                        act=area_puntajes['act'],
                        hm=area_puntajes['hm'],
                        hv=area_puntajes['hv'],
                        arit=area_puntajes['arit'],
                        geo=area_puntajes['geo'],
                        alge=area_puntajes['alge'],
                        trigo=area_puntajes['trigo'],
                        lengua=area_puntajes['lengua'],
                        lit=area_puntajes['lit'],
                        psi=area_puntajes['psi'],
                        civ=area_puntajes['civ'],
                        hp=area_puntajes['hp'],
                        hu=area_puntajes['hu'],
                        geo_l=area_puntajes['geo_l'],
                        eco=area_puntajes['eco'],
                        filo=area_puntajes['filo'],
                        fis=area_puntajes['fis'],
                        qui=area_puntajes['qui'],
                        bio=area_puntajes['bio'],
                        descripcion=','.join(descripcion),
                        importacion=importacion,
                        modo=row.get('Modo', 'presencial')
                    )
                    print(f"[DEBUG] Nota creada para estudiante DNI '{dni}', ID nota: {nota.id}")
                    notas_creadas.append(nota)
                print("[DEBUG] Fin del bloque de 100 preguntas")
                return notas_creadas
            # Lógica original para 40 preguntas
            for row in data:
                dni = str(row.get('Student Dni')).strip()
                try:
                    estudiante = Usuario.objects.get(dni=dni)
                except Usuario.DoesNotExist:
                    continue
                puntaje = row.get('Earned Points', 0)
                porcentaje = row.get('Percent Correct', 0)
                correctas = incorrectas = no_respuesta = 0
                puntos = []
                descripcion = []
                for i in range(1, 41):
                    pts = row.get(f'#{i} Points Earned')
                    resp = row.get(f'#{i} Student Response', '')
                    puntos.append(pts)
                    if pts == 20:
                        correctas += 1
                    elif pts == -1.125:
                        incorrectas += 1
                        descripcion.append(f'{i}:{resp}')
                    elif pts in [None, '', ' ']:
                        no_respuesta += 1
                hm = sum(1 for pts in puntos[0:4] if pts == 20)
                hv = sum(1 for pts in puntos[4:8] if pts == 20)
                arit = sum(1 for pts in puntos[8:10] if pts == 20)
                geo = sum(1 for pts in puntos[10:12] if pts == 20)
                alge = sum(1 for pts in puntos[12:14] if pts == 20)
                trigo = sum(1 for pts in puntos[14:16] if pts == 20)
                lengua = sum(1 for pts in puntos[16:18] if pts == 20)
                psi = sum(1 for pts in puntos[18:20] if pts == 20)
                civ = sum(1 for pts in puntos[20:22] if pts == 20)
                hp = sum(1 for pts in puntos[22:24] if pts == 20)
                hu = sum(1 for pts in puntos[24:26] if pts == 20)
                geo_l = sum(1 for pts in puntos[26:28] if pts == 20)
                eco = sum(1 for pts in puntos[28:30] if pts == 20)
                filo = sum(1 for pts in puntos[30:32] if pts == 20)
                fis = sum(1 for pts in puntos[32:34] if pts == 20)
                qui = sum(1 for pts in puntos[34:36] if pts == 20)
                bio = sum(1 for pts in puntos[36:40] if pts == 20)
                nota = Nota.objects.create(
                    estudiante=estudiante,
                    puntaje=puntaje,
                    porcentaje=porcentaje,
                    correctas=correctas,
                    incorrectas=incorrectas,
                    no_respuesta=no_respuesta,
                    hm=hm, hv=hv, arit=arit, geo=geo, alge=alge, trigo=trigo, lengua=lengua, psi=psi,
                    civ=civ, hp=hp, hu=hu, geo_l=geo_l, eco=eco, filo=filo, fis=fis, qui=qui, bio=bio,
                    descripcion=','.join(descripcion),
                    importacion=importacion
                )
                notas_creadas.append(nota)
            return notas_creadas
        except Exception as e:
            raise serializers.ValidationError(str(e))