from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ReporteForm, ActividadesForm
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from django.conf import settings
from django.core.mail import EmailMessage
from .email_utils import send_email_async
from io import BytesIO
from PIL import Image

def login_view(request):
    """Simple login page using credentials from settings."""
    error = False
    if request.method == 'GET':
        # Clear any existing session so the navigation
        # menu remains hidden on the login page
        request.session.flush()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == settings.USUARIO_WEB and password == settings.PASSWORD_WEB:
            request.session['authenticated'] = True
            request.session['usuario'] = username
            return redirect('formulario')
        error = True
    return render(request, 'core/login.html', {
        'error': error,
        'nombre': request.session.get('usuario')
    })

def formulario_view(request):
    if not request.session.get('authenticated'):
        return redirect('login')

    nombre = request.session.get('usuario')

    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data

            # Plantilla
            tpl = settings.BASE_DIR / 'core' / 'plantillas' / 'reporte.docx'
            doc = DocxTemplate(tpl)

            # Contexto de textos
            context = {
                'fecha': cd['fecha'],
                'nombre': cd['nombre'],
                'parque': cd['parque'],
                'inspeccion_compacto': cd['inspeccion_compacto'],
                'comentario_compacto': cd.get('comentario_compacto', ''),
                'inspeccion_reconectador': cd['inspeccion_reconectador'],
                'comentario_reconectador': cd.get('comentario_reconectador', ''),
                'inspeccion_medidor': cd['inspeccion_medidor'],
                'comentario_medidor': cd.get('comentario_medidor', ''),
                'inspeccion_sala_control': cd['inspeccion_sala_control'],
                'comentario_sala_control': cd.get('comentario_sala_control', ''),
                'inspeccion_linea_mt': cd['inspeccion_linea_mt'],
                'comentario_linea_mt': cd.get('comentario_linea_mt', ''),
                'inspeccion_ct': cd['inspeccion_ct'],
                'comentario_ct': cd.get('comentario_ct', ''),
                'inspeccion_inversores': cd['inspeccion_inversores'],
                'comentario_inversores': cd.get('comentario_inversores', ''),
                'inspeccion_modulos': cd['inspeccion_modulos'],
                'comentario_modulos': cd.get('comentario_modulos', ''),
                'nivel_soiling': cd['nivel_soiling'],
                'comentarios_supervisor': cd.get('comentarios_supervisor', ''),
            }

            # Función helper
            def mkimg(name):
                f = cd.get(name)
                if not f:
                    return None
                img = Image.open(f)
                img.thumbnail((int(120*11.8), int(105*11.8)))
                bio = BytesIO()
                img.save(bio, format=img.format or 'PNG')
                bio.seek(0)
                return InlineImage(doc, bio, width=Mm(120), height=Mm(105))

            # Insertar imágenes
            for key in [
                'imagen_ecm', 'imagen_reconectador', 'imagen_medidor',
                'imagen_sala_control', 'imagen_linea_mt', 'imagen_ct',
                'imagen_inversores', 'imagen_modulos', 'imagen_soiling'
            ]:
                context[key] = mkimg(key)

            # Fotos adicionales
            photos = []
            for i in range(1,11):
                img = mkimg(f'foto_adicional_{i}')
                if img:
                    photos.append(img)
            context['foto_adicional'] = photos

            # Generar DOCX
            doc.render(context)
            buf = BytesIO(); doc.save(buf); buf.seek(0)
            data = buf.getvalue()

            # Email condicional
            dest = cd.get('destinatario')
            if dest:
                mail = EmailMessage(
                    subject=f"Reporte inspección {cd['parque']} realizado por {cd['nombre']}",
                    body="Reporte adjunto",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[dest],
                )
                file_name = f"{cd['fecha'].strftime('%y-%m-%d')}_{cd['parque']}_{cd['nombre_archivo']}.docx"
                mail.attach(
                    filename=file_name,
                    content=data,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                send_email_async(mail)

            # Redirigir para evitar reenvío al refrescar
            return redirect(f"{reverse('formulario')}?success=1")

    else:
        form = ReporteForm()

    mensaje_exito = request.GET.get('success') == '1'
    if mensaje_exito:
        request.session.flush()

    return render(request, 'core/formulario.html', {
        'form': form,
        'mensaje_exito': mensaje_exito,
        'nombre': nombre,
        'active_tab': 'formulario',
    })


def actividades_view(request):
    """Vista para generar el reporte de actividades"""
    if not request.session.get('authenticated'):
        return redirect('login')

    nombre = request.session.get('usuario')

    if request.method == 'POST':
        form = ActividadesForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data

            tpl = settings.BASE_DIR / 'core' / 'plantillas' / 'reporte2.docx'
            doc = DocxTemplate(tpl)

            context = {
                'fecha': cd['fecha'],
                'nombre': cd['nombre'],
                'parque': cd['parque'],
                'resumen': cd.get('resumen', ''),
            }

            def mkimg(name):
                f = cd.get(name)
                if not f:
                    return None
                img = Image.open(f)
                img.thumbnail((int(120*11.8), int(105*11.8)))
                bio = BytesIO()
                img.save(bio, format=img.format or 'PNG')
                bio.seek(0)
                return InlineImage(doc, bio, width=Mm(120), height=Mm(105))

            photos = []
            for i in range(1,11):
                img = mkimg(f'registro_fotografico_{i}')
                if img:
                    photos.append(img)
            context['foto_adicional'] = photos

            doc.render(context)
            buf = BytesIO(); doc.save(buf); buf.seek(0)
            data = buf.getvalue()

            dest = cd.get('destinatario')
            if dest:
                mail = EmailMessage(
                    subject=f"Reporte actividades {cd['parque']} realizado por {cd['nombre']}",
                    body="Reporte adjunto",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[dest],
                )
                file_name = f"{cd['fecha'].strftime('%y-%m-%d')}_{cd['parque']}_{cd['nombre_archivo']}.docx"
                mail.attach(
                    filename=file_name,
                    content=data,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                send_email_async(mail)

            return redirect(f"{reverse('actividades')}?success=1")
    else:
        form = ActividadesForm()

    mensaje_exito = request.GET.get('success') == '1'
    if mensaje_exito:
        request.session.flush()

    return render(request, 'core/reporte_actividades.html', {
        'form': form,
        'mensaje_exito': mensaje_exito,
        'nombre': nombre,
        'active_tab': 'actividades',
    })
