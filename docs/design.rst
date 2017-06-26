
.. _software_design:

===============
Software design
===============

.. _class_diagram:

Class diagram
=============

.. uml::

    @startuml
    class WarningsChecker {
        #min_count = 0
        #max_count = 0
        #count = 0

        #{abstract} __init__(min_count=0, max_count=0, regex=None)
        +check(line)
        +get_count()
    }

    class SphinxWarningsChecker {
        #{static} String regex
        +__init__(min_count=0, max_count=0)
    }

    class DoxygenWarningsChecker {
        #{static} String regex
        +__init__(min_count=0, max_count=0)
    }

    class JUnitFailuresChecker {
        #{static} String regex //todo: issue 20 (use junit parser)
        +__init__(min_count=0, max_count=0)
    }

    WarningsChecker <|-- SphinxWarningsChecker
    WarningsChecker <|-- DoxygenWarningsChecker
    WarningsChecker <|-- JUnitFailuresChecker

    @enduml
