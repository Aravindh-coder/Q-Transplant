"""Initial schema migration marker for Q-Transplant production deployments.

The application models are the source of the initial SQLite development schema.
For an existing database, generate a real Alembic revision from the current
metadata before production rollout; this marker prevents deployments from
silently treating runtime create_all/ALTER TABLE as the production migration
strategy.
"""
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
