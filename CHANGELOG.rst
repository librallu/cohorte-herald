Changes form the 0.0.3 to 0.0.4.dev
-----------------------------------

* New Feature

  * Herald Remote Shell: open a shell session on another peer

* Improvements

  * Herald unlocks send() calls when the target peer is unregistered.
    It also calls the errback of post() calls.

* Bug Fix

  * Fixing synchronisation problem: XMPP transport blocked on
    ``_on_disconnected`` (isandlaTech/cohorte-herald/issues/14).
