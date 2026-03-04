"""create graphs, subjects, predicates, objects, sparql_history

Revision ID: 0001_initial
Revises: –
Create Date: 2026-03-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    #  graphs 
    op.create_table(
        "graphs",
        sa.Column("id",            sa.String(),  primary_key=True),
        sa.Column("name",          sa.String(),   nullable=False),
        sa.Column("format",        sa.String(),   nullable=False),
        sa.Column("file_name",     sa.String(),   nullable=False),
        sa.Column("file_path",     sa.String(),   nullable=False),
        sa.Column("file_size",     sa.Integer(),  nullable=False),
        sa.Column("triples_count", sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("uploaded_at",   sa.DateTime(), nullable=False,
                  server_default=sa.text("(datetime('now'))")),
    )

    #  subjects 
    op.create_table(
        "subjects",
        sa.Column("id",              sa.String(),  primary_key=True),
        sa.Column("graph_id",        sa.String(),  sa.ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uri",             sa.String(),  nullable=False),
        sa.Column("prefix_form",     sa.String(),  nullable=True),
        sa.Column("rdf_type",        sa.String(),  nullable=True),
        sa.Column("predicate_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_subjects_graph_id", "subjects", ["graph_id"])

    #  predicates 
    op.create_table(
        "predicates",
        sa.Column("id",          sa.String(),  primary_key=True),
        sa.Column("graph_id",    sa.String(),  sa.ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uri",         sa.String(),  nullable=False),
        sa.Column("prefix_form", sa.String(),  nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("domain",      sa.String(),  nullable=True),
        sa.Column("range",       sa.String(),  nullable=True),
    )
    op.create_index("ix_predicates_graph_id", "predicates", ["graph_id"])

    #  objects 
    op.create_table(
        "objects",
        sa.Column("id",            sa.String(),  primary_key=True),
        sa.Column("graph_id",      sa.String(),  sa.ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value",         sa.String(),  nullable=False),
        sa.Column("kind",          sa.String(),  nullable=False),  # uri | literal | blank
        sa.Column("prefix_form",   sa.String(),  nullable=True),
        sa.Column("datatype",      sa.String(),  nullable=True),
        sa.Column("language",      sa.String(),  nullable=True),
        sa.Column("referenced_by", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_objects_graph_id", "objects", ["graph_id"])

    #  sparql_history 
    op.create_table(
        "sparql_history",
        sa.Column("id",          sa.String(),  primary_key=True),
        sa.Column("query",       sa.String(),  nullable=False),
        sa.Column("query_type",  sa.String(),  nullable=False),
        sa.Column("graph_id",    sa.String(),  sa.ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=False,
                  server_default=sa.text("(datetime('now'))")),
    )
    op.create_index("ix_sparql_history_graph_id", "sparql_history", ["graph_id"])

    # ontologies

    op.create_table(
        "ontologies",
        sa.Column("id",                sa.String(),  primary_key=True),
        sa.Column("name",              sa.String(),  nullable=False),
        sa.Column("format",            sa.String(),  nullable=False),
        sa.Column("file_name",         sa.String(),  nullable=False),
        sa.Column("file_path",         sa.String(),  nullable=False),
        sa.Column("file_size",         sa.Integer(),  nullable=False),
        sa.Column("classes_count",     sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("properties_count",  sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("individuals_count", sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("uploaded_at",       sa.DateTime(), nullable=False,
                  server_default=sa.text("(datetime('now'))")),
    )

    op.create_table(
        "classes",
        sa.Column("id",          sa.String(),  primary_key=True),
        sa.Column("ontology_id", sa.String(),  sa.ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uri",         sa.String(),  nullable=False),
        sa.Column("label",       sa.String(),  nullable=True),
        sa.Column("prefix_form", sa.String(),  nullable=True),
        sa.Column("parent_uri",  sa.String(),  nullable=True),
        sa.Column("children_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_abstract", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("depth",       sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "properties",
        sa.Column("id",          sa.String(),  primary_key=True),
        sa.Column("ontology_id", sa.String(),  sa.ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uri",         sa.String(),  nullable=False),
        sa.Column("label",       sa.String(),  nullable=True),
        sa.Column("prefix_form", sa.String(),  nullable=True),
        sa.Column("type",        sa.String(),  nullable=True),  # owl:ObjectProperty | owl:DatatypeProperty
        sa.Column("domain",      sa.String(),  nullable=True),
        sa.Column("range",       sa.String(),  nullable=True),
    )

    op.create_table(
        "individuals",
        sa.Column("id",          sa.String(),  primary_key=True),
        sa.Column("ontology_id", sa.String(),  sa.ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uri",         sa.String(),  nullable=False),
        sa.Column("label",       sa.String(),  nullable=True),
        sa.Column("prefix_form", sa.String(),  nullable=True),
        sa.Column("rdf_type",    sa.String(),  nullable=True),
    )

    op.create_table(
        "query_ontologies",
        sa.Column("query_id",    sa.String(),  sa.ForeignKey("sparql_history.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ontology_id", sa.String(),  sa.ForeignKey("ontologies.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("query_ontologies")

    op.drop_table("individuals")
    op.drop_table("properties")
    op.drop_table("classes")

    op.drop_table("objects")
    op.drop_table("predicates")
    op.drop_table("subjects")

    op.drop_table("sparql_history")

    op.drop_table("ontologies")
    op.drop_table("graphs")