function InvestmentsMap(_mapSelector, _legendSelector, data, _token) {
	mapboxgl.accessToken = _token;
	const map = new mapboxgl.Map({
		container: _mapSelector,
		center: [-3.7, 40.42], // starting position [lng, lat]
		zoom: 11,
		style: 'mapbox://styles/civio/ckrakezmj2gfp18p9j8z2bg3j',
		scrollZoom: false,
	});
	let mapLoaded = false;

	const denominations = [
		...new Set([...data.map((d) => d.functional_category)]),
	];
	const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(denominations);

	let hoveredFeature = null;

	let selectedFunctionalCategory = 'all';
	let selectedStatus = 'all';
	let selectedYear = 'all';

	// Create map object
	this.setup = function () {
		const mapNode = document.querySelector(`#${_mapSelector}`);
		const legendNode = document.querySelector(`#${_legendSelector}`);
		map.on('load', () => {
			map.addControl(new mapboxgl.NavigationControl());
			map.addControl(new mapboxgl.FullscreenControl());
			setupLayers(mapNode);
			setupLegend(legendNode);
			setupStateButtons(mapNode);
			setupInputText(mapNode);

			mapLoaded = true;
			filterMap();
		});
	};

	this.selectYear = function (year) {

		// selectedYear = year
		// selectedYear = "2021"
		selectedYear = [2023, 2024]

		if (mapLoaded) {
			// If still loaded, filtering will happen once that's done
			filterMap();
		}

		// Try to update the tooltip, if stuck, if the selected investment exists across the years
		if (hoveredFeature !== null) {

			const pinProject = function () {
				if (Array.isArray(selectedYear)) {
					// console.log(data.filter(d => d.project_id === hoveredFeature.properties.project_id))
					return data.find(
						(d) =>
							d.year === selectedYear[1] &&
							d.project_id === hoveredFeature.properties.project_id
					);
				} else {
					return data.find(
						(d) =>
							d.year === selectedYear &&
							d.project_id === hoveredFeature.properties.project_id
					);
				}
			}

			const obj = pinProject()

			// console.log(data.filter(d => d.project_id === hoveredFeature.properties.project_id))
			// console.log(data.filter(d => d.project_id === hoveredFeature.properties.project_id).at(-1)[0])

			if (obj) {
				const tooltip = document.querySelector('#tooltip');
				populateTooltip(tooltip, obj); // The investment exists across the years
			} else {
				unstickTooltip(); // Nothing to show
			}
		}
	};

	function setupLayers(mapNode) {
		// Note that we generate separate features (i.e. points) for each year an investment
		// is active. We could reuse the same point for multiple years, reducing the number
		// of features, but the implementation is harder and it's just not that critical.
		const investments = {
			type: 'FeatureCollection',
			features: [],
		};
		data.forEach((d, i) => {
			if (d.longitude !== '') {
				investments.features.push({
					type: 'Feature',
					geometry: {
						type: 'Point',
						coordinates: [Number(d.longitude), Number(d.latitude)],
					},
					properties: d,
					id: i,
				});
			}
		});

		// Create map SOURCES
		// Districts polygons
		map.addSource('areas', {
			type: 'geojson',
			data: CARTOGRAPHY,
		});
		// Investments circles
		map.addSource('investments', {
			type: 'geojson',
			data: investments,
		});

		// Create LAYERS
		// Polygons borders (areas)
		map.addLayer({
			id: 'areasLayer',
			type: 'line',
			source: 'areas',
			paint: {
				'line-color': '#a4cdf4',
				'line-width': 3,
				'line-opacity': 0.8,
			},
		});

		// Polygons names (areas)
		// https://docs.mapbox.com/mapbox-gl-js/example/geojson-markers/
		map.addLayer({
			id: 'areaNamesLayer',
			type: 'symbol',
			source: 'areas',
			layout: {
				'text-field': ['get', 'NOMBRE'],
				'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
				'text-size': 14, // Defaults to 16
			},
			paint: {
				'text-opacity': 0.9,
				'text-color': '#4d4d4d',
			},
		});

		// Paint the circle layer for each denomination
		var circleColor = ['match', ['get', 'functional_category']];
		denominations.forEach((d) => {
			circleColor.push(d);
			circleColor.push(colorScale(d));
		});
		circleColor.push('#003DF6'); // Fallback
		map.addLayer({
			id: 'investmentsLayer',
			type: 'circle',
			source: 'investments',
			paint: {
				'circle-radius': [
					'case',
					['boolean', ['feature-state', 'search'], true],
					6,
					0,
				],
				'circle-stroke-width': [
					'case',
					['boolean', ['feature-state', 'hover'], false],
					2,
					0,
				],
				'circle-stroke-color': '#000',
				'circle-color': circleColor,
			},
		});

		// Create tooltip
		const tooltipNode = document.createElement('div');
		tooltipNode.setAttribute('id', 'tooltip');
		tooltipNode.classList.add('map-overlay-inner');
		mapNode.append(tooltipNode);

		// Bind events for the layer
		map.on('mousemove', 'investmentsLayer', (e) => {
			showTooltip(e);
			map.getCanvas().style.cursor = 'pointer';
		});
		map.on('mouseleave', 'investmentsLayer', (e) => {
			map.getCanvas().style.cursor = '';
			hideTooltip();
		});
		map.on('click', 'investmentsLayer', (e) => {
			stickTooltip(e);
		});
	}

	function populateTooltip(tooltip, obj) {
		function formatAmount(amount) {
			return Math.round(amount).toLocaleString('es-ES') + ' €';
		}

		const html = `<div id="tooltip-wrapper">
        <span id="tooltip-close-button">X</span>
        <h3>${obj.description}</h3>
        <div class="tooltip-section tooltip-location">
          <div>Dirección: ${obj.address}</div>
          <div>Distrito: ${obj.area_name}</div>
        </div>
        <div class="tooltip-section tooltip-denomination">
          <span class="tooltip-denomination-marker" style="background-color: ${colorScale(obj.functional_category)}"></span>
          <span>${obj.functional_category}</span>
        </div>
        <table class="tooltip-section tooltip-times">
          <tr>
            <td>Año inicio</td>
            <td>${obj.start_year}</td>
          </tr>
          <tr>
            ${obj.actual_end_year !== ''
				? `<td>Año de finalización</td><td>${obj.actual_end_year}</td>`
				: `<td>Año finalización previsto</td><td>${obj.expected_end_year}</td>`
			}
          </tr>
        </table>
        <table class="tooltip-section tooltip-award">
          <tr><th>Importes en ${obj.year}</th><th></th></tr>
          <tr>
            <td>Gasto ya ejecutado</td>
            <td>${formatAmount(Number(obj.already_spent_amount))}</td>
          </tr>
          <tr>
            <td>Presupuesto año en curso</td>
            <td>${formatAmount(Number(obj.current_year_amount))}</td>
          </tr>
          <tr>
            <td>Anualidades futuras</td>
            <td>${formatAmount(
				Math.abs(
					Number(obj.total_expected_amount) -
					Number(obj.already_spent_amount) -
					Number(obj.current_year_amount)
				)
			)}</td>
          </tr>
          <tr>
            <td>Presupuesto total previsto</td>
            <td>${formatAmount(Number(obj.total_expected_amount))}</td>
          </tr>
        </table>
        ${obj.image_URL ? `<img src="${obj.image_URL}"` : ''}
      </div>`;
		tooltip.innerHTML = html;

		document
			.querySelector('#tooltip-close-button')
			.addEventListener('click', (e) => {
				unstickTooltip();
			});
	}

	function setFeatureHover(feature_id, hover) {
		map.setFeatureState(
			{ source: 'investments', id: feature_id },
			{ hover: hover }
		);
	}

	// custom method to find the last update of a project
	function tooltipInfo() {
		if (Array.isArray(selectedYear)) {
			const projects = data.filter(d => d.project_id === hoveredFeature.properties.project_id)
			return projects.at(-1)
		} else {
			return hoveredFeature.properties
		}
	}

	function showTooltip(e) {
		if (hoveredFeature !== null) {
			setFeatureHover(hoveredFeature.id, false);
		}
		hoveredFeature = e.features[0];
		setFeatureHover(hoveredFeature, true);

		const tooltip = document.querySelector('#tooltip');
		console.log(data.filter(d => d.project_id === hoveredFeature.properties.project_id))
		populateTooltip(tooltip, tooltipInfo());
		tooltip.classList.add('hover');
	}

	function hideTooltip() {
		document.querySelector('#tooltip').classList.remove('hover');
		if (hoveredFeature !== null) {
			setFeatureHover(hoveredFeature, false);
		}

		// XXX: We used to delete hoveredFeature here, but it's useful to remember what was
		// the last hovered point when the tooltip is stuck and we change years. We could
		// store that in a separate state variable, but setting hover to false again and
		// again is not a big deal.
	}

	function stickTooltip() {
		document.querySelector('#tooltip').classList.add('click');
	}

	function unstickTooltip() {
		document.querySelector('#tooltip').classList.remove('click');
	}

	function setupLegend(legendNode) {
		// Create H3 legend
		const legendH3 = document.createElement('h3');
		legendH3.setAttribute('id', 'investments-viz-legend-title');
		legendH3.append(document.createTextNode('Líneas de inversion'));
		legendNode.append(legendH3);

		// Create UL legend
		const legendUl = document.createElement('ul');
		legendUl.setAttribute('id', 'investments-viz-legend-filter');
		legendNode.append(legendUl);

		// Create legend with filters
		denominations.forEach((d) => {
			// Create HTML elements
			const node = document.createElement('li');
			node.classList.add('investments-viz-legend-filter-item');
			node.setAttribute('data-value', d);

			const color = document.createElement('span');
			color.style.borderColor = colorScale(d);
			color.style.backgroundColor = colorScale(d);
			node.append(color);

			const textNode = document.createTextNode(
				d.substring(0, 1) + d.slice(1).toLowerCase()
			);
			node.appendChild(textNode);

			// Bind event to denomination buttons
			node.addEventListener('click', (e) => {
				const denominationItems = document.querySelectorAll(
					'.investments-viz-legend-filter-item'
				);
				const dataValue = [e.target.getAttribute('data-value')];

				const labelsInactives = document.querySelectorAll(
					'.investments-viz-legend-filter-item.inactive'
				).length;

				// 3 possible states
				// 1. Default: all active. Desactivate all labels except clicked if there's no labels inactives
				if (labelsInactives === 0) {
					// Visually
					denominationItems.forEach((el) => {
						el.classList.add('inactive');
						e.target.classList.remove('inactive');
					});
					// Filter values
					document
						.querySelector('#investments-viz-legend-filter')
						.classList.add('active');
					selectedFunctionalCategory = dataValue;
				}

				// 2. Activate all labels if there's only one label active & we are going to desactivate
				else if (
					labelsInactives === denominationItems.length - 1 &&
					!d3.select(e.target).classed('inactive')
				) {
					denominationItems.forEach((el) => {
						el.classList.remove('inactive');
					});
					selectedFunctionalCategory = 'all';
				}

				// 3. Toogle inactive value
				else {
					const thisEl_isActive = !d3.select(e.target).classed('inactive');
					d3.select(e.target).classed('inactive', thisEl_isActive);

					thisCategory = d3.select(e.target).attr('data-value');
					if (!e.target.classList.contains('inactive')) {
						selectedFunctionalCategory.push(thisCategory);
					} else {
						selectedFunctionalCategory = selectedFunctionalCategory.filter((item) => item !== thisCategory);
					}

				}
				filterMap();

				unstickTooltip(); // Hide if open, as the clicked item may disappear
			});
			document
				.querySelector('#investments-viz-legend-filter')
				.appendChild(node);
		});
	}

	function setupStateButtons(mapNode) {
		// Create container with filter elements
		const filterStateNode = document.createElement('div');
		filterStateNode.setAttribute('id', 'investments-viz-filter-state-wrapper');
		filterStateNode.classList.add('investments-viz-filter');

		// Create filter h3
		const filterStateTitle = document.createElement('h3');
		filterStateTitle.append(
			document.createTextNode('SITUACIÓN DE LA INVERSION')
		);
		filterStateNode.append(filterStateTitle);

		// Create filter list element
		const filterStateList = document.createElement('ul');
		filterStateList.setAttribute('id', 'investments-viz-filter-state');
		filterStateNode.append(filterStateList);

		// Append HTML elements
		mapNode.append(filterStateNode);

		// Create buttons with filter of state
		const states = [...new Set([...data.map((d) => d.status)])];
		states.forEach((d) => {
			// Create HTML elements
			const li = document.createElement('li');
			li.classList.add('investments-viz-filter-state-item');
			li.setAttribute('data-value', d);

			const a = document.createElement('a');
			a.href = '#';
			a.appendChild(document.createTextNode(d));
			li.appendChild(a);

			const div = document.createElement('div');
			div.classList.add('tr');
			li.appendChild(div);

			// Bind event to state buttons
			li.addEventListener('click', (e) => {
				const stateItems = document.querySelectorAll(
					'.investments-viz-filter-state-item'
				);
				const dataValue = e.target.getAttribute('data-value');

				// Remove active class from all elements except the selected one
				stateItems.forEach((el) => {
					if (el.getAttribute('data-value') !== dataValue) {
						el.classList.remove('active');
					} else {
						el.classList.toggle('active');
					}
				});

				// Set filter value
				if (selectedStatus !== dataValue) {
					selectedStatus = dataValue;
				} else {
					selectedStatus = 'all';
				}
				filterMap();

				unstickTooltip(); // Hide if open, as the clicked item may disappear
			});
			document.querySelector('#investments-viz-filter-state').appendChild(li);
		});
	}

	function filterMap() {
		function getFilter(field, values) {
			if (values === 'all') {
				return ['all'];
			}
			if (Array.isArray(values)) {
				if (field === 'year') {
					const rango = d3.range(values[0], values[1]).map(d => d.toString()).concat(values[1].toString())
					return ['in', field, ...rango]
				} else return ['in', field, ...values]; // Use the field name directly
			}
			return ['==', field, values]; // Use the field name directly
		}

		map.setFilter('investmentsLayer', [
			'all',
			getFilter('functional_category', selectedFunctionalCategory),
			getFilter('status', selectedStatus),
			getFilter('year', selectedYear),
		]);
	}

	// Go through all the features (not just the visible ones), setting a property indicating
	// whether they match the search query. Since the property is set and remains there,
	// we don't need to call this again when changing year or category or other filters.
	// (The alternative would be to iterate through visible features, but then we have to
	// keep calling this all the time, and there was some race condition or something
	// generating some weird behaviour I couldn't fix easily.)
	function filterSearchResults(searchQuery) {
		const sourceFeaturs = map.querySourceFeatures('investments');
		sourceFeaturs.forEach((d) => {
			let search =
				normalizeString(d.properties.description).includes(searchQuery) ||
				normalizeString(d.properties.area_name).includes(searchQuery);
			map.setFeatureState(
				{ source: 'investments', id: d.id },
				{ search: search }
			);
		});
	}

	function setupInputText(mapNode) {
		// Create input text container
		const inputTextContainer = document.createElement('div');
		inputTextContainer.classList.add('investments-viz-filter-searcher');

		// Create input text element
		const inputTextNode = document.createElement('input');
		inputTextNode.setAttribute('type', 'text');
		inputTextNode.setAttribute('id', 'investments-viz-filter-searcher-input');
		inputTextNode.setAttribute('placeholder', 'Busca por nombre o distrito');

		// Every input needs a label
		const labelNode = document.createElement('label');
		labelNode.setAttribute('for', 'investments-viz-filter-searcher-input');
		labelNode.classList.add('visually-hidden');
		labelNode.innerHTML = 'Busca por nombre o distrito';

		inputTextContainer.append(labelNode);
		inputTextContainer.append(inputTextNode);

		mapNode.append(inputTextContainer);

		// Bind event to input search
		document
			.querySelector('#investments-viz-filter-searcher-input')
			.addEventListener('keyup', (e) => {
				filterSearchResults(normalizeString(e.target.value));
				unstickTooltip(); // Hide if open, as the clicked item may disappear
			});
	}

	function normalizeString(str) {
		return str
			.trim()
			.toLowerCase()
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '');
	}
}
