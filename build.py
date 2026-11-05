#!/usr/bin/env python3
"""Monta o site da Plancenter (início, quem somos, soluções, projetos, para quem, conteúdos com artigos, contato,
privacidade) e a ponte /obrigado para o WhatsApp.

    python3 build.py

A copy saiu dos 9 slides que a Karla mandou (OCR em _src/plancenter-ocr.txt), sem inventar serviço nem número.
O CSS vai minificado para dentro do <head>; o site.js leva o hash do conteúdo no nome.
"""
import hashlib, json, re
from datetime import date
from html import escape as e
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).parent
DOMINIO = "https://plancenter.vercel.app"
INDEXAR = False                 # True depois da aprovação
WHATSAPP = "5561993973723"      # +55 61 99397-3723, o dos slides
TEL_VER = "+55 61 99397-3723"
CSS, JS = RAIZ / "assets/css/site.css", RAIZ / "assets/js/site.js"

# ------------------------------------------------------------------ ícones (traço fino, 24x24)
I = {
    "ideia": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3z"/>',
    "planejamento": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 11h5M10 14h5M10 17h3"/>',
    "projeto": '<path d="M3 21V9l9-6 9 6v12z"/><path d="M9 21v-6h6v6M3 9h18"/>',
    "resultado": '<path d="M4 20h16M6 16l4-4 3 3 6-7"/><path d="M15 8h4v4"/>',
    "alvo": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".6" fill="currentColor"/>',
    "plano": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 16v-3M12 16V9M16 16v-5"/>',
    "camadas": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "pena": '<path d="M12 21l-4-8 4-10 4 10z"/><circle cx="12" cy="11" r="1.5"/><path d="M8 21h8"/>',
    "prancheta": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 10h6M9 14h6M9 18h3"/>',
    "aperto": '<path d="M3 12l4-4 4 2 4-2 6 6-6 4-3-2-3 2-6-6z"/><path d="M11 10l3 3"/>',
    "palestra": '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4M7 12l3-3 2 2 4-4"/>',
    "capelo": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
    "pessoa": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-4 4.5-6 8-6s7 2 8 6"/>',
    "olho": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "engrenagem": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    "grupo": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-3.5 3.3-5 6-5s5.2 1.5 6 5M15 15c2.4-.3 4.6.9 5.5 4"/>',
    "estrutura": '<rect x="9" y="3" width="6" height="5" rx="1"/><rect x="3" y="16" width="6" height="5" rx="1"/><rect x="15" y="16" width="6" height="5" rx="1"/><path d="M12 8v4M6 16v-4h12v4"/>',
    "seta": '<path d="M2 8h11M9 4l4 4-4 4"/>',
}


def ic(nome, vb="0 0 24 24"):
    return f'<svg viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[nome]}</svg>'


SETA = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5"/></svg>'
ZAP = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.6a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>')

# ------------------------------------------------------------------ utilidades
def zap(msg):
    return f"https://wa.me/{WHATSAPP}?text={quote(msg)}"


