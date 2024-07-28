import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { EditControl } from 'react-leaflet-draw';
import SideMenu from './SideMenu';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import L from 'leaflet';
import ResultsDisplay from './ResultsDisplay';
import {deploy_be, debugging_be} from '../App';
import Legend from './Legend';
import { strings } from '../utilities/strings';
import '../styles/Map.css';
import ErrorModal from '../ErrorModal';

function Map({language }) {
  const featureGroupRef = useRef(null);
  const [bounds, setBounds] = useState(null);
  const [polygon, setPolygon] = useState(null);
  const [drawnItems, setDrawnItems] = useState(new L.FeatureGroup());
  const [results, setResults] = useState(null);
  const [allocatedLayer, setAllocatedLayer] = useState(null);
  const [notAllocatedLayer, setNotAllocatedLayer] = useState(null);
  const [gardensLayer, setGardensLayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [gardenColors, setGardenColors] = useState({});

  // Jerusalem coordinates
  const jerusalemCoords = [31.7683, 35.2137];

  // Function to generate a random color
  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };
  const assignGardenColors = (gardens) => {
    const newGardenColors = {};
    gardens.features.forEach(garden => {
      const randomColor = getRandomColor();
      newGardenColors[garden.properties.OBJECTID] = randomColor;
    });
    setGardenColors(newGardenColors);
  };

  useEffect(() => {
    if (gardensLayer) {
      assignGardenColors(gardensLayer);
    }
  }, [gardensLayer]);

  const handleCreated = (e) => {
    const { layerType, layer } = e;
    if (layerType === 'rectangle' || layerType === 'polygon') {
      // Clear previous layers
      drawnItems.clearLayers();
      
      // Add the new layer
      drawnItems.addLayer(layer);

      const latlngs = layer.getLatLngs()[0];

      // Convert LatLng objects to coordinate pairs and structure the data
      const rings = [
        ...latlngs.map(({lng, lat}) => [lng, lat]),
        [latlngs[0].lng, latlngs[0].lat] // Close the polygon
      ];
      const bounds = layer.getBounds();
      const boundsData = {
        northEast: bounds.getNorthEast(),
        southWest: bounds.getSouthWest()
      };
      setBounds(boundsData);
      setPolygon(rings);
      console.log(rings)
    }
  };

  const handleEdited = (e) => {
    const layers = e.layers;
    layers.eachLayer((layer) => {
      const bounds = layer.getBounds();
      const boundsData = {
        northEast: bounds.getNorthEast(),
        southWest: bounds.getSouthWest()
      };
      setBounds(boundsData);
    });
  };

  const handleDeleted = (e) => {
    drawnItems.clearLayers();
    setBounds(null);
  };

  const handleSend = (formData) => {
    setLoading(true);
    // Send bounds to Flask API using fetch
    fetch(debugging_be + '/api/bounds', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        polygon:polygon,
        bounds: bounds,
        projectStatus: formData.projectStatus,
        apartmentType: formData.apartmentType,
        distance: formData.distance,
        sqMeterPerResident: formData.sqMeterPerResident,
        residentsPerApartment: formData.residentsPerApartment
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'failed') {
        if (data.response in strings)
        {
          setErrorMessage(strings[data.response][language]);
        }
        else
        {
          setErrorMessage(data.response);
        }
      } else {
        setAllocatedLayer(data.response.allocated_layer);
        setNotAllocatedLayer(data.response.not_allocated_layer);
        setResults(data.response.allocation_stats);
        setGardensLayer(data.response.gardens_layer);
        
      }
      setLoading(false);
    })
    .catch(error => {
      
      console.error("Error sending bounds to API:", error);
      setErrorMessage(error);
      setLoading(false);
    });
  };

  const onEachFeatureAllocated = (feature, layer) => {
    layer.bindPopup(`
      <strong>${strings.buildingID[language]}:</strong> ${feature.properties.OBJECTID_building}<br>
      <strong>${strings.gardenID[language]}:</strong> ${feature.properties.OBJECTID_garden}<br>
      <strong>${strings.projectStatus[language]}:</strong> ${feature.properties.status}<br>
      <strong>${strings.address[language]}:</strong> ${feature.properties.address}<br>
      <strong>${strings.units[language]}:</strong> ${feature.properties.units_e}<br>
      <strong>${strings.existsOrProposed[language]}:</strong> ${feature.properties.gen_status}<br>
    `);
  };

  const onEachFeatureNotAllocated = (feature, layer) => {
    layer.bindPopup(`
      <b>${strings.address[language]}:</b> ${feature.properties.address}<br>
      <b>${strings.units[language]}:</b> ${feature.properties.units_e}<br>
      <b>${strings.status[language]}:</b> ${strings.notAllocated[language]}
      <b>${strings.projectStatus[language]}:</b> ${feature.properties.status}
    `);
  };

  const onEachFeatureGardens = (feature, layer) => {
    layer.bindPopup(`
      <b>${strings.gardenID[language]}:</b> ${feature.properties.OBJECTID}<br>
      <b>${strings.areaType[language]}:</b> ${feature.properties.Descr}<br>
      <b>${strings.capacity[language]}:</b> ${feature.properties.capacity}<br>
      <b>${strings.remainingCapacity[language]}:</b> ${feature.properties.remaining_capacity}<br>
      <b>${strings.area[language]}:</b> ${feature.properties['Shape.STArea()']} sq m
    `);
  };

  const mapLanguage = language === 'en' ? 'en' : 'he';
  const handleCloseErrorModal = () => {
    setErrorMessage(null);
    window.location.reload();
  };

  return (
    <div className="map-container">
      <div className="map-side-container">
        {results && (
          <ResultsDisplay results={results} language={language} loading={loading} />
        )}
        {loading && (
          <img src="loading.gif" alt="loading"></img>
        )}
      </div>
      <MapContainer
        center={jerusalemCoords}
        zoom={13}
        className="map-leaflet-container"
      >
        <TileLayer
          url={`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?lang=${mapLanguage}`}
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <FeatureGroup ref={featureGroupRef}>
          <EditControl
            position="topright"
            onCreated={handleCreated}
            onEdited={handleEdited}
            onDeleted={handleDeleted}
            draw={{
              polyline: false,
              polygon: true,
              rectangle: true,
              circle: false,
              marker: false,
              circlemarker: false
            }}
            edit={{
              featureGroup: drawnItems
            }}
          />
        </FeatureGroup>
        {allocatedLayer && gardenColors &&(
          <GeoJSON 
            data={allocatedLayer} 
            onEachFeature={onEachFeatureAllocated}
            style={(feature) => {
              return({
              fillColor: gardenColors[feature.properties.OBJECTID_garden],
              color: gardenColors[feature.properties.OBJECTID_garden],
              weight: 1,
              // opacity: 1,
              // dashArray: '3',
              fillOpacity: 0.8
            })}}
          />
        )}
        {notAllocatedLayer && (
          <GeoJSON 
            data={notAllocatedLayer} 
            onEachFeature={onEachFeatureNotAllocated}
            style={(feature) => ({
              fillColor: 'red',
              weight: 2,
              opacity: 1,
              dashArray: '3',
              fillOpacity: 0.8
            })}
          />
        )}
        {gardensLayer && gardenColors &&(
          <GeoJSON 
            data={gardensLayer} 
            onEachFeature={onEachFeatureGardens}
            style={(feature) => ({
              fillColor: gardenColors[feature.properties.OBJECTID],
              weight: 4,
              color: 'green',
              opacity: 1,
              // dashArray: '3',
              fillOpacity: 0.8
            })}
          /> 
        )}
        <Legend language={language} />
      </MapContainer>
      <div className="map-side-container">
        <SideMenu handleSend={handleSend} bounds={bounds} language={language} loading={loading} />
      </div>
      {errorMessage && (
        <ErrorModal 
          show={errorMessage !== null}
          onHide={handleCloseErrorModal}
          message={errorMessage}
          language={language}
        />
      )}
    </div>
  );
}

export default Map;
