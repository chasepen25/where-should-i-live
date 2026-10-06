const form = document.querySelector("#rent-form");
const results = document.querySelector("#results");

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
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const budget = Number(new FormData(form).get("max-rent"));
  if (!Number.isFinite(budget) || budget <= 0) {
    showMessage("Enter a monthly rent greater than $0.", "error");
    return;
  }

  results.setAttribute("aria-busy", "true");
  showMessage("Finding places…", "loading");
  try {
    const response = await fetch(`/states?max-rent=${encodeURIComponent(budget)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load places.");
    renderPlaces(data.places, data.max_rent);
  } catch (error) {
    showMessage(error.message || "Could not connect. Make sure the local app is running.", "error");
  } finally {
    results.setAttribute("aria-busy", "false");
  }
});