def minificar(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return re.sub(r"\n+", "", css).replace("../fonts/", "/assets/fonts/").strip()


def hash_de(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:10] if p.exists() else "0"


def foto(nome, larguras, alt, sizes, lazy=True, celular=None):
    """<img> (ou <picture> com a versão vertical do celular) a partir de assets/img/fotos/<nome>-<largura>.webp."""
    def dim(n, w):
        try:
            from PIL import Image
            with Image.open(RAIZ / f"assets/img/fotos/{n}-{w}.webp") as im:
                return im.size
        except Exception:
            print(f"  ! foto faltando: {n}-{w}.webp")
            return w, int(w * 9 / 16)
    w, h = dim(nome, larguras[-1])
    srcset = ", ".join(f"/assets/img/fotos/{nome}-{x}.webp {x}w" for x in larguras)
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    img = (f'<img src="/assets/img/fotos/{nome}-{larguras[-1]}.webp" srcset="{srcset}" sizes="{sizes}" alt="{e(alt)}" '
           f'width="{w}" height="{h}"{lz} decoding="async">')
    if not celular:
        return img
    nm, lm = celular
    dim(nm, lm[-1])
    src_m = ", ".join(f"/assets/img/fotos/{nm}-{x}.webp {x}w" for x in lm)
    return f'<picture><source media="(max-width:760px)" srcset="{src_m}" sizes="100vw">{img}</picture>'


def fundo(nome):
    """Imagem de fundo de seção (paisagem gerada no ChatGPT), com versão vertical no celular."""
    return f'<div class="fundo__bg" aria-hidden="true">{foto(nome, (1000, 1672), "", "100vw", celular=(nome + "-m", (700, 1122)))}</div>'


# ------------------------------------------------------------------ copy (briefing da cliente, 03/11 19:37 a 19:58)
EMAIL = "plancenterglobal@gmail.com"
MENU = [("Início", "/"), ("Quem Somos", "/quem-somos"), ("Soluções", "/solucoes"), ("Projetos", "/projetos"),
        ("Para Quem", "/para-quem"), ("Conteúdos", "/conteudos"), ("Contato", "/contato")]

FLUXO = [("ideia", "IDEIA"), ("planejamento", "PLANEJAMENTO"), ("projeto", "PROJETO"), ("resultado", "RESULTADO")]
SOLUCOES_HOME = [
    ("alvo", "Planejamento Estratégico", "Organização de objetivos, metas, estratégias e caminhos para o crescimento.", "planejamento"),
    ("plano", "Projetos e Planos de Negócios", "Elaboração e estruturação de projetos, planos de negócios e propostas técnicas.", "negocios"),
    ("pena", "Identidade Visual e Branding", "Desenvolvimento de marcas, posicionamento e identidade institucional.", "branding"),
    ("aperto", "Consultoria Empresarial", "Orientação para organização, gestão e desenvolvimento de negócios.", "consultoria"),
    ("prancheta", "Assessoria Administrativa", "Apoio na organização documental, administrativa e institucional.", "gestao"),
    ("capelo", "Mentoria e Capacitação", "Desenvolvimento de competências, liderança, gestão e planejamento.", "desenvolvimento"),
]
METODO = [("Diagnosticar", "Compreender a realidade e identificar necessidades."),
          ("Planejar", "Definir objetivos, estratégias e prioridades."),
          ("Estruturar", "Organizar ideias e desenvolver soluções."),
          ("Implementar", "Transformar o planejamento em ações."),
          ("Acompanhar", "Avaliar avanços e orientar os próximos passos.")]
PUBLICOS = [("pessoa", "Empreendedores e empresários."), ("plano", "Pequenas e médias empresas."),
            ("prancheta", "Profissionais e prestadores de serviços."), ("estrutura", "Instituições e organizações."),
            ("grupo", "Projetos sociais."), ("capelo", "Igrejas e ministérios.")]
QUEM_SOMOS = [
    "A PLANCENTER nasceu com o propósito de oferecer soluções de planejamento, consultoria e desenvolvimento de projetos para pessoas, empresas e instituições que desejam transformar suas ideias em realizações concretas.",
    "Acreditamos que boas ideias precisam de direção, organização e planejamento para alcançar resultados consistentes.",
    "Por isso, reunimos diferentes áreas de atuação em uma proposta integrada de atendimento, buscando compreender a realidade de cada cliente e desenvolver soluções adequadas às suas necessidades.",
    "Nossa atuação combina visão estratégica, organização, criatividade e compromisso com a excelência.",
]
MVV = [("NOSSA MISSÃO", "Transformar ideias em projetos estruturados e soluções estratégicas que contribuam para o desenvolvimento de negócios e instituições."),
       ("NOSSA VISÃO", "Ser reconhecida como referência em planejamento, consultoria e desenvolvimento estratégico.")]
VALORES = ["Excelência", "Ética", "Estratégia", "Inovação", "Compromisso", "Responsabilidade", "Resultados"]
PROJETOS_TIPOS = ["Projetos desenvolvidos", "Planos estratégicos", "Identidades visuais", "Projetos institucionais",
                  "Trabalhos de consultoria", "Capacitações e treinamentos"]
PROJETOS = []   # {"nome","cliente","desafio","solucao","entregas":[],"resultados"}: só com autorização do cliente
CATEGORIAS = ["Empreendedorismo", "Planejamento Estratégico", "Gestão Empresarial", "Desenvolvimento de Projetos",
              "Identidade Visual e Branding", "Liderança e Gestão", "Organização Institucional", "Gestão de Igrejas e Ministérios"]
AVISO = ("A PLANCENTER oferece planejamento e serviços técnicos conforme o escopo contratado. Não prometemos resultados "
         "financeiros, aprovação de projetos ou captação de recursos como garantia.")
ICONE_AREA = {"planejamento": "alvo", "negocios": "plano", "projetos": "camadas", "branding": "pena", "gestao": "prancheta",
              "consultoria": "aperto", "desenvolvimento": "capelo", "setor-religioso": "estrutura"}
NOS = [(10, 64.3), (30, 21.4), (50, 64.3), (70, 21.4), (90, 64.3)]  # y em % da faixa 40-180 do desenho
CAMINHO = "M0 160C50 160 60 130 100 130C160 130 220 70 300 70C380 70 420 130 500 130C580 130 620 70 700 70C780 70 820 130 900 130C950 130 970 110 1000 100"


def carregar_json(nome, padrao):
    p = RAIZ / "_src" / nome
    if p.exists():
        return json.loads(p.read_text())
    print(f"  ! ainda sem _src/{nome}")
    return padrao


def artigos():
    """Lê _src/artigos/*.md (front matter simples) e devolve a lista na ordem do briefing."""
    out = []
    for p in sorted((RAIZ / "_src/artigos").glob("*.md")):
        txt = p.read_text()
        m = re.match(r"---\n(.*?)\n---\n(.*)", txt, re.S)
        if not m:
            continue
        meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        meta["corpo"] = m.group(2).strip()
        meta.setdefault("slug", p.stem)
        out.append(meta)
    return out


def md(texto):
    """Markdown mínimo dos artigos: ##, ###, listas, negrito e parágrafos."""
    html, lista = [], None
    def inline(s):
        s = e(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    for bloco in re.split(r"\n\s*\n", texto):
        linhas = bloco.strip().splitlines()
        if not linhas:
            continue
        if all(re.match(r"^(\d+\.|[-*])\s", l) for l in linhas):
            tag = "ol" if re.match(r"^\d+\.", linhas[0]) else "ul"
            marcador = re.compile(r"^(\d+\.|[-*])\s+")
            itens = "".join("<li>" + inline(marcador.sub("", l)) + "</li>" for l in linhas)
            html.append(f"<{tag}>{itens}</{tag}>")
        elif linhas[0].startswith("### "):
            html.append(f"<h3>{inline(linhas[0][4:])}</h3>" + ("<p>" + inline(" ".join(linhas[1:])) + "</p>" if len(linhas) > 1 else ""))
        elif linhas[0].startswith("## "):
            html.append(f"<h2>{inline(linhas[0][3:])}</h2>" + ("<p>" + inline(" ".join(linhas[1:])) + "</p>" if len(linhas) > 1 else ""))
        else:
            html.append("<p>" + inline(" ".join(linhas)) + "</p>")
    return "\n".join(html)


def faq_de(corpo):
    """Perguntas frequentes do fim do artigo, para o FAQPage do schema."""
    if "## Perguntas frequentes" not in corpo:
        return []
    parte = corpo.split("## Perguntas frequentes", 1)[1]
    pares = re.findall(r"###\s+(.+?)\n+(.+?)(?=\n###|\Z)", parte, re.S)
    return [(q.strip(), re.sub(r"\s+", " ", a).strip()) for q, a in pares]


# ------------------------------------------------------------------ casca
def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


def org_schema():
    sol = carregar_json("solucoes.json", [])
    return ld({
        "@context": "https://schema.org", "@type": "ProfessionalService", "name": "Plancenter",
        "alternateName": "Plancenter Consultoria & Projetos", "slogan": "Onde suas ideias se transformam em projetos bem-sucedidos.",
        "description": "Centro de planejamento, consultoria e desenvolvimento de projetos para empreendedores, empresas, instituições, projetos sociais e igrejas e ministérios.",
        "url": DOMINIO + "/", "logo": DOMINIO + "/assets/img/plancenter-completa.webp", "image": DOMINIO + "/assets/img/og-image.jpg",
        "telephone": "+55-61-99397-3723", "email": EMAIL, "areaServed": "BR",
        "founder": {"@type": "Person", "name": "Karla Messias", "jobTitle": "Fundadora", "url": "https://karlamessias.vercel.app/"},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Soluções Plancenter", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["servico"], "description": s["descricao"]}} for s in sol]},
    })


def migalhas(rota, nome):
    if rota == "/":
        return ""
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": DOMINIO + "/"},
        {"@type": "ListItem", "position": 2, "name": nome, "item": DOMINIO + rota}]})


