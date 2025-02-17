# astrolabe
This repository has code to generate the climate plate of an astrolabe, also known as the tympanum. Code for the other components will be added at a later date.

The astrolabe is an ancient astronomical instrument. It can be used for determining local time given the latitude, determining latitude given the local time, identifying stars and planets, calculating astronomical positions precisely, solving various surveying and triangulation tasks, and so on. It is an example of an analog computer. 'The Astrolabe' by James Morrison is the ideal resource for any questions on it's history, construction and functions. There are many freely available resources online though, with it's Wikipedia page offering a good starting point (https://en.wikipedia.org/wiki/Astrolabe).

This code uses Pycairo, which can be tricky at times. I found that when running Anaconda, there can be issues with Pycairo. I personally resolved this with the command
  conda config --set auto_activate_base False
entered into terminal. When wishing to work with Anaconda once more, I'd just reset to True with
  conda config --set auto_activate_base True
as needed.
