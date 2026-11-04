# Plancenter — landing

Landing da Plancenter Consultoria & Projetos (empresa da Karla Messias). Página única + ponte `/obrigado` para o WhatsApp.

## Como editar
- Copy, ícones e listas: `build.py` (constantes no topo). A copy atual saiu dos 9 slides em `assets/src/slides/`
  (OCR em `_src/plancenter-ocr.txt`); a cliente vai mandar a copy final.
- Estilo: `assets/css/site.css`. Comportamento: `assets/js/site.js` (fluxo ideia → resultado, caminho do método
  desenhado no scroll, formulário para o WhatsApp).
- Imagens de fundo: geradas no ChatGPT (originais em `assets/src/geradas/`), em 16:9 para o computador e 4:5 para o celular.
- Depois de qualquer mudança: `python3 build.py`. Prévia: `python3 tools/serve.py 4200`.

## Domínio e SEO
- Tudo sai de `DOMINIO` no `build.py`. `INDEXAR = False` até a aprovação; depois `True`, build e push.
- WhatsApp: `WHATSAPP` (+55 61 99397-3723, o dos slides).