def pagina(titulo, desc, corpo, rota="/", preload="", robots=None, casca=True, extra_ld="", nome_rota=""):
    robots = robots or ("index,follow" if INDEXAR else "noindex,nofollow")
    itens = "".join(f'<a href="{h}"{" aria-current=page" if h == rota or (h != "/" and rota.startswith(h)) else ""}>{n}</a>' for n, h in MENU)
    topo = f'''<header class="top"><div class="wrap top__in">
  <a class="marca" href="/" aria-label="Plancenter, início"><img src="/assets/img/plancenter.webp" alt="Plancenter" width="640" height="406"></a>
  <nav class="nav" id="nav" aria-label="Principal">{itens}<a class="btn btn--ouro" href="/obrigado?c=topo">Solicite uma consultoria</a></nav>
  <button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
</div></header>''' if casca else ""
    rodape = f'''<footer class="rod"><div class="wrap">
  <div class="rod__grid">
    <div class="rod__marca"><img src="/assets/img/plancenter-completa.webp" alt="Plancenter Consultoria &amp; Projetos" width="640" height="444" loading="lazy"><p class="rod__frase">Onde suas ideias se transformam em projetos bem-sucedidos.</p></div>
    <div class="rod__links">{"".join(f'<a href="{h}">{n}</a>' for n, h in MENU[1:])}</div>
    <div class="rod__links"><a href="{zap("Olá! Vim pelo site da Plancenter.")}" target="_blank" rel="noopener">WhatsApp {TEL_VER}</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="/privacidade">Política de privacidade</a></div>
  </div>
  <p class="rod__fim">© {date.today().year} Plancenter Consultoria &amp; Projetos. Todos os direitos reservados.</p>
</div></footer>
<a class="zap" href="/obrigado?c=flutuante" aria-label="Falar pelo WhatsApp">{ZAP}</a>''' if casca else ""
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{DOMINIO}{rota}">
<meta name="theme-color" content="#070B16">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Plancenter">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{DOMINIO}{rota}">
<meta property="og:image" content="{DOMINIO}/assets/img/og-image.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/favicon.png" type="image/png"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/poppins-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<script>document.documentElement.classList.add('js')</script>
<style>{minificar(CSS.read_text())}</style>
{org_schema() if rota == "/" else ""}{migalhas(rota, nome_rota)}{extra_ld}
</head>
<body>
{topo}
<main>
{corpo}
</main>
{rodape}
<script src="/assets/js/site.js?v={hash_de(JS)}" defer></script>
</body>
</html>'''


def pag_topo(titulo, texto="", img="cume", ctas=""):
    p = f"<p>{e(texto)}</p>" if texto else ""
    return (f'<section class="pagtopo fundo">{fundo(img)}<div class="wrap"><div class="pagtopo__txt">'
            f'<h1>{titulo}</h1>{p}{ctas}</div></div></section>')


def cta_final(titulo, texto, rotulo="Fale com a Plancenter"):
    return f'''<section class="sec fundo" id="contato">{fundo("aurora")}<div class="wrap"><div class="final final--centro rv">
  <h2>{titulo}</h2><p>{e(texto)}</p>
  <div class="ctas"><a class="btn btn--ouro" href="/obrigado?c=cta">{e(rotulo)} {SETA}</a><a class="btn btn--linha" href="/contato">Preencher o formulário</a></div>
  <a class="tel" href="/obrigado?c=telefone">{ZAP} {TEL_VER}</a>
