/* Plancenter: comportamento da landing. Sem dependências. */
(() => {
  const d = document, h = d.documentElement, w = window;
  const rm = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const largo = w.matchMedia('(min-width:761px)');

  /* menu */
  const burger = d.querySelector('.burger');
  if (burger) burger.addEventListener('click', () => {
    const abre = !h.classList.contains('menu-open');
    h.classList.toggle('menu-open', abre);
    burger.setAttribute('aria-expanded', abre);
  });
  d.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', () => h.classList.remove('menu-open')));

  /* revelações (com reserva: nada fica invisível) */
  const alvos = [...d.querySelectorAll('.rv, .valores, .frase')];
  if ('IntersectionObserver' in w) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      const corre = en.target.matches('.valores');
      if (en.isIntersecting) { en.target.classList.add('in'); if (!corre) io.unobserve(en.target); }
      else if (corre) en.target.classList.remove('in');
    }), { rootMargin: '0px 0px -6% 0px' });
    alvos.forEach(el => io.observe(el));
  } else alvos.forEach(el => el.classList.add('in'));
  setTimeout(() => alvos.forEach(el => { if (el.getBoundingClientRect().top < innerHeight) el.classList.add('in'); }), 2500);

  /* peças que andam com o scroll */
  const topo = d.querySelector('.top');
  const fluxo = d.querySelector('[data-fluxo]');
  const trilho = fluxo && fluxo.querySelector('.fluxo__trilho');
  const etapas = fluxo ? [...fluxo.querySelectorAll('.etapa')] : [];
  const metodo = d.querySelector('.metodo');
  const linha = metodo && metodo.querySelector('.ouro-l');
  const nos = metodo ? [...metodo.querySelectorAll('.no-html')] : [];
  const passos = metodo ? [...metodo.querySelectorAll('.passo')] : [];
  const marcos = [0.1, 0.3, 0.5, 0.7, 0.9];
  const fundo = d.querySelector('[data-paralaxe] img');
  const lim = v => Math.min(1, Math.max(0, v));

  const quadro = () => {
    pendente = false;
    topo && topo.classList.toggle('solid', w.scrollY > 30);
    if (fluxo) {
      const r = fluxo.getBoundingClientRect();
      const p = rm ? 1 : lim((innerHeight * 0.85 - r.top) / (innerHeight * 0.55));
      trilho && trilho.style.setProperty('--p', p.toFixed(3));
      etapas.forEach((el, i) => el.classList.toggle('on', p >= i / 3 - 0.02));
    }
    if (metodo && largo.matches) {
      const r = metodo.getBoundingClientRect(), total = metodo.offsetHeight - innerHeight;
      const p = rm ? 1 : lim(-r.top / (total * 0.85));
      linha && linha.setAttribute('stroke-dashoffset', (1 - p).toFixed(4));
      nos.forEach((n, i) => n.classList.toggle('on', p >= marcos[i] - 0.02));
      passos.forEach((s, i) => s.classList.toggle('on', p >= marcos[i] - 0.02));
    }
    if (fundo && !rm && largo.matches) {
      const y = w.scrollY;
      if (y < innerHeight * 1.2) fundo.style.transform = `scale(1.06) translate3d(0,${(y * 0.18).toFixed(1)}px,0)`;
    }
  };
  let pendente = false;
  const pedir = () => { if (!pendente) { pendente = true; requestAnimationFrame(quadro); } };
  w.addEventListener('scroll', pedir, { passive: true });
  w.addEventListener('resize', pedir, { passive: true });
  quadro();

  /* formulário: mensagem pronta para o WhatsApp */
  const t0 = Date.now();
  d.querySelectorAll('form[data-form]').forEach(form => form.addEventListener('submit', ev => {
    ev.preventDefault();
    if (!form.reportValidity()) return;
    const f = new FormData(form);
    if ((f.get('site') || '').toString().trim() || Date.now() - t0 < 2500) return;
    const linhas = ['Olá! Vim pelo site da Plancenter e quero solicitar um atendimento.', ''];
    for (const [k, v] of f.entries()) {
      if (k === 'site' || k === 'aceite') continue;
      const val = v.toString().trim();
      if (val) linhas.push(`${k}: ${val}`);
    }
    try { sessionStorage.setItem('pc_msg', linhas.join('\n')); } catch (_) {}
    location.href = '/obrigado?c=form';
  }));
})();
