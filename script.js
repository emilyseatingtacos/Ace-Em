const responseBank = {
  yes: [
    "Yes — yeah, sure. After snacks.",
    "Yes — probably, if it benefits me.",
    "Yes — but I expect cheese.",
    "Yes — proceed. I’ll supervise.",
    "Yes — fine, but I’m judging you."
  ],
  no: [
    "No — absolutely not.",
    "No — that’s a terrible idea.",
    "No — did you even think this through?",
    "No — go sit in the corner.",
    "No — ask again after treats."
  ],
  maybe: [
    "Maybe — depends on squirrels.",
    "Maybe — the spirits say nap first.",
    "Maybe — your question lacks peanut butter.",
    "Maybe — unclear, need belly rubs to continue.",
    "Maybe — walk first, decisions later."
  ]
};

const askBtn = document.getElementById("askBtn");
const answerText = document.getElementById("answerText");
const ball = document.getElementById("ball");
const questionInput = document.getElementById("question");

const allResponses = Object.values(responseBank).flat();

function randomResponse() {
  return allResponses[Math.floor(Math.random() * allResponses.length)];
}

function askS8TOBall() {
  const question = questionInput.value.trim();

  if (!question) {
    answerText.textContent = "Ask any yes/no question first, human.";
    return;
  }

  ball.classList.remove("shake");
  void ball.offsetWidth;
  ball.classList.add("shake");

  answerText.textContent = "Consulting rescue-dog spirits...";

  window.setTimeout(() => {
    answerText.textContent = randomResponse();
  }, 520);
}

askBtn.addEventListener("click", askS8TOBall);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") askS8TOBall();
});
