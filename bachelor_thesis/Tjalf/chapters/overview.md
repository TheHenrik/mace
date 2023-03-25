---
lang: de-De
---
# Bachelorarbeit

Dieses Dokument ist nur zur Übersicht über einzelne Kapitel.

## Abstract

## Einleitung

Dies ist die Bachelorarbeit.

### Motivation

Als Mitglied der Akamodell war ich bereits Teil des Entwurfsprozesses für verschiedene Flugzeuge. 
Dabei werden aus verschiedensten Tabellen, Memory Items und Entwurftools kombiniert um dieses zu Entwerfen. 
Um nun alle Schritte zu vereinen und den Entwurfsprozess freundlich zu gestalten, soll nun ein Tool entworfen werden. 
Einer der wichtigsten Teile des Entwurfsprozesses ist die Bestimmung der Masse und der Einzelmassen verschiedener Teile.

Das gesamte Tool soll dann auch für die nächste Air-Cargo-Challenge 2024 genutzt werden.

### Zielsetzung

Verbessern des Modellflugzeugentwurfs und erstellen eines Tools um diverse Prozesse zu vereinen.

### Gliederung

Zunächst werden wichtige Grundlagen, Organisationen und der Stand der Technik erklärt. Danach wird 

## Grundlagen

Hier sollen alle Grundlagen für die verständniss der folgenden Bachelorarbeit geklärt werden. Zunächst wird der Hintergrund erläutert und danach 

### Akamodell Stuttgart

Die Akamodell Stuttgart ist eine 1978 studentische Organisation an der Universität Stuttgart. Hier werden Modellflugzeuge gebaut und entwickelt und so theoretisches Wissen aus den Luft- und Raumfahrt Vorlesungen, die die meisten Mitglieder hören, praktisch umgesetzt werden und gelerntes dann wieder für das Studium genutzt werden.

Die Akamodell Stuttgart nimmt seit 2007 erfolgreich an der Air-Cargo-Challenge Teil, die einer der Gründe für die Entwicklung des Tools ist, und hat 2007 einen zweiten, 2009, 2013, 2017 einen ersten und 2022 einen dritten Platz erreicht. Die Akamodell Stuttgart ist daher auch international bekannt.

Diese Erfahrung 



### Flugaufgaben

Eine Übersicht

Startstrecke/zeit
Landestrecke/zeit

Bestes Steigen
Bestes Gleiten
Geringstes Sinken



### Stand der Technik

Der Stand der Technik soll im folgenden Anhand einer Aufgabenstellung der Air-Cargo-Challenge 2022 erklärt werden.

Zu Beginn der Auslegung gibt es oft eine grobe Vorstellung welche Dimensionen der Flieger haben muss und welche Flugaufgaben erfüllt werden müssen und wie diese zu Gewichten sind.
Auslegung nach ACC Aufgabe 2021/2022
Flugaufgabe und ermitteln wie gewichtung
Größenbeschränkungen
Windkanalmessungen




### Sichere Lasten

Im Modellbau wird meist ein Sicherheitsfaktor von X genutzt.
Die Sichere Last hängt von der geforderten Flugaufgabe ab. Besonders sind dabei Kurvenflüge und starke sinkflüge für hohe g Lasten verantwortlich. Die maximale g-Last kann aus der v-n Diagramm bestimmt werden. Dabei sind in diesem Diagramm auf der x Achse die Geschindigkeiten und auf der y Achse die Lasten aufgezeichnet. Links der Kurve ist kein Flug möglich, da das Flugzeug eine beschleunigung Richtung boden erfährt. Dabei ist zu beachten, dass die maximale Last hauptsächlich von der maximal Geschwindigkeit abhängt. Diese Last ist im Modellflug auch zu erreichen, da gegebenfalls starke Kurven geflogen werden müssen.
Sicherheitsfaktor, Lastenbestimmung, v(n)

### Python

Python ist eine höhere Programmiersprache, die sich auf eine einfache und verständliche Syntax spezialisiert hat. So werden zum Beispiel Blöcke durch Indention und nicht durch Klammern gekennzeichnet. Im Gegenzug ist Python im Vergleich zu anderen Programmiersprachen langsam und der nötige Programmcode ist oft länger. 

Dieses Projekt hat aber den Anspruch eine möglichst einfache Benutzeroberfläche und erweiterbarkeit zu ermöglichen. 

Um aber bestimmte Berechnungen zu beschleunigen, können berechnungen an CPython übergeben werden. CPython ist eine Sprache, die sehr einfach von Python programmcode aufgerufen werden kann und die Geschwindigkeit und teile der Syntax der Programmiersprache C übernimmt. Dieses kann auch über Libraries die in C geschieben worden sind erreicht werden. Im folgenden wird oft NumPy aufgerufen. Dadurch können viele Berechnungen sehr schnell erledigt werden ohne auf die Vorteile von Python verzichten zu müssen. Weiterhin legt Python seit Version 3.11 auch einen Fokus auf eine Beschleunigung der Programiersprache und ist daher im Vergleich zu Version 3.10 um 10-60 % schneller und im Durchschnitt können Benchmarks 1,22 mal schneller bewältigt werden.

Python bietet auch eine einfache Möglichkeit den Programmcode zu Packagen. Das bedeutet, das verschiedene Dateien, im folgenden Module genannt, in ein übergeordnetes Paket zusammengefasst werden. Diese kann nun von Benutzern, die Zugriff auf den Sourcecode haben, installiert werden und mit wenig Know-how genutzt werden. Im fall eines veröffentlichten Source-Codes kann diese auch auf bestimmte Tools hochgeladen werden. Über diese kann nun jeder Nutzer weltweit mit wenigen Zeilen Code das Projekt importieren und nutzen.


## Hauptteil

### Algorithmus

Erklärung Algorithmus anhand von Grafiken

#### UML

Eingegeben werden können Projekte in verschiedenen Arten und weisen. Das Projekt basiert auf einer Datenstruktur, wie sie im UML-Diagramm beschrieben wurde. 
Um den Algorithmus zu nutzen müssen nun die Benötigten Klassen initialisiert und deklariert werden. 
Dies ist auf verschiedene Arten umsetzbar. 
Zum ersten kann selber Programmcode geschrieben werden um Werte zu setzen, es kann der Parser, der aus externen Menschen- und Maschinenlesbaren Dateien einliest, aufgerufen werden oder ein noch nicht umgesetzes Graphische Oberfläche geöffnet werden.

Für die Bachelorarbeit wurde hauptsächlich der Parser genutzt. Dabei kann ein Flugzeug in einer externen Datei gespeichert werden



#### Flowcharts

Im Folgenden werden wichtige Programmschritte anhand von ausgewählten Flowcharts dargestellt und erläutert.

1. Berechnung der Parameter

Zunächst wird der Funktion ein Flugzeug übergeben. Dann muss entschieden werden, ob ein Vollständig definiertes Flugzeug übergeben wurde, oder ob eine bestimmung nach Regression benötigt wird. Zunächst wird hier die Parameterberchnung vorgstellt, danach eine mögliche implementation der Regression.


Das Flugzeug wird in seine einzelnen Bestandteile unterteilt, welche dann berechnet werden können. Im Fall der Flügel ist das Flügelsegment, eine Approximation als Trapezflügel, das kleinste finite Objekt. Dieses wird entweder über vier Koordinatenpunkte an seinen Ecken definiert oder über die beiden Nasenpunkte, die Tiefe und den Winkel zur x-z Ebene. Zusätzlich werden Flügelprofile für die Innen- und Außenkannte definiert. Diese können aus NACA berechnet werden, viele Profile von Seliger sind bereits im Paket enthalten oder es könne eigene Profile übergeben werden. Dann wird über eine Koordinatentransformation das Profil auf die Eckpunkte gelegt. Danach werden über die beiden Profile ein Gitternetz gelegt, wobei die kleinste Fläche ein Dreieck bildet. Dieses hat den Vorteil, dass ein Dreieck mithilfe einfachster Algebra berechenbar ist. Es wird über alle Flächen iteriert und so kann die Gesamtfläche berechnet werden als:

$$ A_{Oberfläche} = \sum_i{\frac{|\overline{A_iB_i} \times \overline{A_iC_i}|}{2}} $$

wobei A, B und C die gegebenen Eckpunkte des Dreiecks sind. Hierbei wird nur die Fläche berechnet, die die Flügelhaut bilden, da die Seitenelemente noch nicht benötigt werden. Dieser Prozess wird nun wiederholt um das Gesamtvolumen des Segmentes zu bestimmen. Die Formel hierfür ist: 

$$ V_{Segment} = \sum_i{\frac{(a_i\times b_i)\cdot c_i}{6}} $$

Wobei wieder A, B und C als Eckpunkte des Dreiecks definiert sind. Dabei wieder ausgenutzt, dass das Spatprodukt das Volumen zwischen den Dreien punkten und dem Ursprung einschließt. Außerdem ist das Spatprodukt vorzeichenbehaftet, wodurch sich Flächen, deren Normalenvektor zum Ursprung zeigt und welche mit entgegen gerichteten Normalenvektoren so kürzen, dass nur das Volumen in dem definierten Objekt verbleibt. Hierbei müssen sämtliche Flächen betrachtet werden, das nur geschlossene Volumen berechnet werden können.





### Optimierer

Hier soll ein Überblick von Algorithmen gegeben werden, die auf das Massenabschätzungs-tool zugreifen könnten und wie dieses aufgerufen werden kann.

### Materialien

Ein wichtiger Punkt der Massenabschätzung im Modellflugzeugbau ist die Wahl geeigneter Materialien. So hat Stahl zwar eine hohe Zugfestigkeit, wiegt aber überproportional viel.
Im Modellbau wird daher meist mit Glas-, Kohlenstofffaserverbundkunstoffen und Balsaholz gearbeitet. Wichtige Parameter sind hier Webedichte, anzahl der Lagen und die Wahl des Richtgen Stoffes. Auch die Elektromagnetischen Eigenschafften sind hier wichtig, da Kohlefaser Funksignale stören kann und daher nicht an überall verwendet werden kann, wenn dieser die Antenne des Senders/Empfängers blockieren würde. 

Im folgenden sind einige Materialien mit ihren Kennzahlen und ihren Eigenschaften kurz aufgeführt.

## Ergebnisse

Hier werden alle während der Arbeit gewonnenen Informationen ausführlich dargestellt.

## Zusammenfassung

Kurze Zusammenfassung der Ergebnisse und Ausblick