# UE-AD-A1-MIXTE

Application de gestion de cinéma découpée en microservices Python (Flask). Elle permet de consulter et gérer un catalogue de films, de programmer des films à des dates données et de réserver des séances pour des utilisateurs.

Le projet mélange deux styles d'API : **GraphQL** (avec [Ariadne](https://ariadnegraphql.org/)) pour `movie` et `booking`, **REST** pour `user` et `schedule`.

## Architecture

| Service    | Port | Type    | Rôle                                                              | Stockage                    |
|------------|------|---------|-------------------------------------------------------------------|-----------------------------|
| `movie`    | 3001 | GraphQL | Catalogue des films et des acteurs                                | `movie/data/*.json`         |
| `booking`  | 3002 | GraphQL | Réservations des utilisateurs                                     | `booking/data/bookings.json` |
| `schedule` | 3003 | REST    | Programmation : quels films sont diffusés à quelle date           | `schedule/data/times.json`  |
| `user`     | 3004 | REST    | Utilisateurs et rôles (`user` / `admin`)                          | MongoDB                     |
| `mongo`    | 27017 | —      | Base de données du service `user`                                 | —                           |

Les appels entre services :

```
booking ──► schedule   (vérifie que le film est programmé à la date demandée)
booking ──► user       (vérifie que l'utilisateur existe)
schedule ──► user      (seul un admin peut modifier la programmation)
schedule ──► movie     (vérifie que les films ajoutés existent)
user ──► mongo
```

Au premier démarrage, le service `user` remplit MongoDB à partir de `user/data/users.json` si la collection est vide.

## Lancer le projet

### Avec Docker (recommandé)

```bash
docker compose up --build
```

Tous les services démarrent avec les bonnes URL entre eux. mongo-express est accessible sur http://localhost:8081.

### En local, sans Docker

Python 3 est requis, ainsi qu'un MongoDB accessible sur `localhost:27017` (le plus simple : `docker compose up -d mongo`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chaque service lit ses données avec des chemins relatifs (`./data/...`) : il faut le lancer **depuis son propre dossier**, dans un terminal séparé.

```bash
cd user     && python user.py
cd movie    && python movie.py
cd schedule && python schedule.py
cd booking  && python booking.py
```

Par défaut, les services se contactent sur `127.0.0.1`. Les variables d'environnement `USER_URL`, `MOVIE_URL`, `SCHEDULE_URL` et `MONGO_URL` permettent de changer ces adresses.

## Exemples d'utilisation

Lister les films (GraphQL) :

```bash
curl -X POST http://localhost:3001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ all_movies { id title director rating } }"}'
```

Voir la programmation d'une date (REST) :

```bash
curl http://localhost:3003/schedule/20151130
```

Ajouter des films à une date (réservé aux admins) :

```bash
curl -X POST http://localhost:3003/schedule/20151130/chris_rivers \
  -H "Content-Type: application/json" \
  -d '{"date": "20151130", "movies": ["720d006c-3a57-4b6a-b18f-9b713b073f3c"]}'
```

Créer une réservation (GraphQL) :

```bash
curl -X POST http://localhost:3002/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { create_booking(_userid: \"chris_rivers\", _date: \"20151130\", _movie: \"720d006c-3a57-4b6a-b18f-9b713b073f3c\") { userid dates { date movies } } }"}'
```

Les schémas GraphQL complets sont dans `movie/movie.graphql` et `booking/booking.graphql`.
