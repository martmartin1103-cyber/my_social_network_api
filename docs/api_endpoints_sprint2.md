# Documentation API — Suite des fonctionnalités (Recherche, Discussions, Médias, Sondages, Billetterie)

**Base URL :** `/api/v1` (ex: `http://127.0.0.1:8000/api/v1`)

---

## 1. Événements d'un groupe

### Besoins fonctionnels
* Seul un membre autorisé (ou un administrateur selon les paramètres du groupe) peut créer un événement dans un groupe.
* La création d'un événement dans un groupe invite automatiquement tous les membres du groupe.
* Seul l'organisateur (ou un administrateur du groupe) peut modifier ou supprimer l'événement.

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Liste des événements du groupe | `GET` | `/api/v1/groups/{group_id}/events` | `200`, `403`, `404` | Récupère tous les événements liés au groupe |
| Détail d'un événement du groupe | `GET` | `/api/v1/groups/{group_id}/events/{event_id}` | `200`, `403`, `404` | Récupère le détail d'un événement précis du groupe |
| Créer un événement dans le groupe | `POST` | `/api/v1/groups/{group_id}/events` | `201`, `400`, `401`, `403`, `404` | Crée l'événement et invite automatiquement tous les membres |
| Modifier un événement du groupe | `PUT` | `/api/v1/groups/{group_id}/events/{event_id}` | `200`, `400`, `401`, `403`, `404` | Met à jour l'événement (organisateur / admin uniquement) |
| Supprimer un événement du groupe | `DELETE` | `/api/v1/groups/{group_id}/events/{event_id}` | `204`, `401`, `403`, `404` | Supprime l'événement (organisateur / admin uniquement) |

---

## 2. Recherche globale (Search)

### Besoins fonctionnels
* Permettre de rechercher rapidement des utilisateurs, des groupes ou des événements par mot-clé (`q`).
* Les groupes `secrets` et les événements `privés` ne doivent pas apparaître dans les résultats pour les utilisateurs non invités.

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Rechercher des utilisateurs | `GET` | `/api/v1/users?q={terme}` | `200`, `400` | Recherche par username, nom complet ou email |
| Rechercher des groupes | `GET` | `/api/v1/groups?q={terme}` | `200`, `400` | Recherche par nom ou description (hors groupes secrets) |
| Rechercher des événements | `GET` | `/api/v1/events?q={terme}` | `200`, `400` | Recherche par nom, lieu ou description |

*(Alternative dédiée si souhaitée : `GET /api/v1/search/users?q=...`, `/search/groups?q=...`, `/search/events?q=...`)*

---

## 3. Fils de discussion & Messages

### Besoins fonctionnels
* Un fil de discussion est lié à **1 groupe OU 1 événement, mais jamais les deux (contrainte XOR)**.
* Contient 0 ou plusieurs messages (texte ou média) créés par un membre, administrateur ou organisateur.
* Chaque membre/participant peut commenter un message.
* Seul l'auteur d'un message peut le modifier ou le supprimer (ou un admin/organisateur pour la modération).

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Fils d'un groupe | `GET` | `/api/v1/groups/{group_id}/threads` | `200`, `403`, `404` | Liste les fils de discussion d'un groupe |
| Fils d'un événement | `GET` | `/api/v1/events/{event_id}/threads` | `200`, `403`, `404` | Liste les fils de discussion d'un événement |
| Créer un fil de discussion | `POST` | `/api/v1/threads` | `201`, `400`, `401`, `403` | Crée un fil (`group_id` XOR `event_id` obligatoire ; `400` si les deux ou aucun) |
| Historique des messages | `GET` | `/api/v1/threads/{thread_id}/messages` | `200`, `403`, `404` | Récupère les messages précédents d'un fil (avec pagination `?limit=50&offset=0`) |
| Envoyer un message texte | `POST` | `/api/v1/threads/{thread_id}/messages` | `201`, `400`, `401`, `403`, `404` | Poste un nouveau message dans le fil |
| Envoyer un message avec image | `POST` | `/api/v1/threads/{thread_id}/messages` | `201`, `400`, `401`, `403`, `413` | Poste un message contenant une image (`multipart/form-data` ou `image_url`) et l'ajoute à la galerie |
| Modifier son message | `PUT` / `PATCH` | `/api/v1/threads/{thread_id}/messages/{message_id}` | `200`, `400`, `401`, `403`, `404` | Modifie le contenu d'un message (auteur uniquement) |
| Supprimer son message | `DELETE` | `/api/v1/threads/{thread_id}/messages/{message_id}` | `204`, `401`, `403`, `404` | Supprime un message (`404` s'il n'existe pas, `403` si non autorisé) |
| Commenter un message | `POST` | `/api/v1/messages/{message_id}/comments` | `201`, `400`, `401`, `403`, `404` | Ajoute un commentaire sous un message |

---

## 4. Albums Photo

### Besoins fonctionnels
* Un album photo est associé à **1 événement** (créable automatiquement ou manuellement par un participant/organisateur).
* Un album contient 0 ou plusieurs photos postées par les participants.
* Chaque photo peut être commentée par 0 ou plusieurs participants.

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Albums d'un événement | `GET` | `/api/v1/events/{event_id}/albums` | `200`, `403`, `404` | Liste les albums photo de l'événement |
| Créer un album photo | `POST` | `/api/v1/events/{event_id}/albums` | `201`, `400`, `401`, `403`, `404` | Crée un nouvel album rattaché à l'événement |
| Visualiser les photos d'un album | `GET` | `/api/v1/albums/{album_id}/photos` | `200`, `403`, `404` | Récupère toutes les photos d'un album |
| Ajouter une photo à un album | `POST` | `/api/v1/albums/{album_id}/photos` | `201`, `400`, `401`, `403`, `404` | Ajoute une photo postée par un participant |
| Supprimer une photo | `DELETE` | `/api/v1/albums/{album_id}/photos/{photo_id}` | `204`, `401`, `403`, `404` | Supprime une photo (auteur ou organisateur) |
| Commenter une photo | `POST` | `/api/v1/photos/{photo_id}/comments` | `201`, `400`, `401`, `403`, `404` | Ajoute un commentaire sur une photo |

---

## 5. Sondages (Polls)

### Besoins fonctionnels
* 0 ou plusieurs sondages par événement, créés uniquement par un **organisateur**.
* Un sondage comporte 1 ou plusieurs questions avec plusieurs choix possibles.
* **Règle métier stricte** : un participant ne peut choisir **qu'une seule réponse par question** (`409 Conflict` s'il tente de revoter).

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Sondages d'un événement | `GET` | `/api/v1/events/{event_id}/polls` | `200`, `403`, `404` | Liste les sondages d'un événement |
| Créer un sondage | `POST` | `/api/v1/events/{event_id}/polls` | `201`, `400`, `401`, `403`, `404` | Crée un sondage avec ses questions et choix (organisateur uniquement) |
| Récupérer les participants | `GET` | `/api/v1/polls/{poll_id}/participants` | `200`, `403`, `404` | Liste les utilisateurs ayant répondu au sondage |
| Répondre à un sondage (voter) | `POST` | `/api/v1/polls/{poll_id}/votes` | `201`, `400`, `401`, `403`, `404`, `409` | Enregistre le vote d'un participant (`409` s'il a déjà répondu à cette question) |
| Récolter les résultats / avis | `GET` | `/api/v1/polls/{poll_id}/results` | `200`, `403`, `404` | Retourne l'agrégation des réponses par question |
| Supprimer un sondage | `DELETE` | `/api/v1/polls/{poll_id}` | `204`, `401`, `403`, `404` | Supprime un sondage (organisateur uniquement) |

---

## 6. Billetterie (Ticketing)

### Besoins fonctionnels
* Disponible uniquement sur les événements **publics** (`400` ou `403` sur un événement privé).
* L'organisateur crée 1 ou plusieurs **types de billets** (`nom`, `montant`, `quantité limitée`).
* Une personne extérieure ne peut acheter **qu'un seul billet maximum** (`409 Conflict` en cas de doublon ou de stock épuisé).
* Chaque billet acheté enregistre : type de billet, nom, prénom, adresse complète et date d'achat.

### Endpoints
| Action | Méthode | URL | Codes HTTP | Description |
| :--- | :--- | :--- | :--- | :--- |
| Types de billets d'un événement | `GET` | `/api/v1/events/{event_id}/ticket-types` | `200`, `404` | Liste les tarifs et le stock restant pour un événement public |
| Créer un type de billet | `POST` | `/api/v1/events/{event_id}/ticket-types` | `201`, `400`, `401`, `403`, `404` | Ajoute un type de billet (organisateur uniquement, événement public) |
| Modifier un type de billet | `PUT` / `PATCH` | `/api/v1/events/{event_id}/ticket-types/{ticket_type_id}` | `200`, `400`, `401`, `403`, `404` | Modifie le nom, le prix ou la quantité disponible |
| Supprimer un type de billet | `DELETE` | `/api/v1/events/{event_id}/ticket-types/{ticket_type_id}` | `204`, `401`, `403`, `404`, `409` | Supprime un type de billet (`409` si des billets ont déjà été vendus) |
| Acheter un billet | `POST` | `/api/v1/events/{event_id}/tickets` | `201`, `400`, `404`, `409` | Achète 1 billet (nom, prénom, adresse) ; `409` si stock = 0 ou acheteur déjà détenteur d'un billet |
| Liste des billets vendus | `GET` | `/api/v1/events/{event_id}/tickets` | `200`, `401`, `403`, `404` | Liste les acheteurs et billets vendus (organisateur uniquement) |