// Manejo del sidebar y carga dinámica de cursos y temas

async function fetchCourses(){
  const res = await fetch('/api/courses');
  const data = await res.json();
  return data;
}

async function loadCourses(){
  const list = document.getElementById('coursesList');
  if(!list) return;
  const courses = await fetchCourses();
  list.innerHTML = '';
  courses.forEach(c=>{
    const li = document.createElement('li');
    li.textContent = c.title;
    li.dataset.slug = c.slug;
    li.addEventListener('click', ()=> onCourseClick(c.slug,c.title));
    list.appendChild(li);
  });
}

async function onCourseClick(slug, title){
  const center = document.getElementById('centerContent');
  // Si estamos en main.html
  if(center){
    const res = await fetch(`/api/topics/${slug}`);
    const topics = await res.json();
    center.innerHTML = `<h3>${title}</h3>`;
    if(!topics || topics.length === 0){
      center.innerHTML += '<p>No hay temas disponibles todavía.</p>';
      return;
    }
    const ul = document.createElement('ul');
    topics.forEach(t=>{
      const item = document.createElement('li');
      item.className = 'topic-item';
      const a = document.createElement('a');
      a.href = `/topic/${slug}/${t.slug}`;
      a.textContent = t.title;
      item.appendChild(a);
      ul.appendChild(item);
    });
    center.appendChild(ul);
  } else {
    // Si estamos en topic.html, redirige al curso para mostrar sus temas
    window.location.href = `/main#${slug}`;
  }
}

// Toggle sidebar (ocultar/mostrar)
function setupSidebarToggle(){
  const btns = document.querySelectorAll('#toggleSidebar');
  btns.forEach(b=>{
    b.addEventListener('click', ()=>{
      const s = document.getElementById('sidebar');
      if(!s) return;
      if(s.style.display === 'none') s.style.display = '';
      else s.style.display = 'block';
    });
  });
}

// Inicial
window.addEventListener('DOMContentLoaded', ()=>{
  loadCourses();
  setupSidebarToggle();

  // Si entramos desde un hash (#curso)
  const hash = window.location.hash.replace('#','');
  if(hash){
    onCourseClick(hash, '');
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const quizForm = document.getElementById("quizForm");
  if (!quizForm) return;

  const qElements = Array.from(quizForm.querySelectorAll(".quiz-question"));
  const nextBtn = document.getElementById("nextBtn");
  const finishBtn = document.getElementById("finishBtn");
  const correctInput = document.getElementById("correctCount");
  let current = 0;
  let correctCount = 0;

  // Mostrar la primera pregunta
  qElements[current].style.display = "block";

  qElements.forEach((q) => {
    const options = Array.from(q.querySelectorAll(".quiz-option"));
    const correctIdx = parseInt(q.dataset.correct);

    options.forEach((btn, idx) => {
      btn.addEventListener("click", () => {
        if (q.classList.contains("answered")) return;
        q.classList.add("answered");

        if (idx === correctIdx) {
          btn.classList.add("correct");
          correctCount++;
        } else {
          btn.classList.add("wrong");
          if (options[correctIdx]) options[correctIdx].classList.add("correct");
        }
        options.forEach(b => b.disabled = true);
      });
    });
  });

  nextBtn.addEventListener("click", () => {
    if (!qElements[current].classList.contains("answered")) {
      alert("Selecciona una respuesta antes de continuar.");
      return;
    }

    qElements[current].style.display = "none";
    current++;

    if (current < qElements.length) {
      qElements[current].style.display = "block";

      if (current === qElements.length - 1) {
        nextBtn.style.display = "none";
        finishBtn.style.display = "inline-block";
      }
    }
  });

  quizForm.addEventListener("submit", (e) => {
    correctInput.value = correctCount;
  });
});
