# ok

Die Telefon-Klingel braucht 12 V. Das kann der Arduino nicht liefern, deshalb ist das weitere Board dazwischen geschaltet, an das das 12 V Netzteil angeschlossen wird. Die Klingel funktioniert, indem sich die Pole schnell ändern. Es gibt kein "rechts oder links / falsch oder richtig". Sollte auch in der entsprechenden Python Funktion ablesbar sein.

Die aktuelle Konfigutation der Kabel am Arduino und der Platine ist als Foto abgelegt

Der Telefonhörer geht einfach per Klinke als Headset in den NUC. Die größte Lautstärke wird in Debian mit der Einstellung "mono" erreicht (aktuell meine ich gerade nicht so konfiguriert.

Die untere Platte des Telefons ist von innen/oben mit Holzschrauben auf der Brett des schwarz angestrichenen Gehäuses geschraubt. Um den Deckel des Telefons zu öffnen (um an die Holzschrauebn kommen) müssen von unter dem Brett die zwei parallelen, vorderen Metall-Schrauben gelöst werden. Diese sind in den oberen Teil der Telefon-Abdeckung geschraubt und so gesichert, dass sie nicht aus dem Boden des Telefons fallen können. Im Holbrett sind dafür Bohrungen vorgesehen, um die Schrauben im Telefongehäuse lösen zu können. Die hintere, einzelne Schraube am Hehäuseboden habe ich mit dem Loch in der Holzplatte nicht richtig getroffen und kann deshalb nicht festgeschraubt werden (muss aber auch nicht gelöst werden).

Für die grünen Laser: Den An-Schalter der Laser-Geräte nur bei gut sitzendem Akku umlegen! Mit dem physischen umlegen der Schalter scheint sich auch eine Lagesicherung zu lösen. Mit Stromversorgung scheint sich das System zu stabilisieren. Ohne Strom (richtig sitzendem Akku) gehen die Laser schnell kaputt. Ein Laser kann von vorne angeschaltet werden, der andere durch ein Loch in der Rückwand. Neben dem Umlegen des Schalter müssen zusätzlich noch die horizontalen Laser ausmachen und die vertikalen angemacht werden. Dazu auf die oben an den Geräten angebrachten Knöpfe drücken: H (horizontal) und V (vertiakl, mehrfach drücken für beide Linien gleichzeig). Der Linke laser ist kaputt und kann nur noch einen vertikalen Strahl absenden.
Wahrscheinlich ist zum Zugang zu den oben angebrachten H- und V-Knöpfen der Laser eine Ausbildung der vorderen Abdeckung als Tür mit Scharnieren und einem Vorhängeschloss / einer einzelnen Schraube am geschicktesten. 
In der vorderen Platte feheln für die Laser wahrscheinlich in der vorderen und von vorne linken Platte noch Schlitze, um die Strahlen weiter in den Raum zu schicken.

Der Remote-Zugang über SSH ist aktuell über remote.it eingerichtet. Bei dem Rechner handelt es sich um einen Intel NUC mit i5 8th Generation und 8 GB RAM. Betriebssystem ist Debian, ich meine 10.
