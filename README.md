# <ins>__Arduino-radar__</ins>
Small arduino project with ultrasound sensor for radar mapping using **KiCad**, **ArduinoIDE** and **PyCharm** over serial comunication.

## Circuit schematic & setup (KiCad)
	Arduino Uno circuit; Servo PWM pin 9; Trig and Echo on 10 and 11 respectively

<p align="center">
  <img src="./img/circuit.png" width="48%" />
  <img src="./img/setup.jpg" width="48%" />
</p>

## Preliminary python based radar
![setup](./img/video.gif)

>![radar](./img/radargif.gif)

	Issues:
	- lacking error correction for occasional false positive
	- "0" case not hidden


