/* =========================================================
   Serenova — Journal Page JS
   Handles: mood pills, word count, tab switching,
            toast auto-dismiss
   ========================================================= */

// ── Mood pill selection ──────────────────────────────────
function pickMood(el) {
  // Remove 'selected' from all pills
  document.querySelectorAll('.sn-mood-pill')
          .forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  // Write mood value into the hidden form input
  document.getElementById('mood-input').value = el.textContent.trim();
}

// ── Word count + progress fill ───────────────────────────
function onType(textarea) {
  const words = textarea.value.trim()
                  ? textarea.value.trim().split(/\s+/).length
                  : 0;
  document.getElementById('sn-wordcount').textContent =
    words + ' word' + (words !== 1 ? 's' : '');

  // Progress bar fills at 200 words = 100%
  const pct = Math.min(Math.round((words / 200) * 100), 100);
  document.getElementById('sn-progress-fill').style.width = pct + '%';
}

// ── Clear textarea ───────────────────────────────────────
function clearDraft() {
  const ta = document.getElementById('sn-textarea');
  ta.value = '';
  onType(ta);
}

// ── Tab switching ────────────────────────────────────────
document.querySelectorAll('.sn-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    // Update active tab style
    document.querySelectorAll('.sn-tab')
            .forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    // Show correct panel, hide the other
    const target = btn.dataset.target;
    document.getElementById('sn-panel-write').style.display =
      target === 'write' ? 'block' : 'none';
    document.getElementById('sn-panel-history').style.display =
      target === 'history' ? 'block' : 'none';
  });
});

// ── Auto-dismiss Django flash toasts after 3 s ───────────
document.querySelectorAll('.sn-toast--show').forEach(toast => {
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(80px)';
  }, 3000);
});