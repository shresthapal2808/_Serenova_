/* ==========================================================
   Serenova — About Page JS  (about.js)
   Handles: star canvas, custom cursor, scroll reveals,
            staggered feature cards, parallax subtle effect
   ========================================================== */

/* ── 1. STAR CANVAS ──────────────────────────────────────── */
(function initStars() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H;
  const stars = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  /* Generate 140 stars with random properties */
  for (let i = 0; i < 140; i++) {
    stars.push({
      x:  Math.random(),          // fraction of width
      y:  Math.random(),          // fraction of height
      r:  Math.random() * 1.3 + 0.2,
      a:  Math.random(),          // current opacity
      s:  Math.random() * 0.004 + 0.001,   // twinkle speed
      p:  Math.random() * Math.PI * 2,     // phase offset
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    stars.forEach(s => {
      s.p += s.s;
      s.a = 0.12 + 0.38 * Math.abs(Math.sin(s.p));
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(196,167,231,${s.a})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();


/* ── 2. CUSTOM CURSOR ────────────────────────────────────── */
(function initCursor() {
  const cur  = document.getElementById('aboutCur');
  const curR = document.getElementById('aboutCurR');
  if (!cur || !curR) return;

  let mx = 0, my = 0, rx = 0, ry = 0;

  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    cur.style.left = mx + 'px';
    cur.style.top  = my + 'px';
  });

  /* Lagging ring for smooth trail effect */
  setInterval(() => {
    rx += (mx - rx) * 0.13;
    ry += (my - ry) * 0.13;
    curR.style.left = rx + 'px';
    curR.style.top  = ry + 'px';
  }, 16);

  /* Cursor grows on hoverable elements */
  document.querySelectorAll('a, button, .ab-feat-card, .ab-pill, .ab-tag')
    .forEach(el => {
      el.addEventListener('mouseenter', () => {
        curR.style.transform = 'translate(-50%,-50%) scale(1.8)';
        curR.style.borderColor = 'rgba(201,75,143,0.5)';
      });
      el.addEventListener('mouseleave', () => {
        curR.style.transform = 'translate(-50%,-50%) scale(1)';
        curR.style.borderColor = 'rgba(224,123,181,0.4)';
      });
    });
})();


/* ── 3. SCROLL REVEAL (IntersectionObserver) ─────────────── */
(function initReveal() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;

      const el = entry.target;
      el.classList.add('visible');

      /* Stagger children: feature cards */
      el.querySelectorAll('.ab-feat-card').forEach((card, i) => {
        card.style.transitionDelay = (i * 0.10) + 's';
        card.classList.add('visible');
      });

      /* Stagger children: value items */
      el.querySelectorAll('.ab-value').forEach((val, i) => {
        val.style.transitionDelay = (i * 0.12) + 's';
        val.classList.add('visible');
      });

      io.unobserve(el); // reveal once only
    });
  }, { threshold: 0.08 });

  /* Observe section-level reveal targets */
  document.querySelectorAll('.ab-reveal').forEach(el => io.observe(el));

  /* Also observe individual cards/values that may be outside .ab-reveal */
  document.querySelectorAll('.ab-feat-card, .ab-value').forEach(el => {
    io.observe(el);
  });
})();


/* ── 4. SUBTLE PARALLAX ON HERO ORBITAL RINGS ───────────── */
(function initParallax() {
  const orbits = document.querySelectorAll('.ab-orbit');
  if (!orbits.length) return;

  window.addEventListener('scroll', () => {
    const sy = window.scrollY;
    orbits.forEach((ring, i) => {
      const dir   = i % 2 === 0 ? 1 : -1;
      const speed = 0.04 + i * 0.015;
      ring.style.marginTop = (sy * speed * dir) + 'px';
    });
  }, { passive: true });
})();


/* ── 5. TECH STACK PILL — staggered entrance ─────────────── */
(function initPills() {
  const pills = document.querySelectorAll('.ab-pill');
  if (!pills.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      pills.forEach((p, i) => {
        p.style.opacity   = '0';
        p.style.transform = 'translateY(16px)';
        p.style.transition = `opacity 0.5s ease ${i * 0.07}s,
                              transform 0.5s ease ${i * 0.07}s`;
        /* Small timeout so transition is applied before class flip */
        setTimeout(() => {
          p.style.opacity   = '1';
          p.style.transform = 'translateY(0)';
        }, 50);
      });
      io.disconnect();
    });
  }, { threshold: 0.2 });

  const stackSection = document.querySelector('.ab-stack');
  if (stackSection) io.observe(stackSection);
})();