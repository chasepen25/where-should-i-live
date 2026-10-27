const form = document.querySelector("#rent-form");
const results = document.querySelector("#results");
const housingPlan = document.querySelector("#housing-plan");
const budgetLabel = document.querySelector("#budget-label");
const budgetInput = document.querySelector("#housing-budget");

housingPlan.addEventListener("change", () => {
  const buying = housingPlan.value === "buy";
  budgetLabel.textContent = buying
    ? "What is your maximum home purchase budget?"
    : "What is your maximum monthly rent?";
  budgetInput.step = buying ? "5000" : "50";
  budgetInput.value = buying ? "300000" : "1500";
  budgetInput.placeholder = buying ? "300000" : "1500";
});

function money(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

function showMessage(message, kind = "") {
  results.className = kind;
  results.replaceChildren();
  const paragraph = document.createElement("p");
  paragraph.textContent = message;
  results.append(paragraph);
}

function appendRetryButton() {
  const retry = document.createElement("button");
  retry.type = "button";
  retry.className = "retry-button";
  retry.textContent = "Try another search";
  retry.addEventListener("click", () => {
    results.replaceChildren();
    results.className = "";
    form.reset();
    housingPlan.dispatchEvent(new Event("change"));
    form.scrollIntoView({ behavior: "smooth", block: "center" });
    housingPlan.focus({ preventScroll: true });
  });
  results.append(retry);
}

function renderPlaces(places, budget) {
  results.replaceChildren();
  results.className = "results-section";

  const heading = document.createElement("h2");
  heading.textContent = places.length
    ? `${places.length} ${places.length === 1 ? "place" : "places"} to explore`
    : "No matches in this demo yet";
  results.append(heading);

  if (!places.length) {
    const empty = document.createElement("p");
    empty.textContent = `Try a budget below ${money(budget)}? The sample cities start at ${money(1050)} per month.`;
    results.append(empty);
    appendRetryButton();
    return;
  }

  const list = document.createElement("div");
  list.className = "place-list";
  places.forEach((place) => {
    const card = document.createElement("article");
    card.className = "place-card";
    const name = document.createElement("h3");
    name.textContent = place.city;
    const state = document.createElement("p");
    state.className = "place-state";
    state.textContent = place.state;
    const rent = document.createElement("p");
    rent.className = "place-rent";
    rent.textContent = `${money(place.rent)} / month`;
    const note = document.createElement("span");
    note.className = "place-note";
    note.textContent = place.note;
    card.append(name, state, rent, note);
    list.append(card);
  });
  results.append(list);

  appendRetryButton();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const answers = new FormData(form);
  const budget = Number(answers.get("housing-budget"));
  const income = Number(answers.get("household-income"));
  if (!Number.isFinite(budget) || budget <= 0 || !Number.isFinite(income) || income <= 0) {
    showMessage("Enter a housing budget and household income greater than $0.", "error");
    return;
  }

  results.setAttribute("aria-busy", "true");
  showMessage("Finding places…", "loading");
  try {
    const params = new URLSearchParams({
      "housing-plan": answers.get("housing-plan"),
      "housing-budget": String(budget),
      "household-income": String(income),
    });
    const response = await fetch(`/states?${params}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load places.");
    renderPlaces(data.places, budget);
  } catch (error) {
    showMessage(error.message || "Could not connect. Make sure the local app is running.", "error");
  } finally {
    results.setAttribute("aria-busy", "false");
  }
});
