
Routing
=======

Cette partie présente l'implémentation de la partie *Cohorte Routing*.

Pour que *Cohorte Routing* soit implémenté, il a été nécessaire de réaliser
quelques changements dans *herald.core* pour que la réception de messages
vérifie avant si le noeud est censé reçevoir le message et le retransmettre.
Cela permet de faire en sorte que le routage soit transparent pour les applications
et garantit une rétro-compatibilité.

De plus, si un noeud n'est pas routeur
et que *Herald* ne connaît pas l'UID demandé dans son *directory*, il enverra
quand même le message au dernier noeud routeur qui lui à envoyé un message de
type *herald/routing/hello*. Cela permet de ne pas garder tous les pairs
de l'application en mémoire sur les noeuds non routeur.

Viennent s'ajouter des composants qui s'occuppent de reçevoir ou envoyer
des messages relatifs au routage.

Fonctionnement Général
----------------------

*Cohorte Routing* utilise les sujets commençant par *herald/routing/*.
Il est conseillé de ne pas utiliser ces sujets pour les autres composants
au risque qu'ils ne remontent pas au delà de Herald ou de perturber l'algorithme
de routage.

Différents composants sont présents dans la couche de routage.
Ceux-ci sont présentés dans les parties suivantes.

L'algorithme de routage utilisé est dit *à états de lien*, c'est à dire que
chaque noeud à une connaissance limitée de l'application :

 - Les noeuds routeur connaissent la latence entre eux et leurs voisins directs
   et la latence et le point d'accès pour les pairs auquels ils ne peuvent
   pas accèder directement.

 - Les noeuds non routeur ne connaissent que un routeur auquel ils peuvent
   accèder.


Routing Constants
-----------------

Ce module définit les noms des services utilisés dans *Cohorte Routing*.


.. autodata:: herald.routing_constants.GET_NEIGHBOURS_AVAILABLE

.. autodata:: herald.routing_constants.ROUTING_INFO

.. autodata:: herald.routing_constants.ROUTING_JSON





Routing Handler
---------------

Ce module contient un composant qui est chargé de répondre aux messages de routage.
C'est lui qui permet au noeud d'être considéré comme un noeud accessible à partir
du routage et doit être installé sur les noeuds routeur et non routeur.


.. autoclass:: herald.routing_handler.MessageHandler
    :members:
    :special-members:





Routing Hellos
--------------


.. autoclass:: herald.routing_hellos.Hellos
    :members:
    :special-members:

.. autoclass:: herald.routing_hellos.NeighbourInformation
    :members:
    :special-members:






Routing Json
------------


.. autoclass:: herald.routing_json.RoutingJson
    :members:
    :special-members:





Routing Roads
-------------

.. autoclass:: herald.routing_roads.Roads
    :members:
    :special-members:


Résumé
------

Pour avoir un noeud non routeur, il faut:

 - avoir le composant *Routing Handler* démarré


Pour avoir un noeud routeur, il faut:

 - avoir le composant *Routing Handler* démarré
 - avoir le composant *Routing Hellos* démarré
 - avoir le composant *Routing Roads* démaré
 - **OPTIONNEL**: le composant *Routing JSON* si démarré fournit
   une interface web pour visualiser les informations du routeur.

