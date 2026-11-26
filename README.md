# my_social_network_api

TP sur la refonte des API d'un réseau social (type Facebook) visant à améliorer la réactivité, la fiabilité et les performances des services. Cette API REST couvre la gestion des utilisateurs, groupes, événements, interactions sociales (discussions, albums photo, sondages) ainsi que les modules de billetterie, shopping list.

## Fonctionnalités principales
* **Utilisateurs** : Gestion complète (CRUDS) avec unicité de l'email.
* **Groupes** : Groupes publics, privés ou secrets, gestion des rôles (administrateurs/membres) et permissions de publication.
* **Événements** : Création guidée, gestion des organisateurs/participants, visibilité et invitation automatique des membres d'un groupe.
* **Fils de discussion** : Liés exclusivement à un groupe ou à un événement, avec messages et commentaires.
* **Albums photo** : Associés à un événement, partage de photos et commentaires par les participants.
* **Sondages** : Création par les organisateurs, questions à choix multiples (1 seule réponse par participant et par question).
* **Billetterie** : Types de billets en quantité limitée pour les événements publics (1 billet max par personne extérieure).
* **Shopping list** : Liste d'éléments uniques à apporter par événement.
* **Covoiturage (Bonus)** : Proposition de trajets avec places disponibles, prix et temps d'écart maximum.

## Stack technique
* **Langage / Framework** : `[python][ex: Node.js / Express ou PHP / Symfony]`
* **Base de données** : `[ex: PostgreSQL / MySQL / MongoDB]`
* **Documentation** : Postman

Architecture BDD: 
## Installation et lancement
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/martmartin1103-cyber/my_social_network_api
   cd my_social_network_api
   ```

## Modélisation de la base de données

```mermaid
erDiagram
    %% ==========================================
    %% NOYAU : UTILISATEURS, GROUPES & EVENEMENTS
    %% ==========================================
    USERS {
        INT id PK
        VARCHAR firstname
        VARCHAR lastname
        VARCHAR email UK
        VARCHAR password_hash
        VARCHAR avatar_url
        DATETIME created_at
    }

    GROUPS {
        INT id PK
        VARCHAR name
        TEXT description
        VARCHAR icon_url
        VARCHAR cover_photo_url
        ENUM type "public, private, secret"
        BOOLEAN allow_member_posts
        BOOLEAN allow_member_events
    }

    GROUP_MEMBERS {
        INT group_id PK,FK
        INT user_id PK,FK
        ENUM role "admin, member"
        DATETIME joined_at
    }

    EVENTS {
        INT id PK
        INT group_id FK "nullable"
        VARCHAR name
        TEXT description
        DATETIME start_date
        DATETIME end_date
        VARCHAR location
        VARCHAR cover_photo_url
        ENUM visibility "public, private"
        BOOLEAN has_shopping_list
        BOOLEAN has_carpooling
    }

    EVENT_PARTICIPANTS {
        INT event_id PK,FK
        INT user_id PK,FK
        ENUM role "organizer, participant"
        ENUM status "invited, accepted, declined"
    }

    USERS ||--o{ GROUP_MEMBERS : "rejoint"
    GROUPS ||--|{ GROUP_MEMBERS : "contient"
    GROUPS |o--o{ EVENTS : "heberge"
    USERS ||--o{ EVENT_PARTICIPANTS : "participe"
    EVENTS ||--|{ EVENT_PARTICIPANTS : "inclut"

    %% ==========================================
    %% INTERACTIONS : DISCUSSIONS, PHOTOS, SONDAGES
    %% ==========================================
    THREADS {
        INT id PK
        INT group_id FK "nullable (XOR)"
        INT event_id FK "nullable (XOR)"
        DATETIME created_at
    }

    MESSAGES {
        INT id PK
        INT thread_id FK
        INT author_id FK
        TEXT content
        DATETIME created_at
    }

    MESSAGE_COMMENTS {
        INT id PK
        INT message_id FK
        INT author_id FK
        TEXT content
        DATETIME created_at
    }

    GROUPS |o--o{ THREADS : "possede (XOR)"
    EVENTS |o--o{ THREADS : "possede (XOR)"
    THREADS ||--o{ MESSAGES : "contient"
    USERS ||--o{ MESSAGES : "publie"
    MESSAGES ||--o{ MESSAGE_COMMENTS : "recoit"
    USERS ||--o{ MESSAGE_COMMENTS : "commente"

    PHOTO_ALBUMS {
        INT id PK
        INT event_id FK
        VARCHAR title
        DATETIME created_at
    }

    PHOTOS {
        INT id PK
        INT album_id FK
        INT author_id FK
        VARCHAR image_url
        VARCHAR caption
        DATETIME created_at
    }

    PHOTO_COMMENTS {
        INT id PK
        INT photo_id FK
        INT author_id FK
        TEXT content
        DATETIME created_at
    }

    EVENTS ||--o{ PHOTO_ALBUMS : "possede"
    PHOTO_ALBUMS ||--o{ PHOTOS : "contient"
    USERS ||--o{ PHOTOS : "poste
