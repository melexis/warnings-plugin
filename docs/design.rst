
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
    }

    class WarningsChecker {
        #min_count = 0
        #max_count = 0
        #count = 0

        #{abstract} __init__(name)
        +set_limits(min_count=0, max_count=0,
        +{abstract}check(content)
        +get_count()
    }

    class RegexChecker {
        #{abstract} __init__(name, regex)
        +check(content)
    }

    class SphinxChecker {
        #{static} String name
        #{static} String regex
        +__init__()
    }

    class DoxyChecker {
        #{static} String name
        #{static} String regex
        +__init__()
    }

    class JUnitChecker {
        #{static} String name
        +__init__()
        +check(content)
    }

    WarningsPlugin o-- WarningsChecker
    WarningsChecker <|-- RegexChecker
    RegexChecker <|-- SphinxChecker
    RegexChecker <|-- DoxyChecker
    WarningsChecker <|-- JUnitChecker

    @enduml


Instrument module
=================

.. automodule:: mlx.warnings
    :members:
    :undoc-members:
    :show-inheritance:
