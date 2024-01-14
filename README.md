# US-BJ-PO

Teammitglieder:
Quang Huy Vien (s0582406)
Miroslaw Keil (s0582192)

Thema:
Prompt Optimzer Using GPT-4

Dieses Repo beinhaltet ein KI-Blackjack Spiel auf Grundlage des Seller-Byer-Problems mit Promptoptimization.

Es gibt einen Dealer, welcher die Karten austeilt und nach den herkömmlichen Blackjackregeln spielt.

Es gibt 3 "normale" Spieler, welche je nach ihrer Persönlichkeit (riskant, defensiv, etc.) spielen.

Es gibt eine Kartenzähler, welcher seinen Einsatz nach dem "Card-Count" richtet.

Es gibt eine Security, welche versucht den Kartenzähler zu entlarven.

Es gibt einen Supervisor, welcher nach jedem Spiel dem Kartenzähler und der Security Tipps gibt (Promptoptimization).

Link zum Repository:
https://github.com/dalbongy/US-BJ-PO

Erklärung der Files:

main.py = der Code

Results = alle Konsolen Outputs

Prompt templates = Alle Anweisungen an die Agents mit persona und system_description und instructions an die einzelnen Rollen

Der API-Key wird in einer .env Datei gespeichert, welche nicht im GitHub Repo liegt.

Einfach lokal eine .env Datei mit OPEN_AI_KEY=YOUR_KEY anlegen.
