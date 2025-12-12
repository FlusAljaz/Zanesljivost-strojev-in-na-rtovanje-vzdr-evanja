# Optimalna zamenjava stroja v prenovitvenem modelu

Projekt obravnava problem optimalne zamenjave stroja v okviru prenovitvenega procesa
z degradacijo življenjske dobe. Cilj je določiti optimalno število popravil pred
zamenjavo stroja z novim, tako da minimiziramo dolgoročne stroške na časovno enoto.

## Obravnavani modeli

V projektu so obravnavani naslednji modeli časov med okvarami:
- eksponentna porazdelitev,
- Weibullova porazdelitev,
- lognormalna porazdelitev (težkorepi model).

Posebaj smo se posvetili kaj se zgodi, če stroji skozi življenje dosežejo degradacijo. To
pomeni, da se z vsakim popravilom stroja njegova življenska doba zmanjša, dokler ne nakupimo 
novega.

## Glavni rezultat

Za izbrane stroškovne in degradacijske parametre dobimo optimalno število popravil
pred zamenjavo stroja
\[
k^* = 7,
\]
kar velja neodvisno od izbire porazdelitve časov med okvarami.
Izbira porazdelitve vpliva na trajanje ciklov, ne pa na optimalno strategijo zamenjave.
