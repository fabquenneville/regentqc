==========
Quickstart
==========

.. code-block:: bash

    regentqc [foo,bar] [-del] [-foo:foo,bar] [-bar:foo,bar]

** Warning dont do this other thing **

default options are:

.. code-block:: bash

    -foo:foo
    -bar:

Examples:

.. code-block:: bash

    # Do this
    regentqc foo -del -foo:bar -bar:foo
    # Do that
    regentqc bar -foo:foo

More examples in :doc:`use_cases`