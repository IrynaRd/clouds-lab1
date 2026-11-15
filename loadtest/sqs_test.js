import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 40 },
    { duration: '5m', target: 40 },
    { duration: '3m', target: 0 },
  ],

  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

const BASE_URL = __ENV.BASE_URL || "http://app-load-balancer-1731186824.eu-central-1.elb.amazonaws.com";

export function setup() {
  const runId = Date.now();
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const userIds = [];
  for (let i = 1; i <= 50; i++) {
    const userPayload = {
      nick_name: `sqs test user_${runId}_${i}`,
      email: `sqst test ${runId}_${i}@example.com`,
      registration_date: '2026-01-01',
    };

    const res = http.post(
      `${BASE_URL}/users`,
      JSON.stringify(userPayload),
      params
    );

    check(res, {
      [`user ${i} created`]: (r) => r.status === 200 || r.status === 201,
    });

    if (res.status === 200 || res.status === 201) {
      userIds.push(res.json('id'));
    }
  }

  // test films
  const filmIds = [];
  for (let i = 1; i <= 10; i++) {
    const filmPayload = {
      title: `SQS test film ${runId} ${i}`,
      year: '2025',
      description: `SQS load test film ${i}`,
      budget: '10000.000',
    };

    const res = http.post(
      `${BASE_URL}/films`,
      JSON.stringify(filmPayload),
      params
    );

    check(res, {
      [`film ${i} created`]: (r) => r.status === 200 || r.status === 201,
    });

    if (res.status === 200 || res.status === 201) {
      filmIds.push(res.json('id'));
    }
  }

  if (userIds.length === 0 || filmIds.length === 0) {
    throw new Error('Failed to create test data');
  }

  return { runId, userIds, filmIds };
}

export default function (data) {
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const userIndex = (__VU - 1) % data.userIds.length;
  const filmIndex = __ITER % data.filmIds.length;

  const userId = data.userIds[userIndex];
  const filmId = data.filmIds[filmIndex];

  const reviewPayload = {
    film_id: filmId,
    user_id: userId,
    review_text: `Load test review VU=${__VU} ITER=${__ITER} ${Date.now()}`,
    review_date: '2025-01-15',
  };

  const createRes = http.post(
    `${BASE_URL}/reviews/`,
    JSON.stringify(reviewPayload),
    params
  );

  check(createRes, {
    'review accepted (202)': (r) => r.status === 202,
  });


  const filmsRes = http.get(`${BASE_URL}/films`);
  check(filmsRes, {
    'films list loaded': (r) => r.status === 200,
  });


  const getRes = http.get(`${BASE_URL}/reviews/film/${filmId}/user/${userId}`);
  check(getRes, {
    'review status checked': (r) => r.status === 200 || r.status === 404,
  });

  sleep(0.5);
}
