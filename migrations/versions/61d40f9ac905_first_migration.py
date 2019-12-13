"""first migration

Revision ID: 61d40f9ac905
Revises: 
Create Date: 2019-12-13 14:21:36.138569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61d40f9ac905'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_line',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_number', sa.Integer(), nullable=True),
    sa.Column('time_for_start', sa.DateTime(), nullable=True),
    sa.Column('time_lag', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('connection_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_of_type', sa.String(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('date_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day_date', sa.DateTime(), nullable=True),
    sa.Column('day_name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('master_news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('published', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('my_work',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_site', sa.String(length=255), nullable=True),
    sa.Column('published', sa.DateTime(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('code', sa.String(length=250), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('owner', sa.String(length=255), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('show', sa.Boolean(), nullable=False),
    sa.Column('source', sa.Text(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_table('news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=255), nullable=False),
    sa.Column('main_picture_url', sa.Text(), nullable=True),
    sa.Column('published', sa.DateTime(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('show', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_table('preliminary_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_of_client', sa.String(length=255), nullable=True),
    sa.Column('phone_of_client', sa.BigInteger(), nullable=True),
    sa.Column('message_of_client', sa.Text(), nullable=True),
    sa.Column('message_worked', sa.Integer(), nullable=True),
    sa.Column('time_to_record', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('russian_mobil_operator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Operator', sa.String(length=250), nullable=True),
    sa.Column('Count', sa.String(length=250), nullable=True),
    sa.Column('Count_parse', sa.BigInteger(), nullable=True),
    sa.Column('Note', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('work_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('priority_to_show', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('code_zone',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Code', sa.Integer(), nullable=True),
    sa.Column('ZoneText', sa.String(length=250), nullable=True),
    sa.Column('Count', sa.String(length=250), nullable=True),
    sa.Column('Count_parse', sa.BigInteger(), nullable=True),
    sa.Column('RussianMobilOperator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['RussianMobilOperator_id'], ['russian_mobil_operator.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments_to_my_works',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_site', sa.String(length=255), nullable=True),
    sa.Column('media', sa.String(length=255), nullable=True),
    sa.Column('owner', sa.String(length=255), nullable=True),
    sa.Column('published', sa.DateTime(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('show', sa.Boolean(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=True),
    sa.Column('my_work_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['my_work_id'], ['my_work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_to_my_works_my_work_id'), 'comments_to_my_works', ['my_work_id'], unique=False)
    op.create_table('price_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('discount', sa.Integer(), nullable=True),
    sa.Column('work_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['work_type_id'], ['work_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('schedule_of_day',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('begin_time_of_day', sa.DateTime(), nullable=True),
    sa.Column('end_time_of_day', sa.DateTime(), nullable=True),
    sa.Column('work_type', sa.String(length=255), nullable=True),
    sa.Column('cost', sa.Integer(), nullable=True),
    sa.Column('name_of_client', sa.String(length=255), nullable=True),
    sa.Column('mail_of_client', sa.String(length=255), nullable=True),
    sa.Column('phone_of_client', sa.String(length=255), nullable=True),
    sa.Column('adress_of_client', sa.String(length=255), nullable=True),
    sa.Column('note', sa.String(length=255), nullable=True),
    sa.Column('connection_type', sa.Integer(), nullable=True),
    sa.Column('connection_type_str', sa.String(length=255), nullable=True),
    sa.Column('client_come_in', sa.Integer(), nullable=True),
    sa.Column('is_empty', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('info_message_for_client', sa.Integer(), nullable=True),
    sa.Column('remind_message_for_client', sa.Integer(), nullable=True),
    sa.Column('date_table_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['date_table_id'], ['date_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('about_me', sa.Text(length=1024), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('email_confirmed', sa.Integer(), nullable=True),
    sa.Column('expire_date_request_confirm_password', sa.DateTime(), nullable=True),
    sa.Column('expire_date_request_bufer_mail', sa.DateTime(), nullable=True),
    sa.Column('bufer_email', sa.String(length=120), nullable=True),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.Column('user_from_master', sa.Integer(), nullable=True),
    sa.Column('trying_to_enter_new_phone', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('role', sa.String(length=10), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('connection_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['connection_type_id'], ['connection_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_role'), 'user', ['role'], unique=False)
    op.create_table('comments_to_news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('show', sa.Integer(), nullable=True),
    sa.Column('news_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_to_news_news_id'), 'comments_to_news', ['news_id'], unique=False)
    op.create_index(op.f('ix_comments_to_news_user_id'), 'comments_to_news', ['user_id'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('nail_master',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('work_phone', sa.BigInteger(), nullable=True),
    sa.Column('work_instagram', sa.Text(), nullable=True),
    sa.Column('work_vk', sa.Text(), nullable=True),
    sa.Column('work_telegram', sa.Text(), nullable=True),
    sa.Column('work_mail', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(length=5), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_internet_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('adress_accaunt', sa.String(length=255), nullable=True),
    sa.Column('black_list', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('adress_accaunt')
    )
    op.create_table('user_phones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number', sa.BigInteger(), nullable=True),
    sa.Column('phone_hash_code', sa.String(length=255), nullable=True),
    sa.Column('phone_checked', sa.Integer(), nullable=False),
    sa.Column('expire_date_hash', sa.DateTime(), nullable=True),
    sa.Column('user_from_master', sa.Integer(), nullable=True),
    sa.Column('black_list', sa.Integer(), nullable=True),
    sa.Column('trying_to_enter_confirm_code', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_phones')
    op.drop_table('user_internet_account')
    op.drop_table('post')
    op.drop_table('nail_master')
    op.drop_table('followers')
    op.drop_index(op.f('ix_comments_to_news_user_id'), table_name='comments_to_news')
    op.drop_index(op.f('ix_comments_to_news_news_id'), table_name='comments_to_news')
    op.drop_table('comments_to_news')
    op.drop_index(op.f('ix_user_role'), table_name='user')
    op.drop_table('user')
    op.drop_table('schedule_of_day')
    op.drop_table('price_list')
    op.drop_index(op.f('ix_comments_to_my_works_my_work_id'), table_name='comments_to_my_works')
    op.drop_table('comments_to_my_works')
    op.drop_table('code_zone')
    op.drop_table('work_type')
    op.drop_table('russian_mobil_operator')
    op.drop_table('preliminary_record')
    op.drop_table('news')
    op.drop_table('my_work')
    op.drop_table('master_news')
    op.drop_table('date_table')
    op.drop_table('connection_type')
    op.drop_table('action_line')
    # ### end Alembic commands ###
