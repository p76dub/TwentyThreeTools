# TwentyThreeTools

Une application pour manipuler des outils en relation avec le nombre 23 (ou pas).
Les outils prévus :
- **Scandable** : permet de tester si un mot (en caractères ASCII) est découpable en paquets dont la 
somme des codes vaut n.
- **Perfect** : tester si un nombre est n-parfait, c'est à dire que la somme de ses diviseurs propres
 vaut n.
 
## Scandable
L'outils Scandable est disponible depuis la version 1.0 mais véritablement fonctionnel qu'à 
partir de la version 1.1rc1. Il propose d'analyser un fichier texte et d'en sortir les mots 
scnadables. Ce module, hautement paramétrable, permet entres autres de modifier le nombre à 
atteindre (23 par défaut), les séparateurs de mots, mais aussi dinfluer sur le réultat en enleant
 les mots vides et les doublons. Enfin, il est possible d'analyser ligne par ligne plutôt que le 
 fichier entier. 