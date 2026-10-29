// Каталог. Фото кладутся в img/<img>.jpg (или .png/.webp — поменяй расширение в IMG_EXT).
// Пока фото нет, показывается серый силуэт на белом фоне.
const IMG_EXT = "jpg";

const FALLBACK_CARS = [
  { brand: "Mercedes-Benz", name: "S 580 4MATIC", img: "mercedes-s580", type: "sedan", price: 126000, hp: 496, acc: 4.4, engine: "4.0 V8 biturbo, mild hybrid", drive: "Полный" },
  { brand: "Mercedes-Benz", name: "AMG G 63", img: "mercedes-g63", type: "suv", price: 180000, hp: 577, acc: 4.4, engine: "4.0 V8 biturbo", drive: "Полный" },
  { brand: "BMW", name: "M5", img: "bmw-m5", type: "sedan", price: 120000, hp: 717, acc: 3.4, engine: "4.4 V8 + электро (гибрид)", drive: "Полный" },
  { brand: "BMW", name: "X7 xDrive40i", img: "bmw-x7", type: "suv", price: 87000, hp: 375, acc: 5.8, engine: "3.0 R6 turbo, mild hybrid", drive: "Полный" },
  { brand: "Audi", name: "RS 7 Sportback", img: "audi-rs7", type: "sedan", price: 130000, hp: 621, acc: 3.5, engine: "4.0 V8 biturbo, mild hybrid", drive: "Полный" },
  { brand: "Audi", name: "RS Q8", img: "audi-rsq8", type: "suv", price: 116000, hp: 591, acc: 3.6, engine: "4.0 V8 biturbo, mild hybrid", drive: "Полный" },
  { brand: "Porsche", name: "911 Carrera S", img: "porsche-911", type: "coupe", price: 143000, hp: 443, acc: 3.0, engine: "3.0 H6 biturbo", drive: "Задний" },
  { brand: "Lexus", name: "LC 500", img: "lexus-lc500", type: "coupe", price: 101000, hp: 471, acc: 4.4, engine: "5.0 V8", drive: "Задний" },
];

const SHAPES = {
  sedan: "M20 118 L44 98 Q66 72 116 68 L196 64 Q236 64 256 92 L296 100 Q314 104 316 120 L316 132 L20 132 Z",
  suv:   "M20 118 L34 78 Q40 62 64 60 L250 60 Q272 62 282 84 L304 98 Q316 104 316 120 L316 132 L20 132 Z",
  coupe: "M20 120 L52 102 Q86 74 136 70 L190 68 Q232 72 252 96 L298 104 Q316 108 316 122 L316 132 L20 132 Z",
};

function silhouette(type) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 336 170">
    <rect width="336" height="170" fill="#fff"/>
    <path d="${SHAPES[type]}" fill="#d9d9d9"/>
    <circle cx="86" cy="132" r="18" fill="#8a8a8a"/><circle cx="86" cy="132" r="8" fill="#fff"/>
    <circle cx="258" cy="132" r="18" fill="#8a8a8a"/><circle cx="258" cy="132" r="8" fill="#fff"/>
  </svg>`;
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

const usd = n => "$" + n.toLocaleString("en-US");
let cars = FALLBACK_CARS;
const grid = document.getElementById("grid");
const filters = document.getElementById("filters");

function card(c) {
  const el = document.createElement("article");
  el.className = "card";
  el.innerHTML = `
    <div class="photo"><img alt="${c.brand} ${c.name}" loading="lazy" src="img/${c.img}.${IMG_EXT}"></div>
    <div class="brand">${c.brand}</div>
    <h3>${c.name}</h3>
    <ul class="specs">
      <li>Мощность <b>${c.hp} л.с.</b></li>
      <li>0–100 км/ч <b>${c.acc} с</b></li>
      <li>Привод <b>${c.drive}</b></li>
      <li>Двигатель <b>${c.engine}</b></li>
    </ul>
    <div class="price"><small>от</small>${usd(c.price)}</div>
    <a class="btn ghost" href="mailto:sales@example.com?subject=${encodeURIComponent(c.brand + " " + c.name)}">Запросить предложение</a>`;
  const img = el.querySelector("img");
  img.addEventListener("error", () => { img.src = silhouette(c.type); }, { once: true });
  return el;
}

function render(brand) {
  grid.replaceChildren(...cars.filter(c => brand === "Все" || c.brand === brand).map(card));
  filters.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.brand === brand)));
}

// Данные берём из API (/api/cars). Если бэкенд недоступен, показываем встроенный список.
async function init() {
  try {
    const r = await fetch("/api/cars");
    if (!r.ok) throw new Error("HTTP " + r.status);
    cars = await r.json();
  } catch (e) {
    cars = FALLBACK_CARS;
  }
  ["Все", ...new Set(cars.map(c => c.brand))].forEach(b => {
    const btn = document.createElement("button");
    btn.textContent = b;
    btn.dataset.brand = b;
    btn.addEventListener("click", () => render(b));
    filters.append(btn);
  });
  render("Все");
}
init();
