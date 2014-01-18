Servostat-interface
============

This is the python software for the klavins lab turbidostot (see http://depts.washington.edu/soslab for details)

Requirements
------------
* Python 2.7.x
   * Pyserial 2.7: https://pypi.python.org/pypi/pyserial
   * numpy: http://www.numpy.org/
   * pygments: (available through pip)

To install requirements, run:
$ sudo pip install numpy pygments pySerial


Configuration
------------------

For now see the official turbidostat page.


Known issues
-------------
All platforms:
* Not exiting via ctrl-C can leave orphaned threads that may interfere with 
later instances of the application, espeically on MacOS and *nix.

MacOS (and probably linux):
* Pumping volumes that take longer than 'period' seconds to process will result in a negative timer value being set, which in turn causes a timer overflow and the program to sleep for nearly 2^32 seconds (many years).
