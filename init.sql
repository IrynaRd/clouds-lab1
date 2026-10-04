DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS facts;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS film;

CREATE TABLE film (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    year YEAR NOT NULL,
    description VARCHAR(450) NOT NULL,
    budget DECIMAL(12, 3) NOT NULL
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nick_name VARCHAR(45) NOT NULL,
    email VARCHAR(60) NOT NULL UNIQUE,
    registration_date DATE NOT NULL
);

CREATE TABLE facts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NOT NULL,
    film_id INT NOT NULL,
    FOREIGN KEY (film_id) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE rating (
    film_id INT NOT NULL,
    user_id INT NOT NULL,
    points INT NOT NULL,
    PRIMARY KEY (film_id, user_id),
    FOREIGN KEY (film_id) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE review (
    film_id INT NOT NULL,
    user_id INT NOT NULL,
    review_text TEXT NOT NULL,
    review_date DATE NOT NULL,
    PRIMARY KEY (film_id, user_id),
    FOREIGN KEY (film_id) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO film (title, year, description, budget) VALUES
('Початок', 2010, 'Злодій краде корпоративні секрети, використовуючи технологію обміну снами.', 160000000.000),
('Матриця', 1999, 'Хакер дізнається справжню природу своєї реальності та свою роль у війні проти контролерів.', 63000000.000),
('Інтерстеллар', 2014, 'Команда дослідників подорожує крізь червоточину в космосі в пошуках нового дому для людства.', 165000000.000),
('Дюна', 2021, 'Син шляхетної родини вирушає на найнебезпечнішу планету у всесвіті.', 165000000.000),
('Аватар', 2009, 'Паралізований морський піхотинець опиняється на місяці Пандора і стає перед вибором.', 237000000.000),
('Темний лицар', 2008, 'Бетмен стикається з психопатом, відомим як Джокер.', 185000000.000);


INSERT INTO user (nick_name, email, registration_date) VALUES
('movie_fan_99', 'fan99@example.com', '2023-01-15'),
('cinema_critic', 'critic@example.com', '2023-03-22'),
('sci_fi_geek', 'geek@example.com', '2023-05-10'),
('casual_viewer', 'viewer@example.com', '2023-07-05'),
('nolan_lover', 'nolan@example.com', '2023-09-18'),
('popcorn_eater', 'popcorn@example.com', '2023-11-30');

INSERT INTO facts (description, film_id) VALUES
('Коридор, що обертається, був справжньою конструкцією, а не комп''ютерною графікою.', 1),
('Код на екранах матриці — це рецепти суші, взяті з японської кухонної книги.', 2),
('Для фільму було вирощено справжнє поле кукурудзи, яке потім продали.', 3),
('Композитор Ганс Циммер створив нові інструменти спеціально для саундтреку цього фільму.', 4),
('Мова Наві була розроблена лінгвістом Полом Фроммером.', 5),
('Хіт Леджер імпровізував сцену з оплесками у в''язниці.', 6);

INSERT INTO rating (film_id, user_id, points) VALUES
(1, 5, 10),
(2, 3, 9),
(3, 1, 10),
(4, 2, 8),
(5, 4, 7),
(6, 6, 9);

INSERT INTO review (film_id, user_id, review_text, review_date) VALUES
(1, 5, 'Шедевр Крістофера Нолана. Візуал просто неймовірний.', '2023-10-01'),
(2, 3, 'Фільм, який змінив жанр фантастики назавжди.', '2023-05-15'),
(3, 1, 'Плакав на кінцівці. Саундтрек доповнює атмосферу на 100%.', '2023-02-10'),
(4, 2, 'Дуже гарна картинка, але місцями затягнуто. Чекаю на другу частину.', '2023-04-05'),
(5, 4, 'Класика 3D, але сюжет досить передбачуваний.', '2023-08-20'),
(6, 6, 'Найкращий Джокер в історії кіно. Неймовірна акторська гра.', '2023-12-05');