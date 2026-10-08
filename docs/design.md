# Software Design

## Layers

The package is built into two layers: Core primatives and Models built on those core primatives. 


| Layer   | Abstractions                                                 | Knowledge Needed   |
| ------- | ------------------------------------------------------------ | ---------- |
| Example | Actual devices and jobs                                      | models, core  |
| Model   | Models for devices and features                              | core |
| Core    | Primitives to build models. Wraps build123d for model makers. | build123d |


## Assembly 

## Terminology 

Names are chosen to not overlap the names used in build123. 