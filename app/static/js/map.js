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
    console.log($('#map-containter').length);
    if ($('#map-containter').length) {
        /**
         * Initialize map view
         */
        console.log("loading map...");
        // set view to batangas
        var lat = 13.882406389460293;
        var long = 121.23650234971542;
        var zoom = 11;

        // initialize map
        var map = L.map('map-containter').setView([lat, long], zoom);

        // initialize osm tile layer
        var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);


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
        // dummy data - replace one geocoding is available 
        // lat, long, numpigs
        // var dummyData = [
        //     [13.757413148089206, 121.05826626908468, 42],
        //     [13.757462595380154, 121.05812012675744, 40],
        //     [13.902000369176863, 121.08865715373985, 20],
        //     [13.784762172550467, 121.03979399812283, 32],
        //     [13.756725764301308, 121.05499304024829, 50],
        //     [14.081607476118473, 121.18257206473466, 20],
        //     [13.99479206671459, 121.21170378257706, 16],
        //     [13.840806354012464, 121.1200278421035, 24],
        //     [13.826096993746729, 121.14817479977627, 44],
        //     [13.764797506521253, 121.05729027875648, 32],
        // ];

        // initialize layer groups
        var allFarms = new L.layerGroup();
        var pigsPerFarm = new L.layerGroup();
        // var mortalityRates = new L.layerGroup();
        // var symptomsRep = new L.layerGroup();

        // add markers and popups to layer groups
        for (var i = 0; i < metadata.length; i++) {
            var farmLat = metadata[i]['latitude'];
            var farmLong = metadata[i]['longitude'];
            var numPigs = metadata[i]['numPigs'];
            var radiusSize = numPigs *100;

            allFarms.addLayer(new L.marker([farmLat, farmLong])
                .bindTooltip('<label class="bold-lbl">Farm Code:</label>' + metadata[i]['code'] + '<br>' +
                    '<label class="bold-lbl">Address:</label>' + metadata[i]['address'])).addTo(map);

            pigsPerFarm.addLayer(new L.circle([farmLat, farmLong], {
                radius: radiusSize,
                color: '#FFFFFF',
                fillColor: 'violet',
                weight: 1,
                fillOpacity: 0.6,
            }).bindTooltip('<label class="bold-lbl">Farm Code:</label>' + metadata[i]['code'] + '<br>' +
                '<label class="bold-lbl">No. of pigs: </label>' + numPigs + '<br>' +
                '<label class="bold-lbl">Last Updated:</label>' + metadata[i]['latest'])).addTo(map);

            // mortalityRates.addLayer(new L.circle([farmLat, farmLong], {
            //     radius: 500,
            //     color: '#FFFFFF',
            //     fillColor: 'red',
            //     weight: 1,
            //     fillOpacity: 0.6,
            // }).bindTooltip('<label class="bold-lbl">Farm Code:</label> 001 <br>' +
            //     '<label class="bold-lbl">Mortality Rate:</label> 10 <br>' +
            //     '<label class="bold-lbl">Last Updated:</label> 1/1/201')).addTo(map);

            // symptomsRep.addLayer(new L.circle([farmLat, farmLong], {
            //     radius: 500,
            //     color: '#FFFFFF',
            //     fillColor: 'orange',
            //     weight: 1,
            //     fillOpacity: 0.6,
            // }).bindTooltip('<label class="bold-lbl">Farm Code:</label> 001 <br>' +
            //     '<label class="bold-lbl">Symptoms Reported:</label> 10 <br>' +
            //     '<label class="bold-lbl">Symptoms Active:</label> 10 <br>' +
            //     '<label class="bold-lbl">Last Updated:</label> 1/1/201')).addTo(map);
        }


        /**
         * Layer Controls
         */
        var baseMaps = {
            "OpenStreetMap": osm
        }

        var overlayMaps = {
            "Farms": allFarms,
            "No. of Pigs per farm": pigsPerFarm,
            // "Moratlity Rates": mortalityRates,
            // "Symptoms Reported": symptomsRep,
        }

        var legend = L.control({
            position: "bottomleft"
        });

        legend.onAdd = function (map) {
            var div = L.DomUtil.create("div", "legend");
            div.innerHTML += "<h4>Legend</h4>";
            div.innerHTML += '<i style="background: violet"></i><span>No. of Pigs</span><br>';
            // div.innerHTML += '<i style="background: red"></i><span>Mortality Rates</span><br>';
            // div.innerHTML += '<i style="background: orange"></i><span>Symptoms Reported</span><br>';

            return div;
        };

        legend.addTo(map);
        L.control.layers(baseMaps, overlayMaps).addTo(map);

        
    }
    return;
});