import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

function getRandomCoordinate() {
    var lat = (Math.random() * 90).toFixed(7);

    var lon = ((Math.random() * 360) - 180).toFixed(7);

    return { lat: lat, lon: lon };
}

export default function () {
  const coordinates = getRandomCoordinate();
  const url = `http://localhost:8000/api/weather/full?lat=${coordinates.lat}&lon=${coordinates.lon}`;
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  check(http.get(url, params), {
    'status is 200': (r) => r.status == 200,
  }) || errorRate.add(1);
}