</div></div></section>'''


def metodo_sec():
    nos = "".join(f'<span class="no-html" style="left:{x}%;top:{y}%"></span>' for x, y in NOS)
    passos = "".join(f'<div class="passo" data-passo="{i}"><span class="passo__n">{i+1}</span><h3>{e(t.upper())}</h3><p>{e(d)}</p></div>'
                     for i, (t, d) in enumerate(METODO))
    return f'''<section class="metodo" id="metodo">
  <div class="metodo__bg">{foto("caminho", (1000, 1672), "", "100vw", celular=("caminho-m", (700, 1122)))}</div>
  <div class="metodo__palco"><div class="wrap">
    <div class="cab"><h2>Não entregamos apenas um serviço. <span class="ouro">Construímos um caminho.</span></h2></div>
    <div class="estrada" aria-hidden="true">
      <svg viewBox="0 40 1000 140"><defs><linearGradient id="gradOuro" x1="0" x2="1"><stop offset="0" stop-color="#9C7224"/><stop offset=".5" stop-color="#F2D48A"/><stop offset="1" stop-color="#D4A853"/></linearGradient></defs>
        <path class="base" d="{CAMINHO}"/><path class="ouro-l" d="{CAMINHO}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/></svg>
      {nos}
    </div>
    <div class="passos">{passos}</div>
    <p class="frase">Método Plancenter: <b class="ouro">estratégia do início ao resultado.</b></p>
  </div></div>
</section>'''


def fundadora_sec(completa=False):
    txt = ('<p>Fundadora da PLANCENTER.</p><p>Administradora, consultora e mentora estratégica, com atuação também nas áreas de psicanálise clínica e teologia.</p>'
           '<p class="fundadora__lema">Visão estratégica, experiência e propósito.</p>')
    return f'''<section class="sec" id="fundadora"><div class="wrap par par--fund">
  <div class="foto foto--retrato rv">{foto("fundadora", (800, 1400), "Karla Messias, fundadora da Plancenter, apresentando um plano de negócios", "(max-width:760px) 92vw, 40vw")}</div>
  <div class="par__txt rv" data-d="1"><h2>Karla <span class="ouro">Messias</span></h2>{txt}
    <div class="ctas" style="margin-top:2rem"><a class="btn btn--linha" href="https://karlamessias.vercel.app/" target="_blank" rel="noopener">Conheça Karla Messias {SETA}</a></div></div>
</div></section>'''


# ------------------------------------------------------------------ páginas
def home():
    fluxo = "".join(f'<div class="etapa" data-etapa="{i}"><div class="etapa__ic">{ic(k)}</div><h3>{t}</h3></div>' for i, (k, t) in enumerate(FLUXO))
    sol = "".join(f'<a class="sol rv" data-d="{i % 3}" href="/solucoes#{slug}">{ic(k)}<h3>{e(t)}</h3><p>{e(d)}</p></a>'
                  for i, (k, t, d, slug) in enumerate(SOLUCOES_HOME))
    pub = "".join(f'<a class="rv" data-d="{i % 3}" href="/para-quem">{ic(k)}<h3>{e(t.rstrip("."))}</h3></a>' for i, (k, t) in enumerate(PUBLICOS))
    corpo = f'''
<section class="capa" id="inicio">
  <div class="capa__bg" data-paralaxe>{foto("hero", (1000, 1672), "Escritório executivo com vista para a cidade ao pôr do sol", "100vw", lazy=False, celular=("hero-m", (700, 1122)))}</div>
  <div class="wrap"><div class="capa__txt">
    <h1>Sua ideia merece um planejamento <span class="ouro">à altura do seu potencial.</span></h1>
    <p class="capa__txt-p">Transformamos ideias em estratégias, projetos e soluções para o desenvolvimento de negócios e instituições.</p>
    <div class="ctas"><a class="btn btn--ouro" href="/solucoes">Conheça nossas soluções {SETA}</a><a class="btn btn--linha" href="/obrigado?c=hero">Fale com um consultor</a></div>
  </div></div>
  <span class="capa__linha" aria-hidden="true"></span>
</section>

<section class="sec" id="apresentacao"><div class="wrap">
  <div class="cab rv"><h2>Mais do que consultoria. <span class="ouro">Estratégia para transformar ideias em resultados.</span></h2>
    <p>A PLANCENTER é um centro de planejamento, consultoria e desenvolvimento de projetos que conecta visão estratégica, organização e execução.</p>
    <p>Trabalhamos para ajudar empreendedores, empresas e instituições a desenvolverem suas ideias com planejamento, profissionalismo e direção.</p></div>
  <div class="fluxo" data-fluxo><div class="fluxo__trilho" aria-hidden="true"><i></i></div>{fluxo}</div>
</div></section>

<section class="sec fundo" id="solucoes">{fundo("rede")}<div class="wrap">
  <div class="cab rv"><h2>Nossas <span class="ouro">soluções.</span></h2></div>
  <div class="solucoes solucoes--3">{sol}</div>
  <div class="fim"><a class="btn btn--linha" href="/solucoes">Ver todas as soluções {SETA}</a></div>
</div></section>

{metodo_sec()}

<section class="sec fundo fundo--claro" id="para-quem">{fundo("cume")}<div class="wrap">
  <div class="cab rv"><h2>Para quem <span class="ouro">trabalhamos.</span></h2></div>
  <div class="porque">{pub}</div>
</div></section>

{fundadora_sec()}

{cta_final('Qual é o próximo passo <span class="ouro">do seu negócio?</span>', "Não importa se você está começando, reorganizando ou planejando crescer. A PLANCENTER pode ajudar você a construir o próximo passo.")}'''
    pre = ('<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="/assets/img/fotos/hero-1000.webp 1000w, /assets/img/fotos/hero-1672.webp 1672w" imagesizes="100vw" fetchpriority="high">\n'
           '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="/assets/img/fotos/hero-m-700.webp 700w, /assets/img/fotos/hero-m-1122.webp 1122w" imagesizes="100vw" fetchpriority="high">')
    return pagina("Plancenter | Planejamento, consultoria e desenvolvimento de projetos",
                  "Plancenter Consultoria & Projetos: planejamento estratégico, planos de negócios, projetos, branding, assessoria administrativa, consultoria e mentoria para empresas e instituições.",
                  corpo, "/", pre)


def quem_somos():
    txt = "".join(f"<p>{e(p)}</p>" for p in QUEM_SOMOS)
    mvv = "".join(f'<div class="mvv__item rv" data-d="{i}"><h3>{t}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(MVV))
    valores = "".join(f"<span>{v}</span><i></i>" for v in VALORES)
    corpo = f'''{pag_topo('Planejamento, estratégia <span class="ouro">e desenvolvimento.</span>', img="rede")}
<section class="sec"><div class="wrap texto rv">{txt}</div></section>
<section class="sec sec--2"><div class="wrap">
  <div class="mvv mvv--2">{mvv}</div>
  <div class="cab rv" style="margin:clamp(3rem,6vw,4.5rem) auto 0"><h2>Nossos <span class="ouro">valores.</span></h2></div>
  <div class="valores" aria-label="{e(", ".join(VALORES))}"><div class="valores__t" aria-hidden="true">{valores * 4}</div></div>
</div></section>
{fundadora_sec()}
{cta_final('Vamos construir <span class="ouro">o próximo passo?</span>', "Conte sua ideia ou o desafio da sua empresa ou instituição. Vamos analisar como podemos ajudar.")}'''
    return pagina("Quem somos | Plancenter", "A PLANCENTER nasceu para oferecer planejamento, consultoria e desenvolvimento de projetos a pessoas, empresas e instituições. Missão, visão e valores.",
                  corpo, "/quem-somos", nome_rota="Quem Somos")


def solucoes():
    sol = carregar_json("solucoes.json", [])
    chips = "".join(f'<a href="#{s["slug"]}">{e(s["area"])}</a>' for s in sol)
    blocos = []
    for i, s in enumerate(sol):
        icone = ic(ICONE_AREA.get(s["slug"], "alvo"))
        para = "".join(f"<li>{e(x)}</li>" for x in s.get("para_quem", []))
        ent = "".join(f"<li>{e(x)}</li>" for x in s.get("entregas", []))
        img = ""
        if s["slug"] == "setor-religioso":
            img = f'<div class="foto rv" style="margin-top:2rem">{foto("ministerio", (900, 1536), "Mesa de planejamento com Bíblia e documentos", "(max-width:760px) 92vw, 40vw")}</div>'
        blocos.append(f'''<article class="area{" area--alt" if i % 2 else ""}" id="{s["slug"]}"><div class="wrap area__grid">
  <div class="area__cab rv"><span class="area__ic">{icone}</span><h2>{e(s["area"])}</h2><p class="area__serv">{e(s["servico"])}</p><p>{e(s["descricao"])}</p>{img}</div>
  <div class="area__corpo rv" data-d="1">
    <div class="area__bloco"><h3>Problema que resolve</h3><p>{e(s["problema"])}</p></div>
    <div class="area__bloco"><h3>Para quem é indicado</h3><ul>{para}</ul></div>
    <div class="area__bloco"><h3>O que pode ser entregue</h3><ul>{ent}</ul></div>
    <div class="area__bloco"><h3>Como solicitar orçamento</h3><p>{e(s["orcamento"])}</p>
      <a class="btn btn--ouro" href="{zap("Olá! Quero um orçamento de " + s["area"] + " (" + s["servico"] + ").")}" target="_blank" rel="noopener">Solicitar orçamento {SETA}</a></div>
  </div>
