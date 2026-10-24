// Location ids per site. Index and njuskalo use the same ids, oglasnik has its own.
const DEFAULTS = {
  mode: "buy",
  priceMin: 0,
  priceMax: 160000,
  rentMax: 500,
  m2Min: 44,
  m2Max: "",
  njuskaloIds: "1248,1257,1258,1260,1261,1262",
  oglasnikIds: "7445,7582,7600,7662,7669,7679",
};

const ids = (value) => value.split(",").map((x) => x.trim()).filter(Boolean);

// Each site returns a list of { label, url } for the current filters.
const SITES = [
  {
    name: "Njuškalo",
    build: (f) => {
      const geo = `geo%5BlocationIds%5D=${ids(f.njuskaloIds).join("%2C")}`;
      if (f.mode === "rent") {
        return [{ label: "najam", url: `https://www.njuskalo.hr/iznajmljivanje-stanova?${geo}&price%5Bmax%5D=${f.rentMax}` }];
      }
      return [{
        label: "prodaja",
        url: `https://www.njuskalo.hr/prodaja-stanova?${geo}`
          + `&price%5Bmin%5D=${f.priceMin}&price%5Bmax%5D=${f.priceMax}`
          + `&flatBuildingType=flat-in-residential-building`
          + `&livingArea%5Bmin%5D=${f.m2Min}`
          + (f.m2Max ? `&livingArea%5Bmax%5D=${f.m2Max}` : ""),
      }];
    },
  },
  {
    name: "Index oglasi",
    rentSupported: false,
    build: (f) => ids(f.njuskaloIds).map((id) => ({
      label: `kvart ${id}`,
      url: `https://www.index.hr/oglasi/prodaja-stanova/gid/3278`
        + `?pojamZup=1153&tipoglasa=1&sortby=1&elementsNum=10&grad=${id}&naselje=0`
        + `&attr_Int_988=${f.m2Min}&attr_Int_887=${f.m2Max}`
        + `&cijenaod=${f.priceMin}&cijenado=${f.priceMax}`,
    })),
  },
  {
    name: "Oglasnik",
    rentSupported: false,
    build: (f) => [{
      label: "prodaja",
      url: `https://www.oglasnik.hr/stanovi-prodaja`
        + `?ad_params_44_from=${f.m2Min}&ad_price_to=${f.priceMax}&ad_location_2%5B%5D=7442`
        + ids(f.oglasnikIds).map((id, i) => `&ad_location_3%5B${i}%5D=${id}`).join(""),
    }],
  },
];

const STORAGE_KEY = "web_scraper.filters";
const form = document.getElementById("filters");
const results = document.getElementById("results");

function loadFilters() {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") };
  } catch {
    return { ...DEFAULTS };
  }
}

function readForm() {
  return Object.fromEntries(new FormData(form));
}

function fillForm(filters) {
  for (const [key, value] of Object.entries(filters)) {
    const field = form.elements[key];
    if (field) field.value = value;
  }
}

function currentLinks(filters) {
  return SITES
    .filter((site) => filters.mode !== "rent" || site.rentSupported !== false)
    .map((site) => ({ name: site.name, links: site.build(filters) }));
}

function render() {
  const filters = readForm();
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(filters)); } catch {}
  document.body.dataset.mode = filters.mode;

  results.replaceChildren(...currentLinks(filters).map(({ name, links }) => {
    const section = document.createElement("section");
    const heading = document.createElement("h2");
    heading.textContent = name;
    const list = document.createElement("ul");
    for (const { label, url } of links) {
      const item = document.createElement("li");
      const a = document.createElement("a");
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = label;
      item.append(a);
      list.append(item);
    }
    section.append(heading, list);
    return section;
  }));
}

document.getElementById("open-all").addEventListener("click", () => {
  // browsers block all but the first popup unless popups are allowed for this page
  for (const { links } of currentLinks(readForm())) {
    for (const { url } of links) window.open(url, "_blank", "noopener");
  }
});

document.getElementById("reset").addEventListener("click", () => {
  fillForm(DEFAULTS);
  render();
});

form.addEventListener("input", render);
fillForm(loadFilters());
render();
