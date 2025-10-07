const questions = [...document.querySelectorAll(".question")];
const total = questions.length;
const progress = document.getElementById("progress");
const progressText = document.getElementById("progress-text");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");

let currentStep = 0;

function renderStep() {
  questions.forEach((q, i) => {
    q.classList.remove("active");
    if (i === currentStep) {
      q.classList.add("active");
    }
  });

  prevBtn.disabled = currentStep === 0;
  nextBtn.style.display = currentStep === total - 1 ? "none" : "inline-block";
  submitBtn.style.display = currentStep === total - 1 ? "block" : "none";

  progressText.textContent = `Pregunta ${currentStep + 1}/${total}`;
  progress.style.width = `${((currentStep + 1) / total) * 100}%`;
}

nextBtn.addEventListener("click", () => {
  if (currentStep < total - 1) {
    currentStep++;
    renderStep();
  }
});

prevBtn.addEventListener("click", () => {
  if (currentStep > 0) {
    currentStep--;
    renderStep();
  }
});

renderStep();
