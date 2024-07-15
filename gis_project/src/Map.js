import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { EditControl } from 'react-leaflet-draw';
import SideMenu from './SideMenu';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import L from 'leaflet';

const styles = {
  container: {
    position: 'relative',
    height: '570px',
    width: '100%',
  },
  mapContainer: {
    height: '100%',
    width: '100%',
    borderRadius: '15px',
    overflow: 'hidden',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
  },
};


function Map() {
  const featureGroupRef = useRef(null);
  const [bounds, setBounds] = useState(null);
  const [drawnItems, setDrawnItems] = useState(new L.FeatureGroup());

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
    })
    .catch(error => {
      console.error("Error sending bounds to API:", error);
    });
  }

  return (
    <div style={styles.container}>
      <SideMenu handleSend={handleSend} bounds={bounds} />
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
      </MapContainer>
    </div>
  );
}

export default Map;