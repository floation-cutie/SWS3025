import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const MapLocation = () => {
  const mapContainerRef = useRef(null);
  const [lng, setLng] = useState(103.774965); // 默认经度
  const [lat, setLat] = useState(1.294619); // 默认纬度
  const [map, setMap] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  const markerRef = useRef(null);

  useEffect(() => {
    mapboxgl.accessToken = 'Your Mapbox Access Token';

    if (!mapboxgl.supported()) {
      alert('Your browser does not support Mapbox GL');
      return;
    }

    const initializeMap = ({ setMap, mapContainerRef }) => {
      const map = new mapboxgl.Map({
        container: mapContainerRef.current,
        center: [lng, lat],
        zoom: 13
      });

      map.on('load', () => {
        setMap(map);
        map.resize();

        // Initial marker
        const marker = new mapboxgl.Marker()
          .setLngLat([lng, lat])
          .addTo(map);
        markerRef.current = marker;

        map.addSource('route', {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: routePoints
            }
          }
        });
      
        map.addLayer({
          id: 'route',
          type: 'line',
          source: 'route',
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': '#0000cd',
            'line-width': 8
          }
        });

      });

      const geolocateControl = new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true,
        showUserHeading: true
      });

      map.addControl(geolocateControl);
    };

    if (!map) initializeMap({ setMap, mapContainerRef });
  }, [map]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetch('http://192.168.92.51:8008/location')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          if (data.status && data.status === 'error') {
            console.error('Location data is not valid:', data.message);
            return;
          }
          setLng(data.longitude);
          setLat(data.latitude);

          setRoutePoints(oldPoints => [...oldPoints, [data.longitude, data.latitude]]);

          if (map && markerRef.current) {
            markerRef.current.setLngLat([data.longitude, data.latitude]);
            // map.flyTo({ center: [data.longitude, data.latitude], essential: true });
          }
        })
        .catch(err => console.error('Failed to fetch location:', err));
    }, 1000);

    return () => clearInterval(intervalId);
  }, [map]); // Make sure map is in the dependency array

  useEffect(() => {
    if (map && routePoints.length > 1) {
      map.getSource('route').setData({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: routePoints
        }
      });
    }
  }, [routePoints, map]);
  

  return (
    <div className="bg-white shadow-lg rounded-lg p-5">
      <h2 className="text-xl font-semibold mb-4">Map Location</h2>
      <div ref={mapContainerRef} style={{ width: '100%', height: '400px' }}></div>
    </div>
  );
};

export default MapLocation;