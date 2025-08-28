(() => {
  const qs = (sel) => document.querySelector(sel);
  const stage = qs('#stage');
  const evcount = qs('#evcount');
  const active = qs('#active');
  const done = qs('#done');
  const runidEl = qs('#runid');
  const soundBtn = qs('#sound');
  const spawnBtn = qs('#spawn');

  let events = 0, activeProviders = 0, completed = 0;
  let audioEnabled = false;

  // WebAudio simple servo sound
  const Audio = {
    ctx: null,
    blip() {
      if (!audioEnabled) return;
      if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      const ctx = this.ctx;
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = 'square';
      o.frequency.setValueAtTime(440, ctx.currentTime);
      o.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 0.18);
      g.gain.setValueAtTime(0.0001, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.03);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.22);
      o.connect(g).connect(ctx.destination);
      o.start();
      o.stop(ctx.currentTime + 0.24);
    }
  };

  function robot(x, y, speed) {
    const el = document.createElement('div');
    el.className = 'robot scanline';
    el.style.left = x + 'px';
    el.style.top = y + 'px';
    el.innerHTML = '<div class="eye"></div><div class="cargo"></div><div class="trail"></div>';
    stage.appendChild(el);
    const dir = Math.random() > 0.5 ? 1 : -1;
    let vx = (speed || (1 + Math.random() * 1.5)) * dir;
    let life = 30 + Math.random() * 30;
    function tick() {
      const rect = el.getBoundingClientRect();
      const nx = rect.left + vx;
      if (nx < 0 || nx > window.innerWidth - rect.width) {
        vx *= -1;
      }
      el.style.left = (rect.left + vx) + 'px';
      if (Math.random() < 0.02) Audio.blip();
      if ((life -= 0.5) > 0) requestAnimationFrame(tick);
      else el.remove();
    }
    requestAnimationFrame(tick);
    return el;
  }

  function spawn(n=3) {
    for (let i=0;i<n;i++) {
      const y = 100 + Math.random() * (window.innerHeight - 200);
      robot(Math.random() * window.innerWidth, y, 1 + Math.random()*2);
    }
  }

  function updateHUD() {
    evcount.textContent = String(events);
    active.textContent = String(activeProviders);
    done.textContent = String(completed);
  }

  // Controls
  soundBtn.addEventListener('click', () => {
    audioEnabled = !audioEnabled;
    soundBtn.textContent = audioEnabled ? 'Disable Sound' : 'Enable Sound';
    if (audioEnabled) Audio.blip();
  });
  spawnBtn.addEventListener('click', () => spawn(5));

  // Connect SSE
  const url = new URL(window.location.href);
  const run = url.searchParams.get('run');
  const latest = url.searchParams.get('latest') ?? '1';
  const evs = new EventSource(`/events?${run ? 'run='+encodeURIComponent(run) : 'latest='+latest}`);
  evs.addEventListener('hello', (e) => {
    try {
      const data = JSON.parse(e.data);
      runidEl.textContent = `run: ${data.run_id}`;
    } catch {}
  });
  evs.onmessage = (e) => {
    events++;
    try {
      const obj = JSON.parse(e.data);
      if (obj.event === 'provider_call_start') {
        activeProviders++;
        spawn(3);
      }
      if (obj.event === 'provider_call_end') {
        activeProviders = Math.max(0, activeProviders - 1);
        completed++;
        spawn(2);
      }
    } catch {}
    updateHUD();
  };

  // Ambient robots
  setInterval(() => spawn(1), 2000);
  updateHUD();
})();

