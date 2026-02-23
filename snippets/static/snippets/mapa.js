(function () {
    "use strict";

    const GEOM_FIELD = "point";
    const DEFAULT_CENTER = [40.4167, -3.7037];
    const DEFAULT_ZOOM = 6;
    const USE_BBOX = false;
    const FIT_BOUNDS_ON_LOAD = true;
    const URL_NEW_SNIPPET = "/snippets/new/";

    const LANG_COLORS = {
        'python': '#3776ab', 'javascript': '#f7df1e', 'typescript': '#3178c6',
        'html': '#e34c26', 'css': '#264de4', 'django': '#092e20',
        'sql': '#336791', 'java': '#007396', 'php': '#777bb4',
        'kotlin': '#7f52ff', 'markdown': '#083fa1'
    };
    const DEFAULT_COLOR = '#6c757d';

    let map, layerGroup, geoLayer;

    /**
     * Helper para mostrar notificaciones con Swal.
     * @param {string} title - Título.
     * @param {string} text - Mensaje.
     * @param {'success'|'error'|'info'|'warning'} icon - Tipo de icono.
     * @param {number} timer - Tiempo en ms para autocierre (0 = sin autocierre).
     */
    function showAlert(title, text, icon = 'info', timer = 3000) {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: timer,
            timerProgressBar: true,
            // Prueba de listeners. Funciona perfe
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
        Toast.fire({icon, title, text});
    }

    /**
     * Helper para confirmar acciones.
     * @param {string} title - Título.
     * @param {string} text - Mensaje.
     * @param {string} confirmButtonText - Texto del botón confirmar.
     * @param {string} cancelButtonText - Texto del botón cancelar.
     * @returns {Promise<boolean>} Resuelve a true si se confirma, false si se cancela.
     */
    async function showConfirm(title, text, confirmButtonText = 'Sí', cancelButtonText = 'Cancelar') {
        const result = await Swal.fire({
            title,
            text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText,
            cancelButtonText,
            focusCancel: true
        });
        return result.isConfirmed;
    }

    function log(msg) {
        const el = document.getElementById('statusText');
        if (el) el.textContent = String(msg);
        console.log('[Map]', msg);
    }

    function getColorForLanguage(lang) {
        return LANG_COLORS[lang] || DEFAULT_COLOR;
    }

    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const d = new Date(dateStr);
            return d.toLocaleDateString('es-ES', {year: 'numeric', month: 'short', day: 'numeric'});
        } catch {
            return dateStr;
        }
    }

    function initMap() {
        map = L.map("map", {
            center: DEFAULT_CENTER,
            zoom: DEFAULT_ZOOM,
            zoomControl: true,
            pmIgnore: false
        });

        map.pm.addControls({
            position: 'topleft',
            drawMarker: true,
            drawCircleMarker: false,
            drawPolyline: false,
            drawPolygon: false,
            drawCircle: false,
            drawRectangle: false,
            editMode: true,
            removalMode: true,
            dragMode: true,
            rotateMode: false,
            cutPolygon: false,
            drawText: false,
        });

        map.pm.setLang('es', {
            tooltips: {
                placeMarker: 'Haz clic para colocar el snippet',
            }
        }, true);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        layerGroup = L.layerGroup().addTo(map);

        setTimeout(() => map.invalidateSize(), 100);

        map.pm.enableGlobalEditMode({
            allowEditing: true,
            allowDragging: true,
            allowRemoval: true,
        });
        log("Mapa inicializado con Geoman");
    }

    function styleFeature(feature) {
        return {
            weight: 2,
            opacity: 1,
            color: '#fff',
            fillOpacity: 0.3,
        };
    }

    /**
     * Convierte un punto GeoJSON en un CircleMarker con configuración interactiva.
     */
    function pointToLayer(feature, latlng) {
        const lang = feature.properties?.language;
        const color = getColorForLanguage(lang);
        const snippetId = feature.id;

        const marker = L.circleMarker(latlng, {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85,
            pmIgnore: false,
        });

        marker.feature = feature;

        marker.pm.setOptions({
            allowEditing: true,
            allowRemoval: true,
            draggable: true,
            allowDragging: true,
            preventMarkerRemoval: false,
        });

        marker.on('pm:dragend', async function (evento) {
            const nuevaLat = evento.target.getLatLng().lat.toFixed(6);
            const nuevaLng = evento.target.getLatLng().lng.toFixed(6);

            const confirmado = await showConfirm(
                'Guardar nueva ubicación',
                '¿Quieres actualizar las coordenadas de este snippet?'
            );

            if (confirmado) {
                const originalStyle = {
                    fillOpacity: marker.options.fillOpacity,
                    dashArray: marker.options.dashArray
                };
                marker.setStyle({fillOpacity: 0.5, dashArray: '3,3'});

                try {
                    const response = await fetch(`/snippets/api/snippets/${snippetId}/update_location/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({lat: nuevaLat, lng: nuevaLng})
                    });
                    const data = await response.json();

                    marker.setStyle(originalStyle);

                    if (data.success) {
                        showAlert('Ubicación actualizada', 'Las coordenadas se guardaron correctamente.', 'success');
                        log(`ID:${marker.feature.id}. Ubicación actualizada.`);
                    } else {
                        showAlert('Error al guardar', data.error || 'Error desconocido', 'error', 5000);
                        log("Error: " + (data.error || "Desconocido"));
                        loadGeoJSON();
                    }
                } catch (err) {
                    marker.setStyle(originalStyle);
                    showAlert('Error de conexión', 'No se pudo contactar con el servidor.', 'error', 5000);
                    log(`Error: ${err}`);
                    loadGeoJSON();
                }
            } else {
                loadGeoJSON();
            }
        });

        return marker;
    }

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
          <div> ${p.author || 'Anónimo'}</div>
          <div> ${formatDate(p.pub_date)}</div>
          <div> ${p.cont_visited || 0} visitas</div>
        </div>
        <div class="mt-2">
          <button class="btn btn-sm btn-outline-primary edit-coords-btn" 
                  data-id="${feature.id}"
                  data-lat="${layer.getLatLng().lat.toFixed(6)}"
                  data-lng="${layer.getLatLng().lng.toFixed(6)}">
            Editar coordenadas
          </button>
        </div>
      </div>
    `;

        layer.bindPopup(popupContent);

        layer.on('popupopen', function () {
            document.querySelectorAll('.edit-coords-btn').forEach(btn => {
                btn.onclick = function (e) {
                    e.stopPropagation();
                    openCoordinateEditor(this.dataset.id, this.dataset.lat, this.dataset.lng, layer);
                };
            });
        });
    }

    /**
     * Abre un popup con inputs para editar coordenadas manualmente.
     * Nota: Usa showAlert para errores de validación en lugar de alert().
     */
    function openCoordinateEditor(snippetId, currentLat, currentLng, layer) {
        layer.closePopup();

        const editorContent = `
      <div class="coord-editor">
        <h6>Editar coordenadas</h6>
        <div class="mb-2">
          <label>Latitud:</label>
          <input type="number" id="edit-lat" step="0.000001" 
                 value="${currentLat}" class="form-control form-control-sm">
        </div>
        <div class="mb-2">
          <label>Longitud:</label>
          <input type="number" id="edit-lng" step="0.000001" 
                 value="${currentLng}" class="form-control form-control-sm">
        </div>
        <div class="d-flex gap-2">
          <button id="save-coords" class="btn btn-primary btn-sm">Guardar</button>
          <button id="cancel-coords" class="btn btn-secondary btn-sm">Cancelar</button>
        </div>
        <small class="text-muted d-block mt-1">Formato: grados decimales (6 decimales)</small>
      </div>
    `;

        layer.bindPopup(editorContent).openPopup();

        document.getElementById('save-coords').onclick = async function () {
            const lat = parseFloat(document.getElementById('edit-lat').value);
            const lng = parseFloat(document.getElementById('edit-lng').value);

            if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                showAlert('Coordenadas inválidas', 'Latitud debe estar entre -90 y 90, longitud entre -180 y 180.', 'warning', 5000);
                return;
            }

            layer.setLatLng([lat, lng]);
            await saveCoordinates(snippetId, lat, lng, layer);
        };

        document.getElementById('cancel-coords').onclick = function () {
            onEachFeature(layer.feature, layer);
            layer.openPopup();
        };
    }

    /**
     * Guarda las coordenadas actualizadas en el backend via API.
     * Nota: Usa showAlert para feedback visual en lugar de alert().
     */
    async function saveCoordinates(snippetId, lat, lng, layer) {
        layer.bindTooltip('Guardando...', {permanent: true}).openTooltip();

        try {
            const response = await fetch(`/snippets/api/snippets/${snippetId}/update_location/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({lat: lat.toFixed(6), lng: lng.toFixed(6)})
            });
            const data = await response.json();

            layer.closeTooltip();

            if (data.success) {
                layer.bindTooltip('Actualizado', {direction: 'top'}).openTooltip();
                showAlert('Guardado', 'Ubicación actualizada correctamente.', 'success');
                setTimeout(() => {
                    layer.closeTooltip();
                    onEachFeature(layer.feature, layer);
                    layer.openPopup();
                }, 1000);
            } else {
                showAlert('Error', data.error || 'Error desconocido', 'error', 5000);
            }
        } catch (err) {
            layer.closeTooltip();
            console.error('Error:', err);
            showAlert('Error de conexión', 'No se pudo contactar con el servidor.', 'error', 5000);
        }
    }

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

    function onGeomanCreate(e) {
        const layer = e.layer;
        const latlng = layer.getLatLng();
        const lat = latlng.lat.toFixed(6);
        const lng = latlng.lng.toFixed(6);

        console.log(`Geoman creó marcador: lat=${lat}, lng=${lng}`);

        const redirectUrl = `${URL_NEW_SNIPPET}?lat=${lat}&lng=${lng}`;
        layer.remove();
        window.location.href = redirectUrl;
    }

    function loadGeoJSON() {
        log("Cargando GeoJSON...");

        $.ajax({
            url: URL_GEOJSON,
            method: "GET",
            dataType: "json",
            data: buildParams(),
            timeout: 15000,
        }).done(function (data) {
            layerGroup.clearLayers();

            if (!data || !Array.isArray(data.features)) {
                log("Respuesta inválida");
                showAlert('Datos inválidos', 'La respuesta del servidor no tiene el formato esperado.', 'error', 5000);
                return;
            }

            geoLayer = L.geoJSON(data, {
                style: styleFeature,
                pointToLayer: pointToLayer,
                onEachFeature: onEachFeature,
            }).addTo(layerGroup);

            const count = data.features.length;
            document.getElementById('totalCount').textContent = count;

            generateLegend(data.features);
            log(`Cargados ${count} snippets`);

            if (FIT_BOUNDS_ON_LOAD && count > 0) {
                try {
                    map.fitBounds(geoLayer.getBounds(), {padding: [30, 30]});
                } catch (e) {
                    console.warn("No se pudo ajustar el zoom:", e);
                }
            }
        }).fail(function (er) {
            const msg = `Error ${er.status}: ${er.responseText || er.statusText}`;
            log("" + msg);
            console.error("GeoJSON load failed:", er);
            const container = document.getElementById('legendContainer');
            if (container) {
                container.innerHTML = `<small class="text-danger">Error al cargar</small>`;
            }
            showAlert('Error de carga', 'No se pudieron cargar los snippets del mapa.', 'error', 5000);
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            for (let cookie of document.cookie.split(';')) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Punto de entrada: inicializa componentes y vincula eventos al cargar el DOM.
     * Nota: El evento pm:remove usa showConfirm para validar eliminación.
     */
    $(document).ready(async function () {
        initMap();

        map.on('pm:create', onGeomanCreate);

        map.on('pm:remove', async function (e) {
            const layer = e.layer;
            const snippetId = layer.feature?.id;

            if (!snippetId) return;

            const confirmado = await showConfirm(
                'Eliminar snippet',
                '¿Estás seguro de que quieres eliminar este snippet? Esta acción no se puede deshacer.'
            );

            if (!confirmado) {
                layer.addTo(layerGroup);
                return;
            }

            log('Eliminando snippet...');

            try {
                const response = await fetch(`/snippets/api/snippets/${snippetId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                const data = await response.json();

                if (data.success) {
                    const countEl = document.getElementById('totalCount');
                    countEl.textContent = Math.max(0, parseInt(countEl.textContent) - 1);
                    showAlert('Eliminado', 'Snippet eliminado correctamente.', 'success');
                    log('Snippet eliminado');
                } else {
                    showAlert('Error', data.error || 'Error desconocido', 'error', 5000);
                    log('Error: ' + (data.error || 'Desconocido'));
                    loadGeoJSON();
                }
            } catch (err) {
                console.error('Error en AJAX:', err);
                showAlert('Error de conexión', 'No se pudo eliminar el snippet.', 'error', 5000);
                log('Error de conexión');
                loadGeoJSON();
            }
        });

        loadGeoJSON();

        if (USE_BBOX) {
            map.on("moveend", loadGeoJSON);
        }
    });

})();