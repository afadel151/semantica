# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('app/storage', 'app/storage'),      # include DB + graph files
        ('alembic.ini', '.'),                 # if needed at runtime
        ('migrations', 'migrations'),         # if running migrations at startup
    ],
    hiddenimports=[
        # FastAPI and Uvicorn
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',

        # SQLAlchemy
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.postgresql',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.pool',

        # Alembic (if used at runtime)
        'alembic',
        'alembic.runtime.migration',
        'alembic.operations',

        # Your app modules
        'app',
        'app.main',
        'app.api',
        'app.api.main',
        'app.api.v1',
        'app.api.v1.helpers',
        'app.api.v1.helpers.ontology',
        'app.api.v1.helpers.rdf',
        'app.api.v1.routes',
        'app.api.v1.routes.namespace',   # was missing
        'app.api.v1.routes.ontology',    # was missing
        'app.api.v1.routes.rdf',         # was missing
        'app.api.v1.routes.reasoning',   # was missing
        'app.api.v1.routes.sparql',      # was missing
        'app.core',
        'app.core.db',
        # 'app.core.config',             # REMOVED — file doesn't exist
        'app.models',
        'app.models.namespace',
        'app.models.ontology',
        'app.models.query_ontology',
        'app.models.rdf',
        'app.models.reasoning',
        'app.models.sparql',
        'app.utils',

        # Pydantic
        'pydantic',
        'pydantic.json',
        'pydantic_core',

        # RDF/OWL — add whichever you use
        'rdflib',
        'rdflib.plugins',
        'rdflib.plugins.parsers',
        'rdflib.plugins.parsers.rdfxml',
        'rdflib.plugins.serializers',
        'owlready2',                     # if used
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)