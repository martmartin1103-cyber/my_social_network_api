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

    USERS ||--o{ GROUP_MEMBERS : rejoint
    GROUPS ||--|{ GROUP_MEMBERS : contient
    GROUPS |o--o{ EVENTS : heberge
    USERS ||--o{ EVENT_PARTICIPANTS : participe
    EVENTS ||--|{ EVENT_PARTICIPANTS : inclut

    %% ==========================================
    %% INTERACTIONS : DISCUSSIONS, PHOTOS, SONDAGES
    %% ==========================================
    THREADS {
        INT id PK
        INT group_id FK "nullable XOR"
        INT event_id FK "nullable XOR"
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

    GROUPS |o--o{ THREADS : possede_XOR
    EVENTS |o--o{ THREADS : possede_XOR
    THREADS ||--o{ MESSAGES : contient
    USERS ||--o{ MESSAGES : publie
    MESSAGES ||--o{ MESSAGE_COMMENTS : recoit
    USERS ||--o{ MESSAGE_COMMENTS : commente

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

    EVENTS ||--o{ PHOTO_ALBUMS : possede
    PHOTO_ALBUMS ||--o{ PHOTOS : contient
    USERS ||--o{ PHOTOS : poste
    PHOTOS ||--o{ PHOTO_COMMENTS : recoit
    USERS ||--o{ PHOTO_COMMENTS : commente

    POLLS {
        INT id PK
        INT event_id FK
        INT creator_id FK
        VARCHAR title
        DATETIME created_at
    }

    POLL_QUESTIONS {
        INT id PK
        INT poll_id FK
        VARCHAR question_text
    }

    POLL_OPTIONS {
        INT id PK
        INT question_id FK
        VARCHAR option_text
    }

    POLL_VOTES {
        INT id PK
        INT question_id FK "UK avec user_id"
        INT option_id FK
        INT user_id FK "UK avec question_id"
        DATETIME voted_at
    }

    EVENTS ||--o{ POLLS : contient
    USERS ||--o{ POLLS : cree
    POLLS ||--|{ POLL_QUESTIONS : comporte
    POLL_QUESTIONS ||--|{ POLL_OPTIONS : propose
    POLL_QUESTIONS ||--o{ POLL_VOTES : recoit
    POLL_OPTIONS ||--o{ POLL_VOTES : est_choisie
    USERS ||--o{ POLL_VOTES : vote

    %% ==========================================
    %% MODULES METIER : BILLETTERIE, SHOPPING, COVOITURAGE
    %% ==========================================
    TICKET_TYPES {
        INT id PK
        INT event_id FK
        VARCHAR name
        DECIMAL price
        INT max_quantity
    }

    TICKETS {
        INT id PK
        INT ticket_type_id FK
        VARCHAR buyer_firstname
        VARCHAR buyer_lastname
        TEXT buyer_address
        VARCHAR buyer_email
        DATETIME purchased_at
    }

    SHOPPING_ITEMS {
        INT id PK
        INT event_id FK "UK avec name"
        INT user_id FK
        VARCHAR name "UK avec event_id"
        INT quantity
        TIME arrival_time
    }

    CARPOOLS {
        INT id PK
        INT event_id FK
        INT driver_id FK
        VARCHAR departure_location
        DATETIME departure_time
        DECIMAL price
        INT available_seats
        INT max_detour_minutes
    }

    EVENTS ||--o{ TICKET_TYPES : propose
    TICKET_TYPES ||--o{ TICKETS : genere
    EVENTS ||--o{ SHOPPING_ITEMS : liste
    USERS ||--o{ SHOPPING_ITEMS : apporte
    EVENTS ||--o{ CARPOOLS : organise
    USERS ||--o{ CARPOOLS : conduit
```
