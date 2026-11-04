#!/usr/bin/env python3
"""Monta a landing da Plancenter (index.html) e a ponte /obrigado para o WhatsApp.

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

# ------------------------------------------------------------------ copy (dos slides)
FLUXO = [("ideia", "IDEIA"), ("planejamento", "PLANEJAMENTO"), ("projeto", "PROJETO"), ("resultado", "RESULTADO")]
SOLUCOES = [("alvo", "Planejamento estratégico"), ("plano", "Business plan"), ("camadas", "Projetos"), ("pena", "Identidade visual"),
            ("prancheta", "Assessoria administrativa"), ("aperto", "Consultoria empresarial"), ("palestra", "Mentoria estratégica"),
            ("capelo", "Capacitação e treinamentos")]
METODO = [("Diagnosticar", "Entendemos sua realidade, desafios e objetivos."),
          ("Planejar", "Definimos estratégias personalizadas para o seu propósito."),
          ("Estruturar", "Organizamos processos, projetos e recursos."),
          ("Implementar", "Apoiamos a execução com método e orientação."),
          ("Acompanhar", "Monitoramos resultados e caminhamos com você até a conquista.")]
MVV = [("MISSÃO", "Transformar ideias em projetos estruturados e sustentáveis."),
       ("VISÃO", "Ser referência em planejamento, consultoria e desenvolvimento estratégico."),
       ("VALORES", "Excelência, ética, estratégia, inovação, compromisso e resultados.")]
VALORES = ["Excelência", "Ética", "Estratégia", "Inovação", "Compromisso", "Resultados"]
PORQUE = [("pessoa", "Atendimento personalizado"), ("olho", "Visão estratégica"), ("engrenagem", "Soluções integradas"),
          ("planejamento", "Planejamento profissional"), ("grupo", "Acompanhamento"), ("resultado", "Foco em resultados")]
DOCS = ["Estatuto social", "Regimento interno", "Atas", "Plano de trabalho", "Plano estratégico"]
FRENTES = [("planejamento", "Planejamento"), ("engrenagem", "Gestão"), ("camadas", "Projetos"), ("estrutura", "Estruturação"), ("capelo", "Capacitação")]
# posição de cada etapa no caminho (x e y em % do desenho), na mesma ordem do método
NOS = [(10, 64.3), (30, 21.4), (50, 64.3), (70, 21.4), (90, 64.3)]  # y em % da faixa 40-180 do desenho
CAMINHO = "M0 160C50 160 60 130 100 130C160 130 220 70 300 70C380 70 420 130 500 130C580 130 620 70 700 70C780 70 820 130 900 130C950 130 970 110 1000 100"


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


def schema():
    org = {
        "@context": "https://schema.org", "@type": "ProfessionalService", "name": "Plancenter",
        "alternateName": "Plancenter Consultoria & Projetos", "slogan": "Onde suas ideias se transformam em projetos bem-sucedidos.",
        "description": "Soluções em planejamento, projetos, gestão, consultoria, branding, mentoria e capacitação, para empresas, projetos e igrejas e ministérios.",
        "url": DOMINIO + "/", "logo": DOMINIO + "/assets/img/plancenter-completa.webp", "image": DOMINIO + "/assets/img/og-image.jpg",
        "telephone": "+55-61-99397-3723", "areaServed": "BR",
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Soluções Plancenter", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for _, n in SOLUCOES]
            + [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Consultoria e assessoria para igrejas e ministérios"}}]},
    }
    return f'<script type="application/ld+json">{json.dumps(org, ensure_ascii=False, separators=(",", ":"))}</script>'


def pagina(titulo, desc, corpo, rota="/", preload="", robots=None, casca=True):
    robots = robots or ("index,follow" if INDEXAR else "noindex,nofollow")
    topo = f'''<header class="top"><div class="wrap top__in">
  <a class="marca" href="/" aria-label="Plancenter, início"><img src="/assets/img/plancenter.webp" alt="Plancenter" width="640" height="406"></a>
  <nav class="nav" id="nav" aria-label="Principal"><a href="#solucoes">Soluções</a><a href="#metodo">Método</a><a href="#ministerios">Igrejas e ministérios</a><a href="#contato">Contato</a>
    <a class="btn btn--ouro" href="/obrigado?c=topo">Solicite seu atendimento</a></nav>
  <button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
</div></header>''' if casca else ""
    rodape = f'''<footer class="rod"><div class="wrap">
  <div class="rod__grid">
    <div class="rod__marca"><img src="/assets/img/plancenter-completa.webp" alt="Plancenter Consultoria &amp; Projetos" width="640" height="444" loading="lazy"><p class="rod__frase">Onde suas ideias se transformam em projetos bem-sucedidos.</p></div>
    <div class="rod__links"><a href="{zap("Olá! Vim pelo site da Plancenter.")}" target="_blank" rel="noopener">WhatsApp {TEL_VER}</a><a href="#solucoes">Soluções</a><a href="#metodo">Método Plancenter</a><a href="#ministerios">Igrejas e ministérios</a></div>
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
{schema() if rota == "/" else ""}
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


def home():
    fluxo = "".join(f'<div class="etapa" data-etapa="{i}"><div class="etapa__ic">{ic(k)}</div><h3>{t}</h3></div>' for i, (k, t) in enumerate(FLUXO))
    solucoes = "".join(f'<div class="sol rv" data-d="{i % 4}">{ic(k)}<h3>{e(t)}</h3></div>' for i, (k, t) in enumerate(SOLUCOES))
    nos = "".join(f'<span class="no-html" style="left:{x}%;top:{y}%"></span>' for x, y in NOS)
    nos_svg = ""
    passos = "".join(f'<div class="passo" data-passo="{i}"><span class="passo__n">{i+1}</span><h3>{e(t.upper())}</h3><p>{e(d)}</p></div>'
                     for i, (t, d) in enumerate(METODO))
    mvv = "".join(f'<div class="mvv__item rv" data-d="{i}"><h3>{t}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(MVV))
    valores = "".join(f"<span>{v}</span><i></i>" for v in VALORES)
    porque = "".join(f'<div class="rv" data-d="{i % 3}">{ic(k)}<h3>{e(t)}</h3></div>' for i, (k, t) in enumerate(PORQUE))
    docs = "".join(f"<li>{e(d)}</li>" for d in DOCS)
    frentes = "".join(f"<li>{ic(k)}{e(t)}</li>" for k, t in FRENTES)
    corpo = f'''
<section class="capa" id="inicio">
  <div class="capa__bg" data-paralaxe>{foto("hero", (1000, 1672), "Escritório executivo com vista para a cidade ao pôr do sol", "100vw", lazy=False, celular=("hero-m", (700, 1122)))}</div>
  <div class="wrap"><div class="capa__txt">
    <h1>Mais do que <span class="ouro">consultoria.</span></h1>
    <p class="capa__sub">Estratégia para transformar ideias em resultados.</p>
    <p class="capa__txt-p">A Plancenter oferece soluções em planejamento, projetos, gestão, consultoria, branding, mentoria e capacitação.</p>
    <div class="ctas">{f'<a class="btn btn--ouro" href="/obrigado?c=hero">Solicite seu atendimento {SETA}</a>'}<a class="btn btn--linha" href="#metodo">Conheça o método</a></div>
  </div></div>
  <span class="capa__linha" aria-hidden="true"></span>
</section>

<section class="sec" id="visao"><div class="wrap">
  <div class="cab rv"><h2>Toda grande realização começa com uma <span class="ouro">visão.</span></h2><p>Nosso propósito é ajudar você a transformá-la em estratégia e ação.</p></div>
  <div class="fluxo" data-fluxo><div class="fluxo__trilho" aria-hidden="true"><i></i></div>{fluxo}</div>
  <p class="frase rv">Estratégia, projetos e soluções para um futuro de <b class="ouro">grandes realizações.</b></p>
</div></section>

<section class="sec fundo" id="solucoes">{fundo("rede")}<div class="wrap">
  <div class="cab rv"><h2>Tudo o que sua ideia precisa para se transformar em <span class="ouro">projeto.</span></h2><p>Da marca à gestão. Do planejamento à execução.</p></div>
  <div class="solucoes">{solucoes}</div>
  <p class="frase rv">Uma empresa. <b class="ouro">Múltiplas soluções.</b></p>
</div></section>

<section class="metodo" id="metodo">
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
</section>

<section class="sec" id="proposito"><div class="wrap">
  <div class="cab rv"><h2>Planejamos o presente. <span class="ouro">Construímos o futuro.</span></h2></div>
  <div class="mvv">{mvv}</div>
  <div class="valores" aria-hidden="true"><div class="valores__t">{valores * 4}</div></div>
</div></section>

<section class="sec fundo fundo--claro" id="porque">{fundo("cume")}<div class="wrap">
  <div class="cab rv"><h2>Seu projeto merece mais do que uma <span class="ouro">solução pronta.</span></h2></div>
  <div class="porque">{porque}</div>
  <p class="frase rv">Mais que projetos, <b class="ouro">realizamos propósitos.</b></p>
</div></section>

<section class="sec" id="ministerios"><div class="wrap par">
  <div class="foto rv">{foto("ministerio", (900, 1536), "Mesa de planejamento com Bíblia, agenda e documentos, com uma cruz simples ao fundo", "(max-width:760px) 92vw, 46vw")}</div>
  <div class="par__txt rv" data-d="1">
    <h2>Propósito espiritual também precisa de <span class="ouro">organização.</span></h2>
    <p>Consultoria e assessoria para igrejas e ministérios. Estratégia e organização para fortalecer o propósito e ampliar os resultados.</p>
    <ul class="docs">{docs}</ul>
    <ul class="frentes">{frentes}</ul>
    <div class="ctas" style="margin-top:2rem"><a class="btn btn--ouro" href="/obrigado?c=ministerios">Quero organizar meu ministério {SETA}</a></div>
  </div>
</div></section>

<section class="sec fundo" id="contato">{fundo("aurora")}<div class="wrap"><div class="final rv"><div class="final__grid">
  <div>
    <h2>Tem uma ideia, empresa, projeto ou ministério que precisa avançar? <span class="ouro">Fale com a Plancenter.</span></h2>
    <p>Conte-nos o que você precisa. Vamos analisar como podemos ajudar.</p>
    <a class="tel" href="/obrigado?c=telefone">{ZAP} {TEL_VER}</a>
  </div>
  <form class="form" data-form novalidate>
    <div class="campo"><label for="f-nome">Nome</label><input id="f-nome" name="Nome" autocomplete="name" required></div>
    <div class="campo"><label for="f-zap">WhatsApp</label><input id="f-zap" name="WhatsApp" type="tel" inputmode="tel" autocomplete="tel" required></div>
    <div class="campo campo--cheio"><label for="f-tipo">O que você quer fazer avançar</label><select id="f-tipo" name="Quero avançar com" required><option value="" disabled selected>Escolha</option><option>Uma ideia</option><option>Uma empresa</option><option>Um projeto</option><option>Um ministério ou igreja</option></select></div>
    <div class="campo campo--cheio"><label for="f-msg">Conte o que você precisa (opcional)</label><textarea id="f-msg" name="Mensagem" rows="2"></textarea></div>
    <div class="form__mel" aria-hidden="true"><input name="site" tabindex="-1" autocomplete="off"></div>
    <label class="aceite"><input type="checkbox" name="aceite" required> Concordo com o uso dos meus dados para receber o retorno da Plancenter (LGPD).</label>
    <button class="btn btn--ouro" type="submit">Solicite seu atendimento {SETA}</button>
  </form>
</div></div></div></section>'''
    pre = ('<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="/assets/img/fotos/hero-1000.webp 1000w, /assets/img/fotos/hero-1672.webp 1672w" imagesizes="100vw" fetchpriority="high">\n'
           '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="/assets/img/fotos/hero-m-700.webp 700w, /assets/img/fotos/hero-m-1122.webp 1122w" imagesizes="100vw" fetchpriority="high">')
    return pagina("Plancenter | Consultoria e projetos: planejamento, gestão, branding e mentoria",
                  "Plancenter Consultoria & Projetos: planejamento estratégico, business plan, projetos, identidade visual, assessoria, consultoria, mentoria e capacitação. Também para igrejas e ministérios.",
                  corpo, "/", pre)


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
    (RAIZ / "index.html").write_text(home())
    (RAIZ / "obrigado.html").write_text(obrigado())
    (RAIZ / "robots.txt").write_text("User-agent: *\n" + ("Allow: /\n" if INDEXAR else "Disallow:\n") + f"\nSitemap: {DOMINIO}/sitemap.xml\n")
    (RAIZ / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMINIO}/</loc><lastmod>{date.today().isoformat()}</lastmod></url></urlset>\n')
    sol = "\n".join(f"- {n}" for _, n in SOLUCOES)
    met = "\n".join(f"{i+1}. {t}: {d}" for i, (t, d) in enumerate(METODO))
    (RAIZ / "llms.txt").write_text(f"""# Plancenter Consultoria & Projetos

> Onde suas ideias se transformam em projetos bem-sucedidos. A Plancenter oferece soluções em planejamento, projetos, gestão, consultoria, branding, mentoria e capacitação, para empresas, projetos e igrejas e ministérios.

## Soluções
{sol}
- Consultoria e assessoria para igrejas e ministérios: estatuto social, regimento interno, atas, plano de trabalho e plano estratégico.

## Método Plancenter
{met}

## Missão, visão e valores
- Missão: {MVV[0][1]}
- Visão: {MVV[1][1]}
- Valores: {MVV[2][1]}

## Contato
WhatsApp: {TEL_VER}
Site: {DOMINIO}/
""")
    print(f"  index.html {len((RAIZ / 'index.html').read_bytes())/1024:.1f} KB  site.js v={hash_de(JS)}  indexar={INDEXAR}")


if __name__ == "__main__":
    main()
