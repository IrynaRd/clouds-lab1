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

const BASE_URL = "http://localhost:5000";

export function setup() {
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const userPayload = {
    nick_name: 'loadtest_user',
    email: 'loadtest_user@example.com',
    registration_date: '2020-10-12',
  };

  const userRes = http.post(
    `${BASE_URL}/users`,
    JSON.stringify(userPayload),
    params
  );

  check(userRes, {
    'user created': (r) => r.status === 200 || r.status === 201,
  });

  if (userRes.status !== 200 && userRes.status !== 201) {
    throw new Error(`User creation failed: ${userRes.status} ${userRes.body}`);
  }

  const userId = userRes.json('id');

  const filmIds = [];

  for (let i = 1; i <= 3; i++) {
    const filmPayload = {
      title: `Loadtest preparation film ${i}`,
      year: '2025',
      description: `description preparation film ${i}`,
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

  const reviewIds = [];

  for (const filmId of filmIds) {
    const reviewPayload = {
      user_id: userId,
      film_id: filmId,
      review_text: 'review loadtest preparation',
      review_date: '2020-12-12',
    };

    const reviewRes = http.post(
      `${BASE_URL}/reviews`,
      JSON.stringify(reviewPayload),
      params
    );

    check(reviewRes, {
      'review created': (r) => r.status === 200 || r.status === 201,
    });

    if (reviewRes.status !== 200 && reviewRes.status !== 201) {
      throw new Error(`Review creation failed: ${reviewRes.status} ${reviewRes.body}`);
    }

    const reviewId = reviewRes.json('id');

    if (reviewId) {
      reviewIds.push(reviewId);
    }
  }

  return {
    userId, filmIds, reviewIds,
  };
}

export default function (data) {
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };
  const postPayload = {
    title: `Loadtest film VU-${__VU} ITER-${__ITER}`,
    year: '2025',
    description: 'Description Loadtest',
    budget: '12000.000',
  };

  const createRes = http.post(
    `${BASE_URL}/films`,
    JSON.stringify(postPayload),
    params
  );

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

  for (let i = 0; i < 2; i++) {
    const res = http.get(`${BASE_URL}/films`);

    check(res, {
      'films list loaded': (r) => r.status === 200,
    });
  }

  let res = http.get(`${BASE_URL}/films/${newFilmId}`);

  check(res, {
    'new film loaded': (r) => r.status === 200,
  });

  for (let i = 0; i < 2; i++) {
    const filmId = data.filmIds[i];

    res = http.get(`${BASE_URL}/films/${filmId}`);

    check(res, {
      'existing film loaded': (r) => r.status === 200,
    });
  }

  res = http.get(`${BASE_URL}/users/${data.userId}`);

  check(res, {
    'user loaded': (r) => r.status === 200,
  });


  for (let i = 0; i < 2; i++) {
    const filmId = data.filmIds[i];

    res = http.get(`${BASE_URL}/reviews/film/${filmId}`);

    check(res, {
      'film reviews loaded': (r) => r.status === 200,
    });
  }

  res = http.get(`${BASE_URL}/reviews/film/${data.filmIds[2]}`);

  check(res, {
    'film3 reviews loaded': (r) => r.status === 200,
  });

  sleep(1);
}