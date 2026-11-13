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

const BASE_URL = "http://app-load-balancer-1731186824.eu-central-1.elb.amazonaws.com";

export function setup() {
  const runId = Date.now();

  const userParams = {
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': `create-user-${runId}`
    },
  };

  const userPayload = {
    nick_name: `loadtest_user_${runId}`,
    email: `loadtest_user_${runId}@example.com`,
    registration_date: '2020-10-12',
  };

  const userRes = http.post(
    `${BASE_URL}/users`,
    JSON.stringify(userPayload),
    userParams
  );

  check(userRes, {
    'user created': (r) => r.status === 200 || r.status === 201,
  });

  if (userRes.status !== 200 && userRes.status !== 201) {
    throw new Error(`User creation failed: ${userRes.status} ${userRes.body}`);
  }

  const userId = userRes.json('id');

  const filmIds = [];

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  for (let i = 1; i <= 3; i++) {
    const filmPayload = {
      title: `Loadtest preparation film ${i} ${runId}`,
      year: '2025',
      description: `description preparation film ${i} ${runId}`,
      budget: '120000.000',
    };

    const filmRes = http.post(
      `${BASE_URL}/films`,
      JSON.stringify(filmPayload),
      params
    );

    check(filmRes, {
      [`preparation film ${i} created`]:
        (r) => r.status === 200 || r.status === 201,
    });

    if (filmRes.status !== 200 && filmRes.status !== 201) {
      throw new Error(`Film creation failed: ${filmRes.status} ${filmRes.body}`);
    }

    const filmId = filmRes.json('id');

    if (!filmId) {
      throw new Error('Film creation response does not contain id');
    }

    filmIds.push(filmId);
  }

  return {
    userId, filmIds
  };
}

export default function (data) {
  const RUN_ID = Date.now();

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const postPayload = {
    title: `Loadtest film ${RUN_ID} VU-${__VU} ITER-${__ITER}`,
    year: '2025',
    description: 'Description Loadtest',
    budget: '12000.000',
  };

  const createRes = http.post(
    `${BASE_URL}/films`,
    JSON.stringify(postPayload),
    params
  );

  if (createRes.status !== 200 && createRes.status !== 201) {
    console.error(
      `Film creation failed: status=${createRes.status}, body=${createRes.body}`
    );
  }

  const created = check(createRes, {
    'new film created': (r) => r.status === 200 || r.status === 201,
  });

  if (!created) {
    return;
  }

  const newFilmId = createRes.json('id');

  if (!newFilmId) {
    return;
  }

  for (let i = 0; i < 5; i++) {
    const res = http.get(`${BASE_URL}/films`);

    check(res, {
      'films list loaded': (r) => r.status === 200,
    });
  }

  for (const filmId of data.filmIds) {
    const res = http.get(`${BASE_URL}/films/${filmId}`);

    check(res, {
      'existing film loaded': (r) => r.status === 200,
    });
  }

  const usersRes = http.get(`${BASE_URL}/users/`);

  check(usersRes, {
    'users list loaded': (r) => r.status === 200,
  });

  sleep(1);
}