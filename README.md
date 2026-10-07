# Deltarune animations assembler
Mainly made to ease the sprite creation for [Deltarune Animation Software](https://github.com/aristhemage/Deltarune-Animation-Software) developed by [@aristhemage](https://github.com/aristhemage)

## How to use
 - put any (Deltarune) spritesheets from [Spriter's Resource](https://www.spriters-resource.com/pc_computer/deltarune/) into the `in/` folder in the same directory as the script
 - run the script, it will output all animations to `out/<sheetname>/x.gif`, where `sheetname` is the filename of the spritesheet it was pulled from and `x` is the number of the animation (eg. first processed animation from file `noelle-1-4.png` would be saved in `out/noelle-1-4/1.gif`) \
 
! *the script assumes 5px gap between animation frames as it seems to be the case in all spritesheets* !

---

### Minimal requirements
 - Python 3.5
 - NumPy 2.5.3
 - OpenCV 5.0.0.93
 - Pillow 12.3.0