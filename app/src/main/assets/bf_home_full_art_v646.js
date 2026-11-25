/* Home-only illustration selector. Exact effective form, never substitute another form. */
(()=>{
  'use strict';
  const allowed = Object.freeze([10011,10012,20011,20012,30011,30012,40011,40012,50011,50012,60011,60012]);
  window.BFHomeFullArtV646 = (unit, fallback) => {
    if (!unit || !Number.isSafeInteger(unit.id) || !allowed.includes(unit.id) ||
        typeof fallback !== 'function') return null;
    const image = document.createElement('img');
    image.alt = '';
    image.style.imageRendering = 'auto';
    const portrait = unit.portrait, name = unit.name;
    // Complete a pre-attachment double failure at the card's append boundary.
    // The same V266 fallback is used for attached and detached cards.
    image.bfArtAttach = () => {
      if (image.parentNode && image.dataset.bfArtFallback === 'none') {
        image.replaceWith(fallback('', name));
      }
    };
    const none = () => {
      image.dataset.bfArtFallback = 'none';
      image.setAttribute('aria-label', 'Portrait unavailable for ' + String(name || 'Unit'));
      image.bfArtAttach();
    };
    const settle = () => {
      if (image.parentNode) { image.replaceWith(fallback(portrait, name)); return; }
      if (image.dataset.bfArtFallback) return;
      image.dataset.bfArtFallback = 'portrait';
      image.style.imageRendering = '';
      const stub = fallback(portrait, name);
      if (stub instanceof HTMLImageElement && stub.getAttribute('src')) {
        image.addEventListener('error', () => {
          if (image.parentNode) image.replaceWith(fallback('', name));
          else none();
        }, {once:true});
        image.src = stub.getAttribute('src');
      } else none();
    };
    image.addEventListener('error', settle, {once:true});
    image.src = 'content/unit/img/unit_ills_full_' + unit.id + '.png';
    return image;
  };
})();
