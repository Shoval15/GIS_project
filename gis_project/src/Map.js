import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { EditControl } from 'react-leaflet-draw';
import SideMenu from './SideMenu';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import L from 'leaflet';
import ResultsDisplay from './ResultsDisplay';

const styles = {
  container: {
    display: 'flex',
    height: '570px',
    width: '100%',
  },
  mapContainer: {
    flex: '1',
    height: '100%',
    borderRadius: '15px',
    overflow: 'hidden',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
  },
  sideContainer: {
    width: '300px',
    height: '100%',
  },
};

function Map() {
  const featureGroupRef = useRef(null);
  const [bounds, setBounds] = useState(null);
  const [drawnItems, setDrawnItems] = useState(new L.FeatureGroup());
  const [results, setResults] = useState(null);
  const [allocatedLayer, setAllocatedLayer] = useState(null);
  const [notAllocatedLayer, setNotAllocatedLayer] = useState(null);
  const [gardensLayer, setGardensLayer] = useState(null);

  // Jerusalem coordinates
  const jerusalemCoords = [31.7683, 35.2137];

  const handleCreated = (e) => {
    const { layerType, layer } = e;
    if (layerType === 'rectangle' || layerType === 'polygon') {
      // Clear previous layers
      drawnItems.clearLayers();
      
      // Add the new layer
      drawnItems.addLayer(layer);

      const bounds = layer.getBounds();
      const boundsData = {
        northEast: bounds.getNorthEast(),
        southWest: bounds.getSouthWest()
      };
      setBounds(boundsData);
    }
  }

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
  }

  const handleSend = (formData) => {
    console.log(formData);
    // Send bounds to Flask API using fetch
    fetch('http://127.0.0.1:5000/api/bounds', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bounds: bounds,
        projectStatus: formData.projectStatus,
        apartmentType: formData.apartmentType,
        distance: formData.distance
      }),
    })
    .then(response => response.json())
    .then(data => {
      console.log("Response from API:", data);
      setAllocatedLayer(data.response.allocated_layer);
      setNotAllocatedLayer(data.response.not_allocated_layer);
      setResults(data.response.allocation_stats);
      setGardensLayer(data.response.gardens_layer);
    })
    .catch(error => {
      console.error("Error sending bounds to API:", error);
    });
  }

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      layer.bindPopup(`
        <strong>Building ID:</strong> ${feature.properties.OBJECTID_building}<br>
        <strong>Garden ID:</strong> ${feature.properties.OBJECTID_garden}<br>
        <strong>Address:</strong> ${feature.properties.address}<br>
        <strong>Units:</strong> ${feature.properties.units_e}<br>
      `);
    }
  };

  
  return (
    <div style={styles.container}>
      <div style={styles.sideContainer}>
        <ResultsDisplay results={results} />
      </div>
      <MapContainer
        center={jerusalemCoords}
        zoom={13}
        style={styles.mapContainer}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
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
        {allocatedLayer && (
          <GeoJSON 
            data={allocatedLayer} 
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`
              <strong>Building ID:</strong> ${feature.properties.OBJECTID_building}<br>
              <strong>Garden ID:</strong> ${feature.properties.OBJECTID_garden}<br>
              <strong>Address:</strong> ${feature.properties.address}<br>
              <strong>Units:</strong> ${feature.properties.units_e}<br>
              <strong>Exists or Proposed:</strong> ${feature.properties.gen_status}<br>
            `);
            }}
            style={(feature) => ({
              fillColor:  'blue',
              weight: 2,
              opacity: 1,
              color: 'white',
              dashArray: '3',
              fillOpacity: 0.7
            })}
          />
        )}
      {/* {notAllocatedLayer && (
          <GeoJSON 
            data={notAllocatedLayer} 
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`
                <b>Building:</b> ${feature.properties.address}<br>
                <b>Units:</b> ${feature.properties.units_e}<br>
                <b>Status:</b> Not Allocated
              `);
            }}
            style={(feature) => ({
              fillColor:  'red',
              weight: 2,
              opacity: 1,
              color: 'white',
              dashArray: '3',
              fillOpacity: 0.6
            })}
          />
        )}

        {gardensLayer && (
          <GeoJSON 
            data={gardensLayer} 
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`
                <b>Garden:</b> ${feature.properties.Descr}<br>
                <b>Capacity:</b> ${feature.properties.capacity}<br>
                <b>Remaining Capacity:</b> ${feature.properties.remaining_capacity}<br>
                <b>Area:</b> ${feature.properties['Shape.STArea()']} sq m
              `);
            }}
            style={(feature) => ({
              fillColor:  'brown',
              weight: 2,
              opacity: 1,
              color: 'white',
              dashArray: '3',
              fillOpacity: 0.5
            })}
          /> 
        )}*/}
      </MapContainer>
      <div style={styles.sideContainer}>
        <SideMenu handleSend={handleSend} bounds={bounds} />
      </div>
    </div>
  );
}

export default Map;