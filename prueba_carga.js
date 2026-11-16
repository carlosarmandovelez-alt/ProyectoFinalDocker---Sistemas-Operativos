import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '20s', target: 30 }, // Sube a 30 usuarios virtuales
    { duration: '40s', target: 50 }, // Mantiene 50 usuarios simultáneos
    { duration: '15s', target: 0 },  // Baja a 0
  ],
};

export default function () {
  const res = http.get('http://localhost:8080/');
  check(res, { 'status es 200': (r) => r.status === 200 });
  sleep(0.1);
}