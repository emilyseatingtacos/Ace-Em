const responseBank = {
  yesEnergy: [
    "Yeah, sure. After snacks.",
    "Probably. If it benefits me.",
    "Yes. But I expect cheese.",
    "Fine. But I’m judging you.",
    "Proceed. I’ll supervise."
  ],
  noEnergy: [
    "Absolutely not.",
    "That’s a terrible idea.",
    "Did you even think this through?",
    "No. Go sit in the corner.",
    "Ask again after treats."
  ],
  chaotic: [
    "Only if we escape the yard again.",
    "Maybe. Depends on squirrels.",
    "The spirits say… nap first.",
    "Your question lacks peanut butter.",
    "Unclear. Need belly rubs to continue."
  ],
  wisdom: [
    "Trust the one with snacks.",
    "Love is real. So are treats.",
    "Walk first. Decisions later.",
    "Adopt, don’t overthink.",
    "You’re overcomplicating it."
  ],
  houdiniEnergy: [
    "I escaped worse situations than this.",
    "I survived Puerto Rico streets. You’ll survive this.",
    "Confidence level: Shar-Pei wrinkle.",
    "The answer is outside. Let’s go.",
    "You are not the alpha here."
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
    answerText.textContent = "Ask a real question first, human.";
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