</div></article>''')
    corpo = f'''{pag_topo('Soluções para cada etapa <span class="ouro">da sua ideia.</span>', "Planejamento, negócios, projetos, branding, gestão, consultoria, desenvolvimento e setor religioso.", "rede")}
<nav class="chips wrap" aria-label="Áreas">{chips}</nav>
{"".join(blocos)}
<section class="sec"><div class="wrap"><p class="aviso rv">{e(AVISO)}</p></div></section>
{cta_final('Não sabe por onde <span class="ouro">começar?</span>', "Conte o que você precisa. Na conversa inicial, entendemos o cenário e indicamos a solução mais adequada.")}'''
    return pagina("Soluções | Plancenter: planejamento, projetos, branding e consultoria",
                  "Planejamento estratégico, plano de negócios, projetos técnicos e institucionais, identidade visual, assessoria administrativa, consultoria, mentoria e planejamento para igrejas.",
                  corpo, "/solucoes", nome_rota="Soluções")


def projetos():
    tipos = "".join(f'<div class="sol rv" data-d="{i % 3}">{ic(["camadas", "alvo", "pena", "estrutura", "aperto", "capelo"][i])}<h3>{e(t)}</h3></div>' for i, t in enumerate(PROJETOS_TIPOS))
    corpo = f'''{pag_topo('Ideias que ganham forma. <span class="ouro">Projetos que ganham direção.</span>', img="caminho")}
<section class="sec"><div class="wrap">
  <div class="cab rv"><h2>O que você vai encontrar <span class="ouro">aqui.</span></h2><p>Os cases são publicados com a autorização de cada cliente, com o desafio, a solução desenvolvida, as entregas e os resultados documentados.</p></div>
  <div class="solucoes solucoes--3">{tipos}</div>
  <div class="vazio rv"><h3>Os primeiros cases estão sendo organizados.</h3><p>Enquanto isso, fale com a gente sobre o seu projeto.</p><div class="ctas"><a class="btn btn--ouro" href="/obrigado?c=projetos">Falar sobre o meu projeto {SETA}</a></div></div>
</div></section>'''
    return pagina("Projetos | Plancenter", "Projetos, planos estratégicos, identidades visuais, projetos institucionais, consultorias e capacitações desenvolvidos pela Plancenter.",
                  corpo, "/projetos", nome_rota="Projetos")


def para_quem():
    pq = carregar_json("para_quem.json", [])
    sol = {s["slug"]: s["area"] for s in carregar_json("solucoes.json", [])}
    icones = {p[1].rstrip("."): p[0] for p in PUBLICOS}
    itens = []
    for i, p in enumerate(pq):
        links = "".join(f'<a href="/solucoes#{s}">{e(sol.get(s, s))}</a>' for s in p.get("solucoes", []))
        itens.append(f'<article class="publico rv" data-d="{i % 2}"><span class="area__ic">{ic(icones.get(p["publico"].rstrip("."), "pessoa"))}</span>'
                     f'<h2>{e(p["publico"].rstrip("."))}</h2><p>{e(p["texto"])}</p><div class="publico__sol">{links}</div></article>')
    corpo = f'''{pag_topo('Para quem <span class="ouro">trabalhamos.</span>', "Do empreendedor que está começando à instituição que precisa se organizar.", "cume")}
<section class="sec"><div class="wrap"><div class="publicos">{"".join(itens)}</div></div></section>
{cta_final('Seu caso não está <span class="ouro">na lista?</span>', "Conte sua necessidade. Vamos analisar como podemos ajudar.")}'''
    return pagina("Para quem | Plancenter", "Empreendedores, pequenas e médias empresas, profissionais, instituições, projetos sociais e igrejas e ministérios.",
                  corpo, "/para-quem", nome_rota="Para Quem")


def conteudos(lista):
    cats = "".join(f"<li>{e(c)}</li>" for c in CATEGORIAS)
    cards = "".join(f'<a class="post rv" data-d="{i % 3}" href="/conteudos/{a["slug"]}"><span class="post__cat">{e(a.get("categoria", ""))}</span>'
                    f'<h3>{e(a["titulo"])}</h3><p>{e(a.get("resumo", ""))}</p><span class="post__ler">Ler artigo · {e(a.get("leitura", ""))} {SETA}</span></a>'
                    for i, a in enumerate(lista))
    corpo = f'''{pag_topo('Conteúdos para quem <span class="ouro">planeja crescer.</span>', "Artigos sobre empreendedorismo, planejamento, gestão, projetos, branding e organização institucional.", "rede")}
