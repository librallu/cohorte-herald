

MicroNode
=========

Micronode correspond à l'implémentation côté pyboard.

Les codes de l'automate série, des messages herald sur la liaison série sont
identiques à la partie bluetooth.

Le module components correspond aux composants utilisateurs. C'est ce fichier
qui contient les composants que l'utilisateur à défini et est chargé et inspecté
automatiquement par le reste du code.

De la même façon que du côté PC, sont présents les modules iPOPO et herald
qui servent respectivement à gérer le système à composants et à réaliser la
communication.





Notes de réalisation
--------------------

Différences entre le framework micropython et python:

 - Les dépendances circulaires sont correctement gérées
   par python, mais pose problème en micropython.
 - MicroPython ne gère pas encore les messages de type herald/rpc/remove.
   Si un service est perdu, il n'est pas détecté par le système
 - de la même manière, il n'a pas de timer pour considérer un
   un service perdu (lors d'un send par exemple)
 - Pour limiter la quantité de mémoire ROM utilisée, le système
   traite les messages SerialHerald directement. Il n'y a pas de
   transformation en messages Herald purs. Cela permet de limiter
   la quantité de mémoire utilisée par les sources du programme.


automata
--------

.. autoclass:: automata.SerialAutomata
    :members:
    :special-members:


components
----------

Fichier comprenant les composants utilisateur.
Voir la partie **Cas d'usage** pour plus d'informations.


iPOPO
-----

Certaines fonctionnalités du framework ne sont pas encore disponibles :

 - Si un composant requiert un service A et que les implémentations *a1* et *a2* sont
   disponibles. Supposons sans perte de généralité que *a1* est utilisé et est supprimé,
   le composant ne passera pas sur *a2*.
 - Si un composant fournit un service sur la pyboard et s'arrête, la pyboard n'informera pas
   le reste de l'application.

.. automodule:: ipopo
    :members:

Herald
------

.. automodule:: pyboard.herald
    :members:

main
----

Représente la boucle principale et intègre les primitives pour allumer/éteindre la LED
ou lire les valeurs sur la photorésistance.

.. automodule:: pyboard.main
    :members:

serial herald message
---------------------

See Serial Herald Message section in Bluetooth part


xmlrpc
------

implémente des primitives permettant de forger ou extraire des
requêtes/réponses Json ou XML. Ce parsing s'effectue avec des
découpages de chaîne de caractère. Cette méthode est utilisée
pour éviter d'utiliser un parseur XML ou Json qui met trop
de temps pour traiter le message. (plusieurs secondes).

.. automodule:: pyboard.xmlrpc
    :members:

