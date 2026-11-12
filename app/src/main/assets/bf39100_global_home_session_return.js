/* v391: Session-only Home navigation shortcut. Original Global shortcut art;
 * reconstructed convenience, NOT a recovered 2022 engine behavior.
 * Never reads/writes the canonical save or triggers gameplay automatically. */
(() => {
  'use strict';
  if (window.BFHomeSessionReturnV39100) return;
  const nav = window.BF_homeNav;
  const home = document.getElementById('bf-home');
  if (!nav || typeof nav.go !== 'function' || !home ||
      home.dataset.globalScene !== '1') return;
  const labels = Object.freeze({
    quest: 'QUEST', units: 'UNITS', summon: 'SUMMON', menu: 'MENU'
  });
  const section = document.createElement('section');
  section.id = 'bf-home-session-return';
  section.hidden = true;
  section.setAttribute('aria-label', 'Session navigation shortcut');
  section.style.cssText =
    'display:none;box-sizing:border-box;max-width:100%;min-width:0;' +
    'margin:8px 0;padding:7px;border:1px solid #9b8050;' +
    'border-radius:6px;background:linear-gradient(#23394a,#102334)';
  const button = document.createElement('button');
  button.id = 'bf-home-return-button';
  button.type = 'button';
  button.style.cssText =
    'display:flex;align-items:center;justify-content:center;gap:8px;' +
    'width:100%;max-width:100%;min-width:0;min-height:48px;' +
    'box-sizing:border-box;padding:6px 10px;cursor:pointer;' +
    'border:2px ridge #bd995d;border-radius:5px;' +
    'background:linear-gradient(#80683e,#324353);color:#ffedc8;' +
    'font:800 12px/1.35 Arial,sans-serif';
  const image = document.createElement('img');
  image.src = 'content/home/home_new_btn_shortcut1.png';
  image.alt = '';
  image.setAttribute('aria-hidden', 'true');
  image.style.cssText =
    'width:43px;height:36px;object-fit:contain;flex:none';
  const title = document.createElement('span');
  title.id = 'bf-home-return-label';
  title.style.cssText = 'min-width:0;overflow-wrap:anywhere';
  button.append(image, title);
  section.append(button);
  home.append(section);
  let lastRoute = null;
  function refresh() {
    const visible = nav.current === 'home' && lastRoute !== null;
    section.hidden = !visible;
    section.style.display = visible ? 'block' : 'none';
    if (visible) {
      title.textContent = 'RETURN TO ' + labels[lastRoute];
      button.setAttribute('aria-label', 'Return to last visited ' +
        labels[lastRoute].toLowerCase() + ' screen');
    } else title.textContent = '';
    return visible;
  }
  window.addEventListener('bf-route-change', event => {
    const route = event && event.detail && event.detail.route;
    if (Object.prototype.hasOwnProperty.call(labels, route)) lastRoute = route;
    refresh();
  });
  button.addEventListener('click', () => {
    if (nav.current !== 'home' || lastRoute === null ||
        !Object.prototype.hasOwnProperty.call(labels, lastRoute)) return;
    // Existing native Home router remains the only navigation authority.
    nav.go(lastRoute);
  });
  window.BFHomeSessionReturnV39100 = Object.freeze({
    get lastRoute() { return lastRoute; },
    refresh
  });
  refresh();
})();