<section class="sec"><div class="wrap"><ul class="docs docs--centro rv">{cats}</ul><div class="posts">{cards}</div></div></section>'''
    return pagina("Conteúdos | Plancenter", "Artigos da Plancenter sobre planejamento estratégico, plano de negócios, projetos institucionais, branding e organização de empresas e instituições.",
                  corpo, "/conteudos", nome_rota="Conteúdos")


def artigo_pag(a, lista):
    faq = faq_de(a["corpo"])
    extra = ld({"@context": "https://schema.org", "@type": "Article", "headline": a["titulo"], "description": a.get("resumo", ""),
                "inLanguage": "pt-BR", "author": {"@type": "Organization", "name": "Plancenter"},
                "publisher": {"@type": "Organization", "name": "Plancenter", "logo": {"@type": "ImageObject", "url": DOMINIO + "/assets/img/plancenter-completa.webp"}},
                "mainEntityOfPage": f"{DOMINIO}/conteudos/{a['slug']}", "datePublished": "2026-11-03"})
    if faq:
        extra += ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]})
    outros = "".join(f'<a href="/conteudos/{o["slug"]}">{e(o["titulo"])}</a>' for o in lista if o["slug"] != a["slug"])[:4000]
    corpo = f'''<article class="artigo"><div class="wrap artigo__wrap">
  <nav class="trilha" aria-label="Você está em"><a href="/">Início</a> / <a href="/conteudos">Conteúdos</a></nav>
  <span class="post__cat">{e(a.get("categoria", ""))}</span>
  <h1>{e(a["titulo"])}</h1>
  <p class="artigo__resumo">{e(a.get("resumo", ""))}</p>
  <div class="artigo__corpo">{md(a["corpo"])}</div>
  <div class="final final--centro" style="margin-top:3rem"><h2>Quer ajuda com <span class="ouro">o seu caso?</span></h2><p>Conte sua necessidade. Vamos analisar como podemos ajudar.</p>
    <div class="ctas"><a class="btn btn--ouro" href="/obrigado?c=artigo">Fale com a Plancenter {SETA}</a></div></div>
  <div class="artigo__mais"><h2>Leia também</h2>{outros}</div>
</div></article>'''
    return pagina(f'{a["titulo"]} | Plancenter', a.get("resumo", ""), corpo, f'/conteudos/{a["slug"]}', extra_ld=extra, nome_rota=a["titulo"])


def contato():
    sol = carregar_json("solucoes.json", [])
    ops = "".join(f"<option>{e(s['area'])}</option>" for s in sol) + "<option>Ainda não sei</option>"
    corpo = f'''{pag_topo('Fale com a <span class="ouro">Plancenter.</span>', "Estamos prontos para conhecer sua necessidade e identificar como podemos ajudar.", "aurora")}
<section class="sec"><div class="wrap"><div class="final"><div class="final__grid">
  <div>
    <h2>Solicite seu <span class="ouro">atendimento.</span></h2>
    <p>Preencha o formulário e a mensagem chega pronta no nosso WhatsApp. Se preferir, fale direto pelos canais abaixo.</p>
    <a class="tel" href="/obrigado?c=telefone">{ZAP} {TEL_VER}</a>
    <a class="tel tel--mail" href="mailto:{EMAIL}">{EMAIL}</a>
  </div>
  <form class="form" data-form novalidate>
    <div class="campo campo--cheio"><label for="f-nome">Nome completo</label><input id="f-nome" name="Nome completo" autocomplete="name" required></div>
    <div class="campo campo--cheio"><label for="f-emp">Nome da empresa ou instituição</label><input id="f-emp" name="Empresa ou instituição" autocomplete="organization"></div>
    <div class="campo"><label for="f-zap">WhatsApp</label><input id="f-zap" name="WhatsApp" type="tel" inputmode="tel" autocomplete="tel" required></div>
    <div class="campo"><label for="f-mail">E-mail</label><input id="f-mail" name="E-mail" type="email" autocomplete="email" required></div>
    <div class="campo"><label for="f-cid">Cidade e estado</label><input id="f-cid" name="Cidade e estado" autocomplete="address-level2" required></div>
    <div class="campo"><label for="f-serv">Serviço de interesse</label><select id="f-serv" name="Serviço de interesse" required><option value="" disabled selected>Escolha</option>{ops}</select></div>
    <div class="campo campo--cheio"><label for="f-msg">Descrição da necessidade</label><textarea id="f-msg" name="Necessidade" rows="3" required></textarea></div>
    <div class="form__mel" aria-hidden="true"><input name="site" tabindex="-1" autocomplete="off"></div>
    <label class="aceite"><input type="checkbox" name="aceite" required> Concordo com o uso dos meus dados para receber o retorno da Plancenter, conforme a <a href="/privacidade">Política de Privacidade</a> (LGPD).</label>
    <button class="btn btn--ouro" type="submit">Enviar {SETA}</button>
  </form>
</div></div></div></section>'''
    return pagina("Contato | Plancenter", f"Fale com a Plancenter pelo WhatsApp {TEL_VER}, pelo e-mail {EMAIL} ou pelo formulário de atendimento.",
                  corpo, "/contato", nome_rota="Contato")


def privacidade():
    corpo = f'''{pag_topo("Política de Privacidade", "Como os seus dados são tratados neste site, conforme a LGPD (Lei 13.709/2018).", "aurora")}
<section class="sec"><div class="wrap texto">
<h2>Quem cuida dos seus dados</h2><p>Este site é da Plancenter Consultoria &amp; Projetos, responsável pelo tratamento dos dados enviados por meio dele.</p>
<h2>Que dados recebemos</h2><p>Apenas os que você digita no formulário: nome, empresa ou instituição, WhatsApp, e-mail, cidade e estado, serviço de interesse e a descrição da sua necessidade.</p>
<h2>Para que usamos</h2><p>Para responder ao seu pedido de atendimento e enviar as informações que você solicitou. Não vendemos nem compartilhamos seus dados para fins comerciais.</p>
<h2>Como a mensagem chega até nós</h2><p>Ao enviar o formulário, a mensagem é aberta no WhatsApp, já preenchida, para que você a envie à Plancenter. O WhatsApp tem a sua própria política de privacidade.</p>
<h2>Cookies</h2><p>Este site não usa cookies de publicidade nem de rastreamento. Se ferramentas de medição forem adicionadas, você será avisado.</p>
<h2>Seus direitos</h2><p>Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento pelo e-mail {EMAIL} ou pelo WhatsApp {TEL_VER}.</p>
</div></section>'''
    return pagina("Política de Privacidade | Plancenter", "Política de privacidade e tratamento de dados (LGPD) da Plancenter.", corpo, "/privacidade", nome_rota="Privacidade")


def obrigado():
    corpo = f'''<section class="obrigado"><div>
  <img src="/assets/img/plancenter.webp" alt="Plancenter" width="640" height="406">
  <h1>Estamos abrindo <span class="ouro">a conversa.</span></h1>
  <p>Em instantes você fala com a Plancenter pelo WhatsApp.</p>
  <div class="gira" aria-hidden="true"></div>
  <div class="ctas"><a class="btn btn--ouro" id="vai" href="https://wa.me/{WHATSAPP}">Abrir o WhatsApp {SETA}</a><a class="btn btn--linha" href="/">Voltar</a></div>
</div></section>
<script>
(function(){{
  var W='{WHATSAPP}', msg='Olá! Vim pelo site da Plancenter e quero solicitar um atendimento.';
  try{{ msg=sessionStorage.getItem('pc_msg')||msg; sessionStorage.removeItem('pc_msg'); }}catch(e){{}}
  var dest='https://wa.me/'+W+'?text='+encodeURIComponent(msg); document.getElementById('vai').href=dest;
  var c=(new URLSearchParams(location.search).get('c')||'site').replace(/[^a-z0-9_-]/gi,'');
  var t0=Date.now(), partiu=false;
  function vai(){{ if(partiu) return; partiu=true; location.replace(dest); }}
  function talvez(){{ var f=900-(Date.now()-t0); setTimeout(vai, f>0?f:0); }}
  window.dataLayer=window.dataLayer||[]; window.dataLayer.push({{event:'conversao_whatsapp',contexto:c,eventCallback:talvez,eventTimeout:2000}});
  if(!window.google_tag_manager) talvez();
  setTimeout(vai,2600);
}})();
</script>'''
    return pagina("Abrindo a conversa | Plancenter", "Abrindo o WhatsApp da Plancenter.", corpo, "/obrigado", robots="noindex,nofollow", casca=False)


def main():
    lista = artigos()
    paginas = {"index.html": home(), "quem-somos.html": quem_somos(), "solucoes.html": solucoes(), "projetos.html": projetos(),
               "para-quem.html": para_quem(), "conteudos/index.html": conteudos(lista), "contato.html": contato(),
               "privacidade.html": privacidade(), "obrigado.html": obrigado()}
    for a in lista:
        paginas[f"conteudos/{a['slug']}.html"] = artigo_pag(a, lista)
    for arq, html in paginas.items():
        p = RAIZ / arq
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html)
    rotas = ["/"] + [h for _, h in MENU[1:]] + [f"/conteudos/{a['slug']}" for a in lista] + ["/privacidade"]
    hoje = date.today().isoformat()
    (RAIZ / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoje}</lastmod></url>" for r in rotas) + "</urlset>\n")
    (RAIZ / "robots.txt").write_text("User-agent: *\n" + ("Allow: /\n" if INDEXAR else "Disallow:\n") + f"\nSitemap: {DOMINIO}/sitemap.xml\n")
    sol = carregar_json("solucoes.json", [])
    (RAIZ / "llms.txt").write_text("# Plancenter Consultoria & Projetos\n\n> Centro de planejamento, consultoria e desenvolvimento de projetos que conecta visão estratégica, organização e execução. Fundadora: Karla Messias.\n\n## Soluções\n"
        + "\n".join(f"- {s['area']}: {s['servico']}. {s['descricao']}" for s in sol)
        + "\n\n## Método Plancenter\n" + "\n".join(f"{i+1}. {t}: {d}" for i, (t, d) in enumerate(METODO))
        + "\n\n## Para quem\n" + "\n".join(f"- {t.rstrip('.')}" for _, t in PUBLICOS)
        + "\n\n## Artigos\n" + "\n".join(f"- [{a['titulo']}]({DOMINIO}/conteudos/{a['slug']}): {a.get('resumo','')}" for a in lista)
        + f"\n\n## Aviso\n{AVISO}\n\n## Contato\nWhatsApp: {TEL_VER}\nE-mail: {EMAIL}\nSite: {DOMINIO}/\n")
    print(f"  {len(paginas)} páginas ({len(lista)} artigos)  site.js v={hash_de(JS)}  indexar={INDEXAR}")


if __name__ == "__main__":
    main()
