// let sounds = {};
if (typeof sounds === "undefined") {
  var sounds = {};
}
// Cleans up long filenames for display: strips extension, replaces _ with space, trims long strings
function cleanName(raw) {
  let name = raw
    .replace(/\.[^/.]+$/, '')          // remove file extension
    .replace(/[_\-]+/g, ' ')           // underscores/hyphens → spaces
    .replace(/\s+/g, ' ')              // collapse multiple spaces
    .trim();
  // Truncate at 32 chars with ellipsis if still too long
  return name.length > 32 ? name.slice(0, 32).trimEnd() + '…' : name;
}

function loadMix(mixData) {
  stopAll();
  sounds = {};
  document.getElementById("mixer").innerHTML = "";
  let parsed = JSON.parse(mixData);
  parsed.forEach(sound => addSound(sound));
  showMixer();
  playAll();
}

async function searchSounds() {
  let q = document.getElementById("searchInput").value;
  let res = await fetch(`/search-sounds/?q=${q}`);
  let data = await res.json();
  let container = document.getElementById("soundLibrary");
  container.innerHTML = "";
  data.results.forEach((sound, i) => {
    let div = document.createElement("div");
    div.className = "sound-card";
    div.style.animationDelay = `${i * 0.07}s`;
    div.innerHTML = `
      <span class="sound-name">${cleanName(sound.name)}</span>
      <audio controls src="${sound.preview}"></audio>
      <button class="add-btn">+ Add to Mix</button>
    `;
    div.querySelector("button").onclick = () => addSound(sound);
    container.appendChild(div);
  });
}

function addSound(sound) {
  if (sounds[sound.name]) return;
  let audio = new Audio(sound.preview);
  audio.loop = true;
  audio.volume = 0.5;
  sounds[sound.name] = audio;

  showMixer();

  let mixer = document.getElementById("mixer");
  let div = document.createElement("div");
  div.className = "mix-item";
  div.id = `sound-${sound.name}`;

  let displayName = cleanName(sound.name);

  div.innerHTML = `
    <span class="mix-track-name" title="${sound.name}">${displayName}</span>
    <input type="range" min="0" max="1" step="0.05" value="0.5" style="--val:50%">
    <button class="remove-btn" onclick="removeSound('${sound.name}')">✕</button>
  `;

  let slider = div.querySelector("input");
  slider.oninput = () => {
    audio.volume = parseFloat(slider.value);
    slider.style.setProperty('--val', (slider.value * 100) + '%');
  };

  mixer.appendChild(div);
}

function showMixer() {
  document.getElementById("mixerSection").style.display = "block";
}

function playAll() {
  Object.values(sounds).forEach(a => { a.currentTime = 0; a.play(); });
}

function stopAll() {
  Object.values(sounds).forEach(a => { a.pause(); a.currentTime = 0; });
}

function removeSound(name) {
  if (sounds[name]) { sounds[name].pause(); delete sounds[name]; }
  let el = document.getElementById(`sound-${name}`);
  if (el) el.remove();
  if (Object.keys(sounds).length === 0) {
    document.getElementById("mixerSection").style.display = "none";
  }
}

// function saveMix() {
//   let name = prompt("Name your soundscape");
//   if (!name) return;
//   let soundData = Object.entries(sounds).map(([name, audio]) => ({ name, preview: audio.src }));
//   fetch("{% url 'save_mix' %}", {
//     method: "POST",
//     headers: { "Content-Type": "application/json", "X-CSRFToken": "{{ csrf_token }}" },
//     body: JSON.stringify({ name, sounds: soundData })
//   }).then(() => location.reload());
// }

function saveMix() {
  let name = prompt("Name your soundscape");
  if (!name) return;

  let soundData = Object.entries(sounds).map(([name, audio]) => ({
    name,
    preview: audio.src
  }));

  fetch(SAVE_MIX_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ name, sounds: soundData })
  })
  .then(response => {

    // 🔒 NOT LOGGED IN
    if (response.status === 401) {
      alert("Please login to save your mix!");
      window.location.href = "/login/";
      return;
    }

    return response.json();
  })
  .then(data => {
    if (data && data.status === "ok") {
      alert("Mix saved successfully!");
      location.reload();
    }
  });
}

// function saveMix() {

//   // 🔒 STEP 1: Check login FIRST
//   if (!IS_AUTHENTICATED) {
//     alert("Login required to save your mix");

//     // redirect to login AND come back here
//       window.location.href = "/login/?next=" + encodeURIComponent(window.location.pathname);
//       window.location.href = "/login/";
//     return;
//   }

//   // ✅ STEP 2: Ask name ONLY if logged in
//   let name = prompt("Name your soundscape");
//   if (!name) return;

//   let soundData = Object.entries(sounds).map(([name, audio]) => ({
//     name,
//     preview: audio.src
//   }));

//   fetch(SAVE_MIX_URL, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//       "X-CSRFToken": getCSRFToken()
//     },
//     body: JSON.stringify({ name, sounds: soundData })
//   })
//   .then(response => response.json())
//   .then(data => {
//     if (data.status === "ok") {
//       alert("Mix saved!");
//       location.reload();
//     }
//   });
// }



// Enter key search
document.getElementById("searchInput").addEventListener("keydown", e => {
  if (e.key === "Enter") {
    e.preventDefault();   // 🔥 stop form submit
    searchSounds();
  }
});;
