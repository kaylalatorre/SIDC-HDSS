/**
 * Helper function to prepare AJAX functions with CSRF middleware tokens.
 * This avoids getting 403 (Forbidden) errors.
 */
function ajaxCSRF() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
}

$(document).ready(async function () {
    console.log($('#map-container').length);
    if ($('#map-container').length) {
        /**
         * Initialize map view
         */
        console.log("loading map...");
        // set view to batangas
        var lat = 13.882406389460293;
        var long = 121.23650234971542;
        var zoom = 11;

        // initialize map
        var map = L.map('map-container').setView([lat, long], zoom);
        console.log(map.getZoom());
        // initialize osm tile layer
        var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        var carto = L.tileLayer(
            'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
            {
              attribution:
                '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }
          ).addTo(map);

        console.log("map loaded");

        /**
         * Populate map
         */
        ajaxCSRF();
        metadata = await $.ajax({
            type: 'POST',
            url: '/map-data',
            success: function (response) {
                return response;
            }
        });

       console.log(metadata);
        // initialize layer groups
        var allFarms = new L.layerGroup();
        var farmsRadius = new L.layerGroup();
        var pigsPerFarm = new L.layerGroup();
        var mortalities = new L.layerGroup();
        var symptoms = new L.layerGroup();

        var pigData = [];
        var mortData = [];
        var sxData = [];

        // add markers and popups to layer groups
        for (let i = 0; i < metadata.length; i++) {
            if(!(metadata[i]['latitude'] && metadata[i]['longitude']))
                continue;

            let farmLat = metadata[i]['latitude'];
            let farmLong = metadata[i]['longitude'];
            let numPigs = metadata[i]['numPigs'];
            let mortRts = metadata[i]['mortRts'];
            let morts = metadata[i]['morts'];
            let sxRept = metadata[i]['sxRept'];
            let sxActv = metadata[i]['sxActv'];

            // Approximate distance of 100 meteres
            // Approximate Metric Equivalents for Degrees, Minutes, and Seconds: https://www.usna.edu/Users/oceano/pguth/md_help/html/approx_equivalents.htm
            // degRadius = 0.0009;
            degRadius = 0.0009* 10;

            // NumPigs
            let dots = []
            while(dots.length < numPigs){
                let ang = Math.random() * 2 * Math.PI;
                let hyp = Math.sqrt(Math.random()) * degRadius;
                let adj = Math.cos(ang) * hyp;
                let opp = Math.sin(ang) * hyp;

                let point = [farmLat + opp, farmLong + adj]
                if (!dots.includes(point)){
                    pigData.push(point);
                    dots.push(point);
                }
            }

            // Mortalities
            dots = []
            while(dots.length < morts){
                let ang = Math.random() * 2 * Math.PI;
                let hyp = Math.sqrt(Math.random()) * degRadius;
                let adj = Math.cos(ang) * hyp;
                let opp = Math.sin(ang) * hyp;

                let point = [farmLat + opp, farmLong + adj]
                if (!dots.includes(point)){
                    mortData.push(point);
                    dots.push(point);
                }
            }

            // Symptopms Active
            dots = []
            while(dots.length < sxRept){
                let ang = Math.random() * 2 * Math.PI;
                let hyp = Math.sqrt(Math.random()) * degRadius;
                let adj = Math.cos(ang) * hyp;
                let opp = Math.sin(ang) * hyp;

                let point = [farmLat + opp, farmLong + adj]
                if (!dots.includes(point)){
                    sxData.push(point);
                    dots.push(point);
                }
            }

            farmsRadius.addLayer(new L.circle([farmLat, farmLong], {
                radius: 1000,
                color: '#A9A9A9',
                weight: 0
            })).addTo(map);

            allFarms.addLayer(new L.marker([farmLat, farmLong])
            .bindTooltip('<label class="bold-lbl">Farm Code:</label>' + metadata[i]['code'] + '<br>' +
                '<label class="bold-lbl">Address:</label>' + metadata[i]['address'] + '<br>' + 
                '<label class="bold-lbl">No. of pigs: </label>' + numPigs + '<br>' +
                '<label class="bold-lbl">Mortality Rate:</label> ' + mortRts + ' <br>' +
                '<label class="bold-lbl">Symptoms Reported:</label> ' + sxRept + ' <br>' +
                '<label class="bold-lbl">Symptoms Active:</label> ' + sxActv + ' <br>' +
                '<label class="bold-lbl">Last Updated:</label>' + metadata[i]['latest'])).addTo(map);

        }

        console.log(pigData);
        pigData.forEach(function(point){
            pigsPerFarm.addLayer(new L.circleMarker(point, { radius: 1, weight: 1, color: 'black' })).addTo(map);
        });
        mortData.forEach(function(point){
            mortalities.addLayer(new L.circleMarker(point, { radius: 1, weight: 1, color: 'red' })).addTo(map);
        });
        sxData.forEach(function(point){
            symptoms.addLayer(new L.circleMarker(point, { radius: 1, weight: 1, color: 'orange' })).addTo(map);
        });
        
        /**
         * Layer Controls
         */

        var baseMaps = {
            "OpenStreetMap": osm,
            "CARTO": carto
        }   

        var overlayMaps = {
            "Farms": allFarms,
            "No. of Pigs per farm": pigsPerFarm,
            "Mortality Rates": mortalities,
            "Symptoms Reported": symptoms,
        }

        var legend = L.control({
            position: "bottomleft"
        });

        legend.onAdd = function (map) {
            var div = L.DomUtil.create("div", "legend");
            div.innerHTML += "<h4>Legend</h4>";
            div.innerHTML += '<br><i style="background: black"></i><span>No. of Pigs</span><br>';
            div.innerHTML += '<br><i style="background: red"></i><span>Mortalities</span><br>';
            div.innerHTML += '<br><i style="background: orange"></i><span>Symptoms Reported</span><br>';

            return div;
        };

        legend.addTo(map);
        L.control.layers(baseMaps, overlayMaps).addTo(map);

        
    }
    

    if ($('#dm-map-container').length) {
        /**
         * Initialize map view
         */
         console.log("loading dm map...");
         // set view to batangas
         var lat = 13.882406389460293;
         var long = 121.23650234971542;
         var zoom = 11;
 
         // initialize map
         var map = L.map('dm-map-container').setView([lat, long], zoom);
         console.log(map.getZoom());
         // initialize osm tile layer
         var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
             attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
         }).addTo(map);
 
         var carto = L.tileLayer(
             'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
             {
               attribution:
                 '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
             }
           ).addTo(map);
 
         console.log("dm map loaded");

         // 

    }

    return;
});