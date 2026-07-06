# Developer´s guide

## guidelines

1. this aims to be a 100% python; when not possible, 100% open-source; when not possible, it will be part of the roadmap.
2. this aims to be modular.
3. this aims to be 100% typed. We use mypy with Protocols to ensure consistency. ABCs are also appropiated if justified.
4. this aims to be 100% test coverage.
5. the development direction is based on the wishlist,  but the progress in different parts depend on the developers' interests and current research.

## architecture


### protocols
protocols are an esential part of the antupy development, as they ensure consistency throughout the project and reduce bugs. Protocols are a new introduced typing concept (PEP 544) allowing structural subtyping, also called static duck typing.
There are two types of protocols in antupy. The software level protocols are defined in protos.py. They define the base interfaces, and they serve as a blueprint for specific module's objects. They define the methods that the modules' objects are expected to have to interact with the rest of the software.
Specific software can also have their own protocols, although they are valid only inside their scope.

For a parametric analysis, all the atributes should be either strings or Variable

### 100% typed
it is recommended to install mypy and run it frequently. It is possible to run it everytime you save your files (with an extension). I do run it permanently in the background. If you can live with these constant red warnings, go on. Your final code must pass mypy to be accepted in production.

## Wishlist

### 003: parametric analyser
so far, only with one level of attributes
capabilities of interest:
 - .params_in: so far only Variable and Categorical. future with Callable and instances.
 - .settings() with all combinations (with itertools).
 - .settings() with linked variables (functions? freeze? dict?). option: ([], by=[], with=[])
 - .settings() with list of instances?

