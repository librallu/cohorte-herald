
Doc Cohorte MicroNode
=====================

Introduction
------------

Cohorte MicroNode est une version minimaliste du framework Cohorte.
Il permet de développer suivant un modèle à composants orientés services (SOCM)
sur des microcontrôleurs de type STM32 et plus en particulier sur une PyBoard.
Les communications entre le MicroNode et le reste de l'application se fait via
communication Bluetooth.

Pour rappel, un des grands intérêts de Cohorte est de permettre à l'utilisateur
de seulement définir les composants et les interactions entre eux et de spécifier
éventuellement sur quelle machine devront s'exécuter ces composants.
Tout le reste, à savoir le déploiement, la réinstantiaion en cas de panne est gérée
par le framework.


Le projet *Cohorte MicroNode* est composé :

 - d'une partie **Routing** qui est une méthode générique pour permettre à
   un isolat Cohorte de "faire passer" des messages d'un isolat à un autre.
   Il s'agit d'une solution générique permettant d'augmenter la connectivité d'une application
   Cohorte. Le problème est particulièrement important dans le cas de MicroNode car la
   liaison Bluetooth ne s'effectue seulement qu'avec un autre isolat. Il est donc nécessaire
   d'avoir un mécanisme de routage pour permettre aux autres isolats de l'application de
   dialoguer avec le microNode.

 - d'une partie **Bluetooth** qui est une méthode de transport au même titre que *HTTP* ou *XMPP*.
   Il s'agit du mode de communication utilisé pour faire dialoguer MicroNode et le reste de l'application
   Cohorte.

 - d'une partie **MicroNode** qui correspond à l'implémentation de Cohorte MicroNode.
   Il représente l'ensemble du code exécuté sur la pyboard pour fournir une interface de
   programmation Cohorte.

 - Enfin d'une partie **UseCase** qui correspond au cas d'usage de Cohorte MicroNode.
   Seront expliquées dans cette partie les montages électroniques réalisés et l'implémentation
   des composants correspondants.

Table des Matières
------------------

.. toctree::
   :maxdepth: 2

   routing
   bluetooth
   micronode
   usecase



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

