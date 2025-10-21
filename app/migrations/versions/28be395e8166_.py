from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '28be395e8166'
down_revision: Union[str, Sequence[str], None] = 'c86a05b42286'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    op.drop_column('users', 'patronymic')

def downgrade() -> None:
    op.add_column('users', sa.Column('patronymic', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')

