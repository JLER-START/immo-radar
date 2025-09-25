async function loadData() {
  const r = await fetch('data/listings.json?cache=' + Date.now());
  return await r.json();
}

function fmtPrice(x) {
  if (x == null) return '—';
  return new Intl.NumberFormat('nl-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(x);
}
function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('nl-BE', { dateStyle: 'medium', timeStyle: undefined });
}

function render(list) {
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  list.forEach(it => {
    const card = document.createElement('div');
    card.className = 'card';
    const a = document.createElement('a');
    a.className = 'title';
    a.href = it.url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = it.title;

    const meta = document.createElement('div');
    meta.className = 'meta';
    const loc = document.createElement('span'); loc.textContent = it.location || '—';
    const price = document.createElement('span'); price.className = 'price'; price.textContent = fmtPrice(it.price_eur);
    const dateP = document.createElement('span'); dateP.textContent = 'Geplaatst: ' + fmtDate(it.date_posted_iso || it.date_posted_raw);
    const firstSeen = document.createElement('span'); firstSeen.textContent = 'Ontdekt: ' + fmtDate(it.first_seen);
    const source = document.createElement('span'); source.className = 'source'; source.textContent = it.source;

    const isNew = (() => {
      if (!it.first_seen) return false;
      const now = Date.now();
      return (now - new Date(it.first_seen).getTime()) < (36 * 3600 * 1000); // 36u
    })();
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = isNew ? 'Nieuw' : 'Laatste update';

    meta.append(loc, price, dateP, firstSeen, source, badge);
    card.append(a, meta);
    grid.append(card);
  });
}

function applyFilters(raw) {
  const q = document.getElementById('q').value.toLowerCase().trim();
  let list = raw;
  if (q) {
    list = list.filter(it => (it.title || '').toLowerCase().includes(q) || (it.location || '').toLowerCase().includes(q));
  }
  const sort = document.getElementById('sort').value;
  const cmp = {
    posted_desc: (a,b)=> (b.date_posted_iso||'').localeCompare(a.date_posted_iso||''),
    first_seen_desc: (a,b)=> (b.first_seen||'').localeCompare(a.first_seen||''),
    price_asc: (a,b)=> (a.price_eur??Infinity) - (b.price_eur??Infinity),
    price_desc: (a,b)=> (b.price_eur??-Infinity) - (a.price_eur??-Infinity),
  }[sort];
  list = [...list].sort(cmp);
  return list;
}

(async () => {
  const data = await loadData();
  const state = { raw: data };
  const onChange = () => render(applyFilters(state.raw));
  document.getElementById('q').addEventListener('input', onChange);
  document.getElementById('sort').addEventListener('change', onChange);
  document.getElementById('reset').addEventListener('click', () => {
    document.getElementById('q').value = '';
    document.getElementById('sort').value = 'posted_desc';
    onChange();
  });
  onChange();
})();
