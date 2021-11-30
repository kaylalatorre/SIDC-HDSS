/**
 * Initialize map view
 */

// set view to batangas
var lat =  13.753916804358575;
var long = 121.04149886683209;
var zoom = 12;

// initialize map
var map = L.map('map-containter').setView([lat, long], zoom);

// initialize osm tile layer
var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);



/**
 * Populate map
 */

// style icons
var ibIcon = L.divIcon({
    html: "<i class='bx bxs-circle' style='color:#ff0000' ></i>"
});

// add markers and popups
var intBiosec = L.marker([13.837938209780106, 120.98931380662845], {icon: ibIcon}).addTo(map)
    .bindPopup(' <label class="bold-lbl">Address:</label> address <br>' +
                '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                '<label class="bold-lbl">Score:</label> 10 <br>' +
                '<label class="bold-lbl">Last Updated:</label> 1/1/201');

var extBiosec = L.marker([13.901922259900022, 121.08875371280136]).addTo(map)
    .bindPopup(' <label class="bold-lbl">Address:</label> address <br>' +
                '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                '<label class="bold-lbl">Score:</label> 10 <br>' +
                '<label class="bold-lbl">Last Updated:</label> 1/1/201');

var mortalityRates = L.marker([13.756777869646523, 121.05502522675748]).addTo(map)
    .bindPopup(' <label class="bold-lbl">Address:</label> address <br>' +
                '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                '<label class="bold-lbl">Mortality Rate:</label> 10 <br>' +
                '<label class="bold-lbl">Last Updated:</label> 1/1/201');

var symptomsRep = L.marker([13.825951142071434, 121.14811042675792]).addTo(map)
    .bindPopup(' <label class="bold-lbl">Address:</label> address <br>' +
                '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                '<label class="bold-lbl">Symptoms Reported:</label> 10 <br>' +
                '<label class="bold-lbl">Symptoms Active:</label> 10 <br>' +
                '<label class="bold-lbl">Last Updated:</label> 1/1/201');

/**
 * Layer Controls
 */
var baseMaps = {
    "OpenStreetMap" : osm
}

var overlayMaps = {
    "Internal Biosecurity Scores" : intBiosec,
    "External Biosecurity Scores" : extBiosec,
    "Moratlity Rates" : mortalityRates,
    "Symptoms Reported" : symptomsRep
}

// add everything to map
L.control.layers(baseMaps, overlayMaps).addTo(map);