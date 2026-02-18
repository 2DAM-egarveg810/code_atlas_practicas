(function () {
    "use strict";

    // === Configuracion ===
    const GEOM_FIELD = "point";
    const DEFAULT_CENTER = [40.4167, -3.7037]; // Madrid
    const DEFAULT_ZOOM = 6;
    const USE_BBOX = false;  // false = cargar todos, true = filtrar por vista
    const FIT_BOUNDS_ON_LOAD = true;
    const URL_NEW_SNIPPET = "/snippets/new/";

    // Colores por lenguaje
    const LANG_COLORS = {
        'python': '#3776ab', 'javascript': '#f7df1e', 'typescript': '#3178c6',
        'html': '#e34c26', 'css': '#264de4', 'django': '#092e20',
        'sql': '#336791', 'java': '#007396', 'php': '#777bb4',
        'kotlin': '#7f52ff', 'markdown': '#083fa1'
    };
    const DEFAULT_COLOR = '#6c757d';

    // === Variables ===
    let map, layerGroup, geoLayer;

    // === Helpers ===
    function log(msg) {
        const el = document.getElementById('statusText');
        if (el) el.textContent = String(msg);
        console.log('[Map]', msg);
    }

    function getColorForLanguage(lang) {
        return LANG_COLORS[lang] || DEFAULT_COLOR;
    }

    // ej: 15 feb 2024
    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const d = new Date(dateStr);
            return d.toLocaleDateString('es-ES', {year: 'numeric', month: 'short', day: 'numeric'});
        } catch {
            return dateStr;
        }
    }

    // === Inicializacion del Mapa ===
    function initMap() {
        map = L.map("map", {
            center: DEFAULT_CENTER,
            zoom: DEFAULT_ZOOM,
            zoomControl: true,
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        layerGroup = L.layerGroup().addTo(map);

        setTimeout(() => map.invalidateSize(), 100);

        log("Mapa inicializado");
    }

    // === Estilo de los puntos ===
    function styleFeature(feature) {
        return {
            weight: 2,
            opacity: 1,
            color: '#fff',
            fillOpacity: 0.3,
        };
    }

    // Convierte cada punto en un circleMarker
    function pointToLayer(feature, latlng) {
        const lang = feature.properties?.language;
        const color = getColorForLanguage(lang);

        return L.circleMarker(latlng, {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85,
        });
    }

    // === Popup ===
    function onEachFeature(feature, layer) {
        const p = feature.properties || {};

        const popupContent = `
      <div class="snippet-popup">
        <div class="title">${p.title || 'Sin título'}</div>
        <span class="lang-badge" style="background-color: ${getColorForLanguage(p.language)}">
          ${p.language || 'unknown'}
        </span>
        ${p.description ? `<div class="description">${p.description}</div>` : ''}
        <hr class="my-2">
        <div class="meta">
          <div> ${p.author.username || 'Anónimo'}</div>
          <div> ${formatDate(p.pub_date)}</div>
          <div> ${p.cont_visited || 0} visitas</div>
        </div>
      </div>
    `;

        layer.bindPopup(popupContent);
    }

    // === Construir parametros de consulta ===
    // Si USE_BBOX es true, devuelve un string con los limites del mapa visible
    function buildParams() {
        if (!USE_BBOX) return {};
        const b = map.getBounds();
        return {
            bbox: [
                b.getWest().toFixed(6),
                b.getSouth().toFixed(6),
                b.getEast().toFixed(6),
                b.getNorth().toFixed(6),
            ].join(","),
        };
    }

    // === Generar Leyenda ===
    function generateLegend(features) {
        const counts = {};
        features.forEach(f => {
            const lang = f.properties?.language;
            if (lang) counts[lang] = (counts[lang] || 0) + 1;
        });

        const container = document.getElementById('legendContainer');
        if (!container) return;

        if (Object.keys(counts).length === 0) {
            container.innerHTML = '<small class="text-muted">Sin datos</small>';
            return;
        }

        let html = '';
        Object.entries(counts).sort((a, b) => b[1] - a[1]).forEach(([lang, count]) => {
            html += `
        <div class="legend-item">
          <span class="legend-dot" style="background-color: ${getColorForLanguage(lang)}"></span>
          <span><strong>${lang}</strong> <small class="text-muted">(${count})</small></span>
        </div>
      `;
        });
        container.innerHTML = html;
    }

    // Al hacer clic en el mapa obtiene coordenadas con 6 decimales y redirige para crear el snippet
    function onMapClick(e) {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);

        console.log(`Click en mapa: lat=${lat}, lng=${lng}`);

        // Formato: /snippets/new/?lat=XX.XXXXXX&lng=YY.YYYYYY
        const redirectUrl = `${URL_NEW_SNIPPET}?lat=${lat}&lng=${lng}`;
        window.location.href = redirectUrl;
    }

    // === Cargar GeoJSON ===
    function loadGeoJSON() {
        log("Cargando GeoJSON...");

        $.ajax({
            url: URL_GEOJSON,
            method: "GET",
            dataType: "json",
            data: buildParams(), // Parametros bbox si USE_BBOX=true
            timeout: 15000,
        }).done(function (data) {
            layerGroup.clearLayers(); // Limpia marcadores anteriores

            // Validar estructura GeoJSON
            if (!data || !Array.isArray(data.features)) {
                log("Respuesta inválida");
                return;
            }

            geoLayer = L.geoJSON(data, {
                style: styleFeature,
                pointToLayer: pointToLayer,
                onEachFeature: onEachFeature,
            }).addTo(layerGroup);

            // Actualizar contador total
            const count = data.features.length;
            document.getElementById('totalCount').textContent = count;

            // Generar leyenda
            generateLegend(data.features);
            log(`Cargados ${count} snippets`);

            // Ajusta el zoom a los datos si hay
            if (FIT_BOUNDS_ON_LOAD && count > 0) {
                try {
                    map.fitBounds(geoLayer.getBounds(), {padding: [30, 30]});
                } catch (e) {
                    console.warn("No se pudo ajustar el zoom:", e);
                }
            }
        }).fail(function (xhr) {
            const msg = `Error ${xhr.status}: ${xhr.responseText || xhr.statusText}`;
            log("" + msg);
            console.error("GeoJSON load failed:", xhr);
            const container = document.getElementById('legendContainer');
            if (container) {
                container.innerHTML = `<small class="text-danger">Error al cargar</small>`;
            }
        });
    }

    // === Inicializacion ===
    $(document).ready(function () {
        // Crea el mapa
        initMap();

        // Registra clic para crear snippets
        map.on('click', onMapClick);

        // Carga y muestra los datos
        loadGeoJSON();

        // Si USE_BBOX=true, recarga datos al mover/zoomear el mapa
        if (USE_BBOX) {
            map.on("moveend", function () {
                loadGeoJSON();
            });
        }
    });

})();