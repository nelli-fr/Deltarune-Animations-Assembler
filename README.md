# Deltarune-Animations-Assembler
Mainly made to ease the sprite creation for [Deltarune Animation Software](https://github.com/aristhemage/Deltarune-Animation-Software) by [@aristhemage](https://github.com/aristhemage)

## How to use
 - put any spritesheets from [Spriter's Resource](https://www.spriters-resource.com/pc_computer/deltarune/) into the `in/` folder
 - run the script, it will output all animations to `out/x.gif`, where x is the number of the animation (eg. first processed animation would be saved as `1.gif`)

*the script assumes 5px gap between animation frames as it seems to be the case in all spritesheets*

### Minimal requirements
 - Python 3.5
 - NumPy 2.5.3
 - OpenCV 5.0.0.93