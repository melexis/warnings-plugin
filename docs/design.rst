
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml
    class WarningsPlugin {
        #checkerList : WarningsChecker
        +__init__(sphinx=False, doxygen=False, junit=False, verbose=False)
    }

    class WarningsChecker {
        #min_count = 0
        #max_count = 0
        #count = 0
        #verbose = False

        #{abstract} __init__(name, verbose=False)
        +set_limits(min_count=0, max_count=0,
        +{abstract}check(content)
        +get_count()
    }

    class RegexChecker {
        #{abstract} __init__(name, regex, verbose=False)
        +check(content)
    }

    class SphinxChecker {
        #{static} String name
        #{static} String regex
        +__init__(verbose=False)
    }

    class DoxyChecker {
        #{static} String name
        #{static} String regex
        +__init__(verbose=False)
    }

    class JUnitChecker {
        #{static} String name
        +__init__(verbose=False)
        +check(content)
    }

    WarningsPlugin o-- WarningsChecker
    WarningsChecker <|-- RegexChecker
    RegexChecker <|-- SphinxChecker
    RegexChecker <|-- DoxyChecker
    WarningsChecker <|-- JUnitChecker

    @enduml

String handling
===============

Convention is to use plain python strings everywhere. Where needed the strings can be converted to anything else.

Example: junitparser expects byte array objects, so we encode our string right before passing it to junitparser.

Instrument module
=================

.. automodule:: mlx.warnings
    :members:
    :undoc-members:
    :show-inheritance:
