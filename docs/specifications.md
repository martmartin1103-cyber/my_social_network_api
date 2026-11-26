
- Exigence métiers techniquofonctionnel de nouvelle API

- Définire les End points

- créer et mettre à jour la documentation de l'API avec Postamn

url par services :
-pour chanque url indique le code API attendu 


/User : 

Recherche : GET https://api.mysocialnetwork.org/3/search/user

Details : GET https://api.mysocialnetwork.org/3/person/{person_id}

Création : POST https://api.mysocialnetwork.org/3/person/{person_id} ->user.json

Modification : PUT https://api.mysocialnetwork.org/3/person/{person_id}

Suppression : DEL https://api.mysocialnetwork.org/3/person/{person_id}/



Liste des évents d'une personne : 


/Evènements: 

Recherche : GET https://api.mysocialnetwork.org/3/search/event

Details : GET https://api.mysocialnetwork.org/3/event/{event_id}


//Evènements of User :

Liste des events d'une personne :
GET https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id} 

New event by User : (il faut être log pour créer un évènemment)
POST https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id} ->event.json

Modification : 
PUT https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id} ->event.json

Delete Event by User Owneur :
DEL https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id} 

//Invitation Event Managemment: 

Send Invitation d'un utilisateur à un autre à un évènemment :
Ou plutot Ajout d'un utilisateur à la liste des inviter de l'évènemment (plus performant?)
POST OU PUT
https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id}/invitation/{invitation_id} ->invitation.json

Supression  Invitation d'un utilisateur à l'évènemment :
DEL https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id}/invitation/{invitation_id} 


(A supprimer de ma doc ?-->
Modification : PUT https://api.mysocialnetwork.org/3/person/{person_id}

Suppression : DEL https://api.mysocialnetwork.org/3/person/{person_id}/


Details : get https://api.mysocialnetwork.org/3/event/{event_id}/

POST https://api.mysocialnetwork.org/3/event/{event_id}/

DEL https://api.mysocialnetwork.org/3/event/{event_id}/
)

/Groups : 


Recherche : GET https://api.mysocialnetwork.org/3/search/group

Details : GET https://api.mysocialnetwork.org/3/group/{group_id} /

Création : POST https://api.mysocialnetwork.org/3/person/{person_id}/group ->group.json

Modification : PUT https://api.mysocialnetwork.org/3/group/{group_id} /public privée

Suppression : DEL https://api.mysocialnetwork.org/3/group/{group_id}/



Liste des id_user du groupe:
Details : GET https://api.mysocialnetwork.org/3/group/{group_id}/member/ member group liste

invitation d'un utilisateur au groupe:
POST OU PUT
https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id}/invitation/{invitation_id} ->invitation.json

sortit de l'utilisateur du groupe:
DEL ou PUT https://api.mysocialnetwork.org/3/person/{person_id}/event/{event_id}/invitation/{invitation_id}


Cration évènemment de groupe + envoie invitation automatique au membre du groupe. 


//Evènements of group :

Liste des events d'un group :
GET https://api.mysocialnetwork.org/3/group/{group_id}/event/{event_id}

New event for group by member : (il faut être membre pour créer un évènemment)
POST https://api.mysocialnetwork.org/3/group/{group_id}/event/ ->event.json

Modification :
PUT https://api.mysocialnetwork.org/3/group/{group_id}/event/{event_id} ->event.json

Delete Event by Owneur for group :
DEL https://api.mysocialnetwork.org/3/group/{group_id}/event/{event_id}






Search : 

get https://api.mysocialnetwork.org/3/search/user

get https://api.mysocialnetwork.org/3/search/group

get https://api.mysocialnetwork.org/3/search/event









trending/movie/{time_window}



explication fonctionnel :

données retournées :



- livré sur repo git hub


--------------------


1.1 : Configuration de l'évènemment 
Exigence un utilisateur doit créer un évènemment en 3 clic seulemment avec parcours guidé.



1.2: Les groupes :

Création de groupe privée ou public d'utilisateur

Dans chaque groupe il existe un fil de conversation classic

Possibilité de créer des évènemment avec invitation auto en 1 clic à tout les membres du groupes (Get adresse email user grouope id, Post invitation à email user groupe récupérer?)

Pour groupe public :
Possibilité de repartager les évènemment sur API forma autre réseaux socieux pour les organisateur.

Les paramètres d'un groupe :
...



