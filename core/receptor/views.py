from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


COMANDOS = [
    ("INICIAR", "Iniciar", "btn-success", "player-play", ""),
    ("DETENER", "Detener", "btn-warning", "player-stop", "¿Cerrar el puerto? El emisor no podrá conectarse."),
    ("REINICIAR", "Reiniciar", "btn-primary", "refresh", ""),
    ("RESETEAR_CONTADORES", "Resetear contadores", "btn-outline-secondary", "eraser", "¿Poner los contadores en cero?"),
    ("APAGAR", "Apagar", "btn-danger", "power", "¿Apagar el proceso? Solo vuelve si lo levanta systemd."),
]
POR_PAGINA = 25


def _paginar(request, items):
    return Paginator(items, POR_PAGINA).get_page(request.GET.get("pagina"))


@login_required
def panel(request):
    contexto = {
        "estado": None,     # TODO: EstadoServicio.objects.first()
        "registros": [],    # TODO: Registro.objects.order_by("-recibido_en")[:10]
        "eventos": [],      # TODO: Evento.objects.all()[:8]
        "comandos_disponibles": COMANDOS,
    }
    return render(request, "panel.html", contexto)


@login_required
def registros(request):
    q = request.GET.get("q", "").strip()
    items = []  # TODO: Registro.objects.order_by("-recibido_en"), filtrado por crudo__icontains=q
    return render(request, "registros.html", {"pagina": _paginar(request, items), "q": q})


@login_required
def eventos(request):
    nivel = request.GET.get("nivel", "")
    if nivel not in ("INFO", "AVISO", "ERROR"):
        nivel = ""
    items = []  # TODO: Evento.objects.all(), filtrado por nivel si viene
    return render(request, "eventos.html", {"pagina": _paginar(request, items), "nivel": nivel})


@login_required
def comandos(request):
    items = []  # TODO: Comando.objects.all()
    return render(request, "comandos.html", {
        "pagina": _paginar(request, items),
        "comandos_disponibles": COMANDOS,
    })


@login_required
@require_POST
def enviar_comando(request):
    etiquetas = {c[0]: c[1] for c in COMANDOS}
    tipo = request.POST.get("tipo")
    if tipo not in etiquetas:
        messages.error(request, "Orden desconocida.")
    else:
        # TODO: Comando.objects.create(tipo=tipo, creado_por=request.user.get_username())
        messages.info(request, f"Orden «{etiquetas[tipo]}» recibida. Falta conectarla con el servicio.")
    volver = request.POST.get("volver")
    return redirect(volver if volver in ("panel", "comandos") else "panel")
