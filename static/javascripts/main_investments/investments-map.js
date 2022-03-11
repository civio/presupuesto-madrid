function InvestmentsMap (_mapSelector, _legendSelector, data, _token) {
  mapboxgl.accessToken = _token
  const mapNode = document.querySelector(`#${_mapSelector}`)
  const legendNode = document.querySelector(`#${_legendSelector}`)
  const map = new mapboxgl.Map({
    container: _mapSelector,
    center: [-3.7, 40.42], // starting position [lng, lat]
    zoom: 11,
    style: "mapbox://styles/civio/ckrakezmj2gfp18p9j8z2bg3j",
    scrollZoom: false
  })
  const denominations = [...new Set([...data.map(d => d["DENOMINACIÓN LÍNEA DE INVERSIÓN"])])]
  const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(denominations)
  let hoveredStateId = null
  let denominationSelected
  let stateSelected
  let yearSelected
  const filters = {
    denomination: ["all"],
    state: ["all"],
    year: ["all"],
    name: ["all"]
  }
  // Create map object
  this.setup = function () {
    map.on("load", () => {
      map.addControl(new mapboxgl.NavigationControl());
      setupLayers()
      setupLegend()
      setupStateButtons()
      setupInputText()
    })
  }
  function setupLayers() {
    const investments = {
      type: "FeatureCollection",
      features: []
    };
    data.forEach((d, i) => {
      if (d.Longitud !== "") {
        investments.features.push({
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [Number(d.Longitud), Number(d.Latitud)]
          },
          properties: d,
          id: i 
        });
      }
    });
    // Create map SOURCES
    // Districts polygons
    map.addSource("geojsonPolyg", {
      type: "geojson",
      data: CARTOGRAPHY
    })
    // Investments circles
    map.addSource("geojsonPoints", {
      type: "geojson",
      data: investments
    })
    // Create  LAYERS
    // Polygons borders (distritos)
    map.addLayer({
      id: "geojsonLayer-outline",
      type: "line",
      source: "geojsonPolyg",
      paint: {
        "line-color": "#a4cdf4",
        "line-width": 3,
        "line-opacity": 0.8
      }
    });
    // Polygons names (distritos)
    // https://docs.mapbox.com/mapbox-gl-js/example/geojson-markers/
    map.addLayer({
      id: 'geojsonLayer-text',
      type: 'symbol',
      source: "geojsonPolyg",
      layout: {
        'text-field': ['get', 'NOMBRE'],
        'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
        //'text-offset': [0, 1.25],
        //'text-anchor': 'top',
        'text-size': 14 // Defaults to 16
      },
      paint: {
        'text-opacity': 0.9,
        'text-color': "#4d4d4d"
      }
    });
    // Paint the circle layer for each denomination
    var circleColor = [
      "match",
      ["get", "DENOMINACIÓN LÍNEA DE INVERSIÓN"]
    ];
    denominations.forEach(d => { circleColor.push(d); circleColor.push(colorScale(d)) });
    circleColor.push("#003DF6"); // Fallback
    map.addLayer({
      id: "geojsonLayer-points",
      type: "circle",
      source: "geojsonPoints",
      paint: {
        "circle-radius": [
          'case',
          ['boolean', ['feature-state', 'search'], true],
          6,
          0
        ],
        "circle-stroke-width": [
          'case',
          ['boolean', ['feature-state', 'hover'], false],
          2,
          0
        ],
        "circle-stroke-color": "#000",
        "circle-color": circleColor
      }
    })
    // Create tooltip
      const tooltipNode = document.createElement("div")
      tooltipNode.setAttribute("id", "tooltip")
      tooltipNode.classList.add("map-overlay-inner")
      mapNode.append(tooltipNode)
    // Bind events for the layer
    map.on("mousemove", "geojsonLayer-points", e => {
      showTooltip(e, 'mouseenter')
      map.getCanvas().style.cursor = 'pointer'
    });
    map.on("mouseleave", "geojsonLayer-points", e => {
      map.getCanvas().style.cursor = ''
      hideTooltip("mouseenter")
    });
    map.on("click", "geojsonLayer-points", e => {
      showTooltip(e, 'click')
    });;
  }
  function showTooltip (e, className) {
    const obj = e.features[0].properties;
    if (hoveredStateId !== null) {
      map.setFeatureState(
        { source: 'geojsonPoints', id: hoveredStateId },
        { hover: false }
      );
    }
    hoveredStateId = e.features[0].id;
    map.setFeatureState(
      { source: 'geojsonPoints', id: hoveredStateId },
      { hover: true }
    );
    const html = `<div id="tooltip-wrapper">
          <span id="tooltip-close-button">X</span>
      <h3>${obj.Denominación}</h3>
      <div class="tooltip-section tooltip-location">
        <div>Dirección: ${obj["Dirección"]}</div>
        <div>Distrito: ${obj["Denominación Distrito"]}</div>
      </div>
      <div class="tooltip-section tooltip-denomination">
        <span class="tooltip-denomination-marker" style="background-color: ${colorScale(
          obj["DENOMINACIÓN LÍNEA DE INVERSIÓN"]
        )}"></span>
        <span>${obj["DENOMINACIÓN LÍNEA DE INVERSIÓN"]}</span>
      </div>
      <table class="tooltip-section tooltip-times">
        <tr><td>Año inicio</td><td>${obj["Año inicio"]}</td></tr>
        <tr>${obj["Año de finalización"]!=="" ? `<td>Año de finalización</td><td>${
          obj["Año de finalización"]
        }</td>`: `<td>Año finalización previsto</td><td>${
          obj["Año de finalización previsto"]
        }</td>`}</tr>
      </table>
      <table class="tooltip-section tooltip-award">
        <tr><th>Importes</th><th></th></tr>
        <tr><td>Gasto ya ejecutado</td><td>${Math.round(
          Number(obj["Gasto ejecutado"])
        ).toLocaleString("es-ES")} €</td></tr>
        <tr><td>Presupuesto inicial (2021)</td><td>${Math.round(
          Number(obj["Importe 2021"])
        ).toLocaleString("es-ES")} €</td></tr>
        <tr><td>Anualidades futuras</td><td>${Math.abs(
          Math.round(
            Number(obj["Total previsto"]) - Number(obj["Gasto ejecutado"]) - Number(obj["Importe 2021"])
          )
        ).toLocaleString("es-ES")}
           €</td></tr>
        <tr><td>Presupuesto total previsto</td><td>${Math.round(
          Number(obj["Total previsto"])
        ).toLocaleString("es-ES")} €</td></tr>
      </table>
      ${ obj["img"] ? `<img src="${ obj["img"] }"` : ""}
    </div>
    `;
    document.querySelector("#tooltip").innerHTML = html
    document.querySelector("#tooltip").classList.add(className)
    document.querySelector("#tooltip-close-button").addEventListener("click", (e) => {
      hideTooltip("click")
    })
  }
  function hideTooltip (className) {
    document.querySelector("#tooltip").classList.remove(className)
    if (hoveredStateId !== null) {
      map.setFeatureState(
        { source: 'geojsonPoints', id: hoveredStateId },
        { hover: false }
      );
    }
    hoveredStateId = null
  }
  function setupLegend() {
    // Create H3 legend
    const legendH3 = document.createElement("h3")
    legendH3.setAttribute("id", "investments-viz-legend-title")
    const legendH3Text = document.createTextNode("Líneas de inversion")
    legendH3.append(legendH3Text)
    // Create UL legend 
    const legendUl = document.createElement("ul")
    legendUl.setAttribute("id", "investments-viz-legend-filter")
    // Append both elements
    legendNode.append(legendH3)
    legendNode.append(legendUl)

    // Create legend with filters
    denominations.forEach(d => {
      // Create HTML elements
      const node = document.createElement("li")
      node.classList.add("investments-viz-legend-filter-item")
      node.setAttribute("data-value", d) 
      const color = document.createElement("span")
      color.style.borderColor = colorScale(d)
      color.style.backgroundColor = colorScale(d)
      node.append(color)
      const textNode = document.createTextNode(d.substring(0, 1) + d.slice(1).toLowerCase())
      node.appendChild(textNode)
      // Bind event to denomination buttons
      node.addEventListener("click", (e) => {
        const denominationItems = document.querySelectorAll(".investments-viz-legend-filter-item")
        const dataValue = e.target.getAttribute("data-value")
        denominationItems.forEach(el => {
          // Toggle active (for selected) and unactive (for unselected) class from legend elements
          if (el.getAttribute("data-value") !== dataValue) {
            el.classList.remove("active")
            el.classList.add("inactive")
          } else {
            // Set filter and toggle the background of the circle of
            // the legend
            if (denominationSelected !== dataValue) {
              document.querySelector("#investments-viz-legend-filter").classList.add("active")
              el.classList.add("active")
              el.classList.remove("inactive")
              denominationSelected = dataValue
              filters.denomination = ["==", ["get", "DENOMINACIÓN LÍNEA DE INVERSIÓN"], dataValue]
            } else {
              document.querySelector("#investments-viz-legend-filter").classList.remove("active")
              el.classList.remove("active")
              el.classList.add("inactive")
              denominationSelected = "all"
              filters.denomination = [denominationSelected]
            }
          }
        })
        filterMap()
      })
      document.querySelector("#investments-viz-legend-filter").appendChild(node)
    })
  }
  function setupStateButtons() {
    // Create container with filter elements
    const filterStateNode = document.createElement("div")
    filterStateNode.setAttribute("id", "investments-viz-filter-state-wrapper")
    filterStateNode.classList.add("investments-viz-filter")

    // Create filter h3
    const filterStateTitle = document.createElement("h3")
    const titleTextNode = document.createTextNode("SITUACIÓN DE LA INVERSION")
    filterStateTitle.append(titleTextNode)
    filterStateNode.append(filterStateTitle)

    // Create filter list element 
    const filterStateList = document.createElement("ul")
    filterStateList.setAttribute("id", "investments-viz-filter-state")
    filterStateNode.append(filterStateList)
    
    // Append HTML elements
    mapNode.append(filterStateNode)
    // Create buttons with filter of state
    const states = [...new Set([...data.map(d => d["Estado"])])]
    states.forEach(d => {
      // Create HTML elements
      const li = document.createElement("li")
      const a = document.createElement("a")
      a.href = "#"
      const div = document.createElement("div")
      div.classList.add("tr")
      li.appendChild(a)
      li.appendChild(div)
      li.classList.add("investments-viz-filter-state-item")
      li.setAttribute("data-value", d)
      const textNode = document.createTextNode(d)
      a.appendChild(textNode)
      // Bind event to state buttons
      li.addEventListener("click", (e) => {
        const stateItems = document.querySelectorAll(".investments-viz-filter-state-item")
        const dataValue = e.target.getAttribute("data-value")
        // Remove active class from all elements except the selected one
        stateItems.forEach(el => {
          if (el.getAttribute("data-value") !== dataValue) {
            el.classList.remove("active")
          } else {
            el.classList.toggle("active")
          }
        })
        // Set filter value
        if (stateSelected !== dataValue) {
          stateSelected = dataValue
          filters.state = ["==", ["get", "Estado"], stateSelected]
        } else {
          stateSelected = "all"
          filters.state = [stateSelected]
        }
        filterMap()
      })
      document.querySelector("#investments-viz-filter-state").appendChild(li)
    })
  }
  function filterMap() {
    map.setFilter("geojsonLayer-points", ["all",
      filters.denomination,
      filters.state,
      filters.year
    ]);
  }
  function setupInputText() {
    // Create input text container
    const inputTextContainer = document.createElement("div")
    inputTextContainer.classList.add("investments-viz-filter-searcher")

    // Create input text element
    const inputTextNode = document.createElement("input")
    inputTextNode.setAttribute("type", "text")
    inputTextNode.setAttribute("id", "investments-viz-filter-searcher-input")
    inputTextNode.setAttribute("placeholder", "Busca por nombre o distrito")

    inputTextContainer.append(inputTextNode)

    mapNode.append(inputTextContainer)

    // Bind event to input search
    document.querySelector('#investments-viz-filter-searcher-input').addEventListener("keyup", (e) => {
      const value = formatStr(e.target.value)
      const renderedPoints = map.queryRenderedFeatures(
        { layers: ['geojsonLayer-points'] }
      );
      let search = false
      // Format text that user insert
      renderedPoints.forEach(d => {
        if (formatStr(d.properties["Denominación"]).includes(value) ||
          formatStr(d.properties["Denominación Distrito"]).includes(value)){
          search = true 
        } else {
          search = false
        }
        map.setFeatureState(
          { source: 'geojsonPoints', id: d.id },
          { search: search }
        );
      })
      function formatStr(str) {
        return str
          .trim()
          .toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
      }
    })
  }
}
