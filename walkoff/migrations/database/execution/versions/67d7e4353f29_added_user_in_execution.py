"""Added user in execution

Revision ID: 67d7e4353f29
Revises: de7dd1e1487c
Create Date: 2018-11-19 12:32:29.099993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67d7e4353f29'
down_revision = 'de7dd1e1487c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('environment_variable')
    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_action_workflow_id_workflow'), 'workflow', ['workflow_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('action_metric', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_action_metric_app_metric_id_app_metric'), 'app_metric', ['app_metric_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('action_status', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_action_status__workflow_status_id_workflow_status'), 'workflow_status', ['_workflow_status_id'], ['execution_id'], ondelete='CASCADE')

    with op.batch_alter_table('action_status_metric', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_action_status_metric_action_metric_id_action_metric'), 'action_metric', ['action_metric_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('argument', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_argument_action_id_action'), 'action', ['action_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_argument_condition_id_condition'), 'condition', ['condition_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_argument_transform_id_transform'), 'transform', ['transform_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_argument_action_device_id_action'), 'action', ['action_device_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_branch_workflow_id_workflow'), 'workflow', ['workflow_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('condition', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_condition_conditional_expression_id_conditional_expression'), 'conditional_expression', ['conditional_expression_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('conditional_expression', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_conditional_expression_branch_id_branch'), 'branch', ['branch_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_conditional_expression_action_id_action'), 'action', ['action_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_conditional_expression_parent_id_conditional_expression'), 'conditional_expression', ['parent_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_device_app_id_app'), 'app', ['app_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('encrypted_device_field', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_encrypted_device_field_device_id_device'), 'device', ['device_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('plaintext_device_field', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_plaintext_device_field_device_id_device'), 'device', ['device_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('playbook', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_playbook_name'), ['name'])

    with op.batch_alter_table('position', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_position_action_id_action'), 'action', ['action_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('saved_workflow', schema=None) as batch_op:
        batch_op.drop_column('accumulator')

    with op.batch_alter_table('transform', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_transform_condition_id_condition'), 'condition', ['condition_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('workflow', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_workflow_playbook_id_playbook'), 'playbook', ['playbook_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('workflow_status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workflow_status', schema=None) as batch_op:
        batch_op.drop_column('user')

    with op.batch_alter_table('workflow', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_workflow_playbook_id_playbook'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'playbook', ['playbook_id'], ['id'])

    with op.batch_alter_table('transform', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_transform_condition_id_condition'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'condition', ['condition_id'], ['id'])

    with op.batch_alter_table('saved_workflow', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accumulator', sa.BLOB(), nullable=False))

    with op.batch_alter_table('position', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_position_action_id_action'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'action', ['action_id'], ['id'])

    with op.batch_alter_table('playbook', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_playbook_name'), type_='unique')

    with op.batch_alter_table('plaintext_device_field', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_plaintext_device_field_device_id_device'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'device', ['device_id'], ['id'])

    with op.batch_alter_table('encrypted_device_field', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_encrypted_device_field_device_id_device'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'device', ['device_id'], ['id'])

    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_device_app_id_app'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'app', ['app_id'], ['id'])

    with op.batch_alter_table('conditional_expression', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_conditional_expression_parent_id_conditional_expression'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_conditional_expression_action_id_action'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_conditional_expression_branch_id_branch'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'conditional_expression', ['parent_id'], ['id'])
        batch_op.create_foreign_key(None, 'branch', ['branch_id'], ['id'])
        batch_op.create_foreign_key(None, 'action', ['action_id'], ['id'])

    with op.batch_alter_table('condition', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_condition_conditional_expression_id_conditional_expression'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'conditional_expression', ['conditional_expression_id'], ['id'])

    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_branch_workflow_id_workflow'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'workflow', ['workflow_id'], ['id'])

    with op.batch_alter_table('argument', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_argument_action_device_id_action'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_argument_transform_id_transform'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_argument_condition_id_condition'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_argument_action_id_action'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'condition', ['condition_id'], ['id'])
        batch_op.create_foreign_key(None, 'action', ['action_id'], ['id'])
        batch_op.create_foreign_key(None, 'action', ['action_device_id'], ['id'])
        batch_op.create_foreign_key(None, 'transform', ['transform_id'], ['id'])

    with op.batch_alter_table('action_status_metric', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_action_status_metric_action_metric_id_action_metric'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'action_metric', ['action_metric_id'], ['id'])

    with op.batch_alter_table('action_status', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_action_status__workflow_status_id_workflow_status'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'workflow_status', ['_workflow_status_id'], ['execution_id'])

    with op.batch_alter_table('action_metric', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_action_metric_app_metric_id_app_metric'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'app_metric', ['app_metric_id'], ['id'])

    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_action_workflow_id_workflow'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'workflow', ['workflow_id'], ['id'])

    op.create_table('environment_variable',
    sa.Column('id', sa.CHAR(length=32), nullable=False),
    sa.Column('workflow_id', sa.CHAR(length=32), nullable=True),
    sa.Column('name', sa.VARCHAR(length=80), nullable=True),
    sa.Column('value', sa.VARCHAR(length=80), nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['workflow_id'], ['workflow.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###