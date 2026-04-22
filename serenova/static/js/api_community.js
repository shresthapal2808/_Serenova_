let nextPage = null;
let prevPage = null;
let currentMood = "";
let currentUrl = "/api/posts/";

// ================= LOAD POSTS =================
async function loadPosts(url = "/api/posts/") {
  try {
    currentUrl = url;

    let finalUrl = url;

    // attach mood filter safely
    if (currentMood) {
      if (finalUrl.includes("?")) {
        finalUrl += `&mood=${currentMood}`;
      } else {
        finalUrl += `?mood=${currentMood}`;
      }
    }

    const response = await fetch(finalUrl);
    const data = await response.json();

    const container = document.getElementById("posts-container");
    container.innerHTML = "";

    nextPage = data.next;
    prevPage = data.previous;

    data.results.forEach((post) => {
      const div = document.createElement("div");
      div.classList.add("post-card");

      div.innerHTML = `
        ${
          post.is_owner
            ? `
          <button class="edit-btn" onclick="editPost(${post.id}, this)">✏️Edit</button>
          <button class="delete-btn" onclick="deletePost(${post.id})">🗑️Delete</button>
        `
            : ""
        }

        <div class="post-header">
          <div class="post-avatar">${post.username.charAt(0).toUpperCase()}</div>
          <div class="post-meta">
            <h4>${post.username}</h4>
          </div>
        </div>

        <p class="post-content">${post.content}</p>

        <!-- COMMENTS -->
        <div class="comments-section">
            <div id="comments-${post.id}"></div>

            <div class="comment-input-box">
                <input id="input-${post.id}" placeholder="Write something kind..." />
                <button class="add-comment-btn" onclick="addComment(${post.id})">Add</button>
            </div>
        </div>
      `; 

      container.appendChild(div);

      // ✅ IMPORTANT: load comments per post
      loadComments(post.id);
    });

    // ✅ pagination buttons
    document.getElementById("next-btn").style.display = nextPage
      ? "inline-block"
      : "none";

    document.getElementById("prev-btn").style.display = prevPage
      ? "inline-block"
      : "none";

  } catch (error) {
    console.error("Error loading posts:", error);
  }
}

// ================= INIT =================
  document.addEventListener("DOMContentLoaded", () => {

  const savedMood = localStorage.getItem("selectedMood");

  if (savedMood) {
    currentMood = savedMood;
    document.getElementById("mood-filter").value = savedMood;
  }

  // ✅ ADD THIS BACK (VERY IMPORTANT)
  document.getElementById("mood-filter").addEventListener("change", (e) => {
    currentMood = e.target.value;
    localStorage.setItem("selectedMood", currentMood);
    loadPosts("/api/posts/");
  });

  loadPosts();  
});

  // pagination
  document.getElementById("next-btn").addEventListener("click", () => {
    if (nextPage) loadPosts(nextPage);
  });

  document.getElementById("prev-btn").addEventListener("click", () => {
    if (prevPage) loadPosts(prevPage);
  });

  // post form
  const form = document.getElementById("post-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const contentInput = document.getElementById("content");
    const content = contentInput.value.trim();
    const mood = document.getElementById("mood-filter").value || "calm";

    if (!content) {
      alert("Write something first");
      return;
    }

    try {
      const response = await fetch("/api/posts/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "same-origin",
        body: JSON.stringify({ content, mood }),
      });

      if (!response.ok) {
        alert("Post failed ❌");
        return;
      }

      contentInput.value = "";
      await loadPosts("/api/posts/");

    } catch (err) {
      console.error(err);
    }
  });


// ================= DELETE POST =================
async function deletePost(id) {
  if (!confirm("Delete this post?")) return;

  try {
    const response = await fetch(`/api/posts/${id}/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      credentials: "same-origin",
    });

    if (!response.ok) throw new Error("Delete failed");

    await loadPosts(currentUrl);

  } catch (error) {
    console.error(error);
  }
}

// ================= EDIT =================
async function editPost(id, btn) {
  const postCard = btn.closest(".post-card");
  const contentElement = postCard.querySelector(".post-content");

  const oldContent = contentElement.innerText;

  contentElement.innerHTML = `
    <textarea class="edit-area">${oldContent}</textarea>
    <button onclick="saveEdit(${id}, this)">💾 Save</button>
  `;
}

async function saveEdit(id, btn) {
  const postCard = btn.closest(".post-card");
  const newContent = postCard.querySelector(".edit-area").value.trim();

  if (!newContent) return alert("Empty!");

  const response = await fetch(`/api/posts/${id}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    credentials: "same-origin",
    body: JSON.stringify({ content: newContent }),
  });

  if (!response.ok) return alert("Edit failed");

  loadPosts(currentUrl);
}

// ================= COMMENTS =================
function loadComments(postId) {
  fetch(`/api/comments/${postId}/`)
    .then((res) => res.json())
    .then((data) => {
      const container = document.getElementById(`comments-${postId}`);
      container.innerHTML = "";

      data.forEach((comment) => {
       /* container.innerHTML += `
          <div class="comment">
            <p><strong>${comment.user}: </strong>${comment.text}</p>
            <button class="delete-comment-btn" onclick="deleteComment(${comment.id}, ${postId})">🗑️</button>
          </div>
        `;*/
          container.innerHTML += `
            <div class="comment">
                <div class="comment-text">
                    <strong>${comment.user}:</strong> ${comment.text}
                </div>
                <button class="comment-delete-btn" onclick="deleteComment(${comment.id}, ${postId})">🗑️</button>
            </div>
            `;
      });
    });
}

function addComment(postId) {
  const input = document.getElementById(`input-${postId}`);
  const text = input.value.trim();

  if (!text) return alert("Write something");

  fetch(`/api/comments/create/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    credentials: "same-origin",
    body: JSON.stringify({ post: postId, text }),
  }).then(() => {
    input.value = "";
    loadComments(postId);
  });
}

function deleteComment(commentId, postId) {
  fetch(`/api/comments/delete/${commentId}/`, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    credentials: "same-origin",
  }).then(() => {
    loadComments(postId);
  });
}

// ================= CSRF =================
function getCSRFToken() {
  let cookieValue = null;
  const cookies = document.cookie.split(";");

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith("csrftoken=")) {
      cookieValue = cookie.substring("csrftoken=".length);
      break;
    }
  }
  return cookieValue;
}