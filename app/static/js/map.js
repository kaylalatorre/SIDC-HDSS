/**
 * Initialize map view
 */

// set view to batangas
var lat =  13.882406389460293;
var long = 121.23650234971542;
var zoom = 10.5;

// initialize map
var map = L.map('map-containter').setView([lat, long], zoom);

// initialize osm tile layer
var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


/**
 * Populate map
 */
var dummyData = [
    [13.757413148089206, 121.05826626908468],
    [13.757462595380154, 121.05812012675744],
    [13.902000369176863, 121.08865715373985],
    [13.784762172550467, 121.03979399812283],
    [13.756725764301308, 121.05499304024829],
    [14.081607476118473, 121.18257206473466],
    [13.99479206671459, 121.21170378257706],
    [13.840806354012464, 121.1200278421035],
    [13.826096993746729, 121.14817479977627],
    [13.764797506521253, 121.05729027875648],
];

// initialize layer groups
var intBiosec = new L.layerGroup();
var extBiosec = new L.layerGroup();
var mortalityRates = new L.layerGroup();
var symptomsRep = new L.layerGroup();

// add markers and popups to layer groups
for (var i = 0; i < dummyData.length; i++) {
    intBiosec.addLayer(new L.circleMarker([dummyData[i][0], dummyData[i][1]], {
        radius: 12,
        color: 'red',
        weight: 0,
        fillOpacity: 0.4,
    } ).bindPopup(  '<label class="bold-lbl">Address:</label> address <br>' +
                    '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                    '<label class="bold-lbl">Score:</label> 10 <br>' +
                    '<label class="bold-lbl">Last Updated:</label> 1/1/201'));

    extBiosec.addLayer(new L.circleMarker([dummyData[i][0], dummyData[i][1]], {
        radius: 8,
        color: 'blue',
        weight: 0,
        fillOpacity: 0.4,
    }).bindPopup(   '<label class="bold-lbl">Address:</label> address <br>' +
                    '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                    '<label class="bold-lbl">Score:</label> 10 <br>' +
                    '<label class="bold-lbl">Last Updated:</label> 1/1/201'));
    
    mortalityRates.addLayer(new L.circleMarker([dummyData[i][0], dummyData[i][1]], {
        radius: 8,
        color: 'yellow',
        weight: 0,
        fillOpacity: 0.4,
    }).bindPopup(   '<label class="bold-lbl">Address:</label> address <br>' +
                    '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                    '<label class="bold-lbl">Mortality Rate:</label> 10 <br>' +
                    '<label class="bold-lbl">Last Updated:</label> 1/1/201'));
    
    symptomsRep.addLayer(new L.circleMarker([dummyData[i][0], dummyData[i][1]], {
        radius: 8,
        color: 'orange',
        weight: 0,
        fillOpacity: 0.4,
    }).bindPopup(   '<label class="bold-lbl">Address:</label> address <br>' +
                    '<label class="bold-lbl">Farm Code:</label> 001 <br>' + 
                    '<label class="bold-lbl">Symptoms Reported:</label> 10 <br>' +
                    '<label class="bold-lbl">Symptoms Active:</label> 10 <br>' +
                    '<label class="bold-lbl">Last Updated:</label> 1/1/201'));
}


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
    "Symptoms Reported" : symptomsRep,
}

L.control.layers(baseMaps, overlayMaps).addTo(map);