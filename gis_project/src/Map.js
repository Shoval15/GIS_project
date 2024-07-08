import React, { useState, useRef } from 'react';
import { MapContainer, TileLayer, FeatureGroup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { EditControl } from 'react-leaflet-draw';
import axios from 'axios';
import { bounds } from 'leaflet';

function Map() {
  const [selectedArea, setSelectedArea] = useState([]);
  const featureGroupRef = useRef(null);

  // Jerusalem coordinates
  const jerusalemCoords = [31.7683, 35.2137];
  const handleCreated = (e) => {
    const { layerType, layer } = e;
    if (layerType === 'rectangle') {
      const bounds = layer.getBounds();
      const boundsData = {
        northEast: bounds.getNorthEast(),
        southWest: bounds.getSouthWest()
      };
      console.log(boundsData)
      setSelectedArea(bounds);

    // Send bounds to Flask API using fetch
    fetch('http://127.0.0.1:5000/api/bounds', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(boundsData),
    })
    .then(response => response.json())
    .then(data => {
      console.log("Response from API:", data);
    })
    .catch(error => {
      console.error("Error sending bounds to API:", error);
    });
    }
  };

  return (
    <MapContainer
      center={jerusalemCoords}
      zoom={13}
      style={{ height: '400px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <FeatureGroup ref={featureGroupRef}>
        <EditControl
          position="topright"
          onCreated={handleCreated}
          draw={{
            rectangle: true,
            polyline: false,
            polygon: false,
            circle: false,
            marker: false,
            circlemarker: false,
          }}
        />
      </FeatureGroup>
    </MapContainer>
  );
}

export default Map;