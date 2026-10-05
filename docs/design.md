# Software Design

## Layers

| Layer   | Abstractions                                                 | Knowledge Needed   |
| ------- | ------------------------------------------------------------ | ---------- |
| Example | Actual devices and jobs                                      | package.models, device  |
| Model   | Models for specific and general devices and features         | package.elements     |
| Element | Primitives to build models. Wraps build123d for model makers. | build123d |

