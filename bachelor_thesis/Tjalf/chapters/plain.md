---
lang: de-DE
---
# Chapter

## Motivation

Diese Bachelorarbeit ist entsprungen, um in der Akamodell Stuttgart effizienter Modellflugzeuge auslegen zu können. Die Akamodell Stuttgart ist ein eingetragener Verein an der Universität Stuttgart, an dem Studenten lernen Modellflugzeuge zu entwerfen und zu bauen. Dazu nimmt die Akamodell zwei-jährlich an der Air Cargo Challenge (ACC) teil. Die ACC ist ein Wettbewerb, bei dem verschiedene Teams aus europäischen und einigen internationalen Universitäten gegeneinander antreten, um ein Flugzeug zu konstruieren, dass dem Regelwerk entsprechend die Flugaufgaben möglichst gut zu erfüllen. Besonders für diese Wettbewerbe ist eine schnelle und qualitativ hochwertige Auslegung von Bedeutung. Da solche Auslegungen viel Know-how erfordern, ist es das Ziel ein Tool zu entwickeln, dass dieses vereinfacht.

## Flugaufgaben

### Start

#### Startstrecke

#### Startzeit

### Steigen

#### Steilstes Steigen

#### Schnellstes Steigen

## Massenbestimmung

### Durch Toplevel

Interpolation durch 

### Definiertes Flugzeug

Zunächst muss das Flugzeug in seine Bestandteile aufgeteilt werden. Diese sind der Flügel, das Leitwerk und der Rumpf neben gegebenen Massen, wie das Fahrwerk, Batterie und Motor.

Der Flügel und das Leitwerk können auf ähnliche Weisen berechnet werden. Sie werden auf Flügelsegmente aufgeteilt. Jedes Flügelsegment kann nun einzelne berechnet werden. Dabei wird die Oberfläche und das Volumen zuerst bestimmt. Mit der Oberfläche und der Lagen Kohle/Glas kann nun eine erste Masse bestimmt werden. Die weitere Berechnung erfolgt nun abhängig von der gewählten Bauweise. Ist es ein Formenbau, muss nun die Lastenverteilung auf den Holm bestimmt werden und danach die benötigte Dicke des Holms berechnet werden. Dadurch kann der Holm nun dimensioniert werden und diesem eine Masse zugeteilt werden. Zuletzt müssen gegebenenfalls noch Verbinder zwischen verschiedenen Flügelsegmenten dimensioniert werden.


## Algorithmus

### Eingabe

1. Permutationen der Flugzeuge 

### Bewertung

$$
    \sum{\frac{a_i\cdot i}{a_{max}}}
$$

Wobei $a_i$ die gewertete Flugaufgabe, max die maximale über alle Flugzeuge und i die manuelle Bewertung.