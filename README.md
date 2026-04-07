# Spritesheet Manager

A Krita manager for everything Spritesheet related!

## Installation

**Tools → Scripts → Import Python Plugin from file**
**Enable Spritesheet Manager and restart Krita**
**The Spritesheet Manager menu will appear in the top menu bar**

##

## Atlas Manager

Not yet implemented. Will allow assembling multiple spritesheets into a single texture atlas with drag and drop layout, live links to source files, and per-tileset sub-grid organisation.

## Spritesheet Editor

Tools for working on individual spritesheet files.

### Add Padding

**Spritesheet Manager → Sheet Editor → Add Padding**

Takes an existing spritesheet and produces a new one with configurable padding around every tile. Padding prevents texture bleeding in game engines that sample neighbouring pixels at tile edges during rendering.