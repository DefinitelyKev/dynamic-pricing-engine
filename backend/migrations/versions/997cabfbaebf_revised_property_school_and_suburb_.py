"""revised property, school and suburb model to match scraper and remove pricing

Revision ID: 997cabfbaebf
Revises: a8c8e443a43f
Create Date: 2025-02-16 22:23:45.624767

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "997cabfbaebf"
down_revision: Union[str, None] = "a8c8e443a43f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "property_school",
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("school_id", sa.Integer(), nullable=False),
        sa.Column("distance", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["property.id"],
        ),
        sa.ForeignKeyConstraint(
            ["school_id"],
            ["school.id"],
        ),
        sa.PrimaryKeyConstraint("property_id", "school_id"),
    )
    op.drop_table("suburb_surroundings")
    op.drop_table("priceadjustment")
    op.drop_index("ix_pricingrule_name", table_name="pricingrule")
    op.drop_table("pricingrule")
    op.drop_table("propertyevent")
    op.add_column("property", sa.Column("listing_mode", sa.String(), nullable=True))
    op.add_column("property", sa.Column("listing_method", sa.String(), nullable=True))
    op.add_column("property", sa.Column("features", postgresql.ARRAY(sa.String()), nullable=False))
    op.add_column("property", sa.Column("structured_features", postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    op.add_column("property", sa.Column("address", sa.String(), nullable=True))
    op.alter_column("property", "type", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "display_price", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "listing_status", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "bedrooms", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("property", "bathrooms", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("property", "parking_spaces", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "property", "land_area", existing_type=sa.DOUBLE_PRECISION(precision=53), type_=sa.Integer(), nullable=False
    )
    op.alter_column("property", "street_number", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "street_name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "suburb_name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "postcode", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("property", "state", existing_type=sa.VARCHAR(), nullable=True)
    op.execute("ALTER TABLE property ALTER COLUMN images TYPE VARCHAR[] USING (images::text::varchar[])")
    op.drop_index("ix_property_property_id", table_name="property")
    op.create_index(op.f("ix_property_id"), "property", ["id"], unique=False)
    op.create_unique_constraint(None, "property", ["listing_url"])
    op.drop_column("property", "internal_area")
    op.drop_column("property", "region")
    op.drop_column("property", "property_id")
    op.drop_column("property", "longitude")
    op.drop_column("property", "area")
    op.drop_column("property", "display_address")
    op.drop_column("property", "suburb_insights")
    op.drop_column("property", "category")
    op.drop_column("property", "latitude")
    op.drop_column("property", "listing_type")
    op.drop_column("property", "street_type")
    op.drop_column("property", "market_stats")
    op.add_column("school", sa.Column("education_level", sa.String(), nullable=True))
    op.add_column("school", sa.Column("state", sa.String(), nullable=True))
    op.add_column("school", sa.Column("postcode", sa.String(), nullable=True))
    op.alter_column("school", "name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("school", "type", existing_type=sa.VARCHAR(), nullable=True)
    op.create_index(op.f("ix_school_id"), "school", ["id"], unique=False)
    op.drop_constraint("school_property_id_fkey", "school", type_="foreignkey")
    op.drop_column("school", "distance")
    op.drop_column("school", "sector")
    op.drop_column("school", "property_id")
    op.add_column("suburb", sa.Column("suburb_profile_url", sa.String(), nullable=False))
    op.alter_column(
        "suburb",
        "sales_growth",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    )
    op.create_unique_constraint(None, "suburb", ["suburb_profile_url"])
    op.drop_column("suburb", "properties_for_sale")
    op.drop_column("suburb", "area")
    op.drop_column("suburb", "region")
    op.drop_column("suburb", "properties_for_rent")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("suburb", sa.Column("properties_for_rent", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column("suburb", sa.Column("region", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("suburb", sa.Column("area", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("suburb", sa.Column("properties_for_sale", sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, "suburb", type_="unique")
    op.alter_column(
        "suburb",
        "sales_growth",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=postgresql.JSON(astext_type=sa.Text()),
        nullable=False,
    )
    op.drop_column("suburb", "suburb_profile_url")
    op.add_column("school", sa.Column("property_id", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column("school", sa.Column("sector", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column(
        "school", sa.Column("distance", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False)
    )
    op.create_foreign_key("school_property_id_fkey", "school", "property", ["property_id"], ["id"])
    op.drop_index(op.f("ix_school_id"), table_name="school")
    op.alter_column("school", "type", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("school", "name", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("school", "postcode")
    op.drop_column("school", "state")
    op.drop_column("school", "education_level")
    op.add_column(
        "property",
        sa.Column("market_stats", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    )
    op.add_column("property", sa.Column("street_type", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column("property", sa.Column("listing_type", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column(
        "property", sa.Column("latitude", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True)
    )
    op.add_column("property", sa.Column("category", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column(
        "property",
        sa.Column("suburb_insights", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    )
    op.add_column("property", sa.Column("display_address", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column("property", sa.Column("area", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "property", sa.Column("longitude", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True)
    )
    op.add_column("property", sa.Column("property_id", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column("property", sa.Column("region", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "property", sa.Column("internal_area", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True)
    )
    op.drop_constraint(None, "property", type_="unique")
    op.drop_index(op.f("ix_property_id"), table_name="property")
    op.create_index("ix_property_property_id", "property", ["property_id"], unique=False)
    op.alter_column(
        "property",
        "images",
        existing_type=postgresql.ARRAY(sa.String()),
        type_=postgresql.JSON(astext_type=sa.Text()),
        existing_nullable=False,
    )
    op.alter_column("property", "state", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "postcode", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "suburb_name", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "street_name", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "street_number", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        "property", "land_area", existing_type=sa.Integer(), type_=sa.DOUBLE_PRECISION(precision=53), nullable=True
    )
    op.alter_column("property", "parking_spaces", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("property", "bathrooms", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("property", "bedrooms", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("property", "listing_status", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "display_price", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("property", "type", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("property", "address")
    op.drop_column("property", "structured_features")
    op.drop_column("property", "features")
    op.drop_column("property", "listing_method")
    op.drop_column("property", "listing_mode")
    op.create_table(
        "propertyevent",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("property_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("event_price", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
        sa.Column("event_date", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("agency", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("category", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("days_on_market", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("price_description", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["property.id"], name="propertyevent_property_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="propertyevent_pkey"),
    )
    op.create_table(
        "pricingrule",
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "conditions",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
            comment="E.g., {'property_type': 'House', 'suburb': 'Calga'}",
        ),
        sa.Column(
            "adjustments",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
            comment="E.g., {'type': 'percentage', 'value': 10}",
        ),
        sa.Column("priority", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('pricingrule_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("rule_type", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "stats",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
            comment="Rule application statistics",
        ),
        sa.PrimaryKeyConstraint("id", name="pricingrule_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_index("ix_pricingrule_name", "pricingrule", ["name"], unique=False)
    op.create_table(
        "priceadjustment",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("property_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("rule_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("original_price", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("adjusted_price", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("adjustment_type", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("adjustment_value", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
        sa.Column(
            "market_conditions",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
            comment="Market conditions when adjustment was made",
        ),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["property.id"], name="priceadjustment_property_id_fkey"),
        sa.ForeignKeyConstraint(["rule_id"], ["pricingrule.id"], name="priceadjustment_rule_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="priceadjustment_pkey"),
    )
    op.create_table(
        "suburb_surroundings",
        sa.Column("suburb_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("surrounding_suburb_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["suburb_id"], ["suburb.id"], name="suburb_surroundings_suburb_id_fkey"),
        sa.ForeignKeyConstraint(
            ["surrounding_suburb_id"], ["suburb.id"], name="suburb_surroundings_surrounding_suburb_id_fkey"
        ),
        sa.PrimaryKeyConstraint("suburb_id", "surrounding_suburb_id", name="suburb_surroundings_pkey"),
    )
    op.drop_table("property_school")
    # ### end Alembic commands ###
