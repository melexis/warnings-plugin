
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
        #checkers : WarningsChecker
        +main()
    }

    class WarningsChecker {
        #min_count = 0
        #max_count = 0
        #count = 0

        #{abstract} __init__(regex=None)
        +set_limits(min_count=0, max_count=0,
        +check(line)
        +get_count()
    }

    class SphinxWarningsChecker {
        #{static} String regex
        +__init__()
    }

    class DoxygenWarningsChecker {
        #{static} String regex
        +__init__()
    }

    class JUnitFailuresChecker {
        #{static} String regex //todo: issue 20 (use junit parser)
        +__init__()
    }

    WarningsPlugin o-- WarningsChecker
    WarningsChecker <|-- SphinxWarningsChecker
    WarningsChecker <|-- DoxygenWarningsChecker
    WarningsChecker <|-- JUnitFailuresChecker

    @enduml


Instrument module
=================

.. automodule:: mlx.warnings
    :members:
    :undoc-members:
    :show-inheritance:
