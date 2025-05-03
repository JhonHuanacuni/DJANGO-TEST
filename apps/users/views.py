# users/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.users.serializers import UsuarioSerializer
from apps.users.models import Usuario
from django.contrib.auth.hashers import make_password
from rest_framework.generics import get_object_or_404

from apps.users.permissions.roles import IsAdmin, IsSecretario, IsUsuario
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
import os
from django.conf import settings
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import qrcode
from io import BytesIO


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {'non_field_errors': ['Credenciales inválidas']},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']
        
        if not user.is_active:
            return Response(
                {'non_field_errors': ['Cuenta desactivada']},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'usuario': UsuarioSerializer(user).data
        })

class UsuarioActualAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        serializer = UsuarioSerializer(usuario)

        # Respuesta diferente según el rol
        mensaje = ""
        if usuario.rol == "admin":
            mensaje = "Tienes acceso completo al sistema: gestión de usuarios, reportes y configuración."
        elif usuario.rol == "secretario":
            mensaje = "Puedes registrar clientes, gestionar asistencias y manejar membresías."
        elif usuario.rol == "usuario":
            mensaje = "Puedes ver tu información personal, asistencias y membresía."

        return Response({
            "usuario": serializer.data,
            "rol_info": mensaje
        })

class UsuarioListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class CrearUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsSecretario]

    def post(self, request):
        data = request.data
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            usuario = serializer.save()
            response_data = serializer.data
            
            # Generar QR solo si el usuario tiene DNI
            if usuario.dni:
                qr_path = usuario.generar_qr()
                if qr_path:
                    response_data['qr_url'] = f'{settings.MEDIA_URL}{qr_path}'
                else:
                    response_data['qr_url'] = None
                    response_data['error_qr'] = 'No se pudo generar el código QR'
            
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)
    
class EditarUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin| IsSecretario]

    def put(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)  # `partial=True` permite actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

class EliminarUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.delete()
        return Response({"detail": "Usuario eliminado correctamente."}, status=204)

class GenerarCarnetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            usuario = Usuario.objects.get(id=pk)
            
            # Datos del usuario (MODIFICADO PARA APELLIDOS COMPUESTOS)
            nombre = f"{usuario.nombres}".capitalize()
            apellido = ' '.join([part.capitalize() for part in usuario.apellidos.split()])  # <- Cambio clave aquí
            dni = usuario.dni

            # Generar el QR solo con el DNI
            qr_data = f"{dni}"
            qr_image = qrcode.make(qr_data)
            qr_path = os.path.join(settings.MEDIA_ROOT, "qrcodes", f"qr_{dni}.png")
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            qr_image.save(qr_path)


            # Seleccionar plantilla según el rol
            if usuario.rol == "admin":
                plantilla_nombre = "TemplateAdministradorVaron.pdf"
            elif usuario.rol == "secretario":
                plantilla_nombre = "TemplateSecretarioVaron.pdf"
            else:
                plantilla_nombre = "TemplateEstudianteVaron.pdf"
            plantilla_pdf_path = os.path.join(settings.MEDIA_ROOT, "templateCarnet", plantilla_nombre)
            output_pdf_path = os.path.join(settings.MEDIA_ROOT, "templateCarnet", f"output_carnet.pdf")
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

            # Configurar tamaño del PDF
            pdf_width = 50 * mm
            pdf_height = 85 * mm
            
            # Crear el PDF
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(pdf_width, pdf_height))
            
            # Configuración inicial de fuente para nombre y apellido
            c.setFont("Helvetica-Bold", 10)
            
            # Centrar textos (nombre y apellido)
            nombre_width = c.stringWidth(nombre, "Helvetica-Bold", 10)
            apellido_width = c.stringWidth(apellido, "Helvetica-Bold", 10)
            
            nombre_x = (pdf_width - nombre_width) / 2
            apellido_x = (pdf_width - apellido_width) / 2
            
            nombre_y = 38 * mm
            apellido_y = 34 * mm
            dni_y = 7 * mm
            qr_y = (11 * mm)-0.65 * mm
            
            # Dibujar nombre y apellido
            c.drawString(nombre_x, nombre_y, nombre)
            c.drawString(apellido_x, apellido_y, apellido)
            
            # Configurar DNI con tamaño de letra más pequeño
            c.setFont("Helvetica-Bold", 5)  # Tamaño reducido a 8
            dni_width = c.stringWidth(f"{dni}", "Helvetica-Bold", 5)  # Ahora usa 8
            dni_x = (pdf_width - dni_width) / 2  # Recalcula posición
            
            c.setFillColorRGB(0.5, 0.5, 0.5)  # Color gris
            c.drawString(dni_x, dni_y, f"{dni}")
            c.setFillColorRGB(0, 0, 0)  # Volver a color negro
            
            # Posicionamiento del QR
            qr_size = 20 * mm
            qr_x = ((pdf_width - qr_size) / 2)-0.25 * mm
            c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)
            
            c.save()
            packet.seek(0)
            
            # Unir los PDFs
            new_pdf = PdfReader(packet)
            existing_pdf = PdfReader(open(plantilla_pdf_path, "rb"))
            output = PdfWriter()
            
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            
            with open(output_pdf_path, "wb") as outputStream:
                output.write(outputStream)

            # Enviar el PDF como respuesta
            with open(output_pdf_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="carnet_{dni}.pdf"'
                return response

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class CambiarPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 8:
            return Response({'error': 'La contraseña debe tener al menos 8 caracteres.'}, status=400)
        user.password = make_password(new_password)
        user.save()
        return Response({'detail': 'Contraseña actualizada correctamente.', 'username': user.username})