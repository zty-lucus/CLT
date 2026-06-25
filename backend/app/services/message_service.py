"""
消息服务：消息存储、查询、转发业务逻辑
依赖: models/
"""
from datetime import datetime

from app import db
from app.models import Message, Conversation, ConversationMember, User


class MessageService:
    """消息业务逻辑封装"""

    @staticmethod
    def get_conversations(user_id):
        """获取用户的所有会话（含最后一条消息和未读数）"""
        memberships = (
            db.session.query(ConversationMember)
            .filter_by(user_id=user_id)
            .all()
        )
        conversation_ids = [m.conversation_id for m in memberships]
        if not conversation_ids:
            return []

        conversations = (
            db.session.query(Conversation)
            .filter(Conversation.id.in_(conversation_ids))
            .all()
        )
        result = []
        for conv in conversations:
            membership = next(
                (m for m in memberships if m.conversation_id == conv.id),
                None,
            )
            last_message = (
                db.session.query(Message)
                .filter_by(conversation_id=conv.id)
                .order_by(Message.created_at.desc())
                .first()
            )

            # 单聊：使用对方的昵称和头像
            conv_name = conv.name
            conv_avatar = conv.avatar
            if conv.type == 1 and (not conv_name or not conv_avatar):
                other_member = (
                    db.session.query(ConversationMember)
                    .filter_by(conversation_id=conv.id)
                    .filter(ConversationMember.user_id != user_id)
                    .first()
                )
                if other_member:
                    other_user = db.session.query(User).filter_by(id=other_member.user_id).first()
                    if other_user:
                        if not conv_name:
                            conv_name = other_user.nickname or other_user.username
                        if not conv_avatar:
                            conv_avatar = other_user.avatar

            result.append({
                'id': conv.id,
                'type': conv.type,
                'name': conv_name or '',
                'avatar': conv_avatar or '',
                'unread_count': membership.unread_count if membership else 0,
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'msg_type': last_message.msg_type if last_message else 1,
                    'created_at': (
                        last_message.created_at.isoformat()
                        if last_message and last_message.created_at
                        else None
                    ),
                } if last_message else None,
                'updated_at': (
                    conv.updated_at.isoformat()
                    if conv.updated_at else None
                ),
            })

        result.sort(
            key=lambda c: c['updated_at'] or '',
            reverse=True,
        )
        return result

    @staticmethod
    def get_conversation_detail(conversation_id, user_id):
        """获取会话详情（含对方信息/群信息）"""
        conv = db.session.query(Conversation).filter_by(id=conversation_id).first()
        if conv is None:
            return None

        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=conversation_id, user_id=user_id)
            .first()
        )
        if membership is None:
            return None

        members = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=conversation_id)
            .all()
        )
        member_list = []
        for m in members:
            user = db.session.query(User).filter_by(id=m.user_id).first()
            member_list.append({
                'user_id': m.user_id,
                'nickname': user.nickname if user else '',
                'avatar': user.avatar if user else '',
                'role': m.role,
            })

        return {
            'id': conv.id,
            'type': conv.type,
            'name': conv.name,
            'avatar': conv.avatar,
            'creator_id': conv.creator_id,
            'members': member_list,
            'created_at': (
                conv.created_at.isoformat()
                if conv.created_at else None
            ),
        }

    @staticmethod
    def create_private_conversation(user_id, target_id):
        """创建或查找单聊会话"""
        target_user = db.session.query(User).filter_by(id=target_id).first()
        if target_user is None:
            return None

        # 查找已存在的单聊会话
        user_convs = (
            db.session.query(ConversationMember.conversation_id)
            .filter_by(user_id=user_id)
            .subquery()
        )
        target_convs = (
            db.session.query(ConversationMember.conversation_id)
            .filter_by(user_id=target_id)
            .subquery()
        )
        existing = (
            db.session.query(Conversation)
            .filter(
                Conversation.type == 1,
                Conversation.id.in_(user_convs),
                Conversation.id.in_(target_convs),
            )
            .first()
        )
        if existing:
            return {
                'id': existing.id,
                'type': existing.type,
                'name': existing.name,
                'is_new': False,
            }

        # 创建新会话
        conv = Conversation(type=1, name='')
        db.session.add(conv)
        db.session.flush()

        db.session.add(ConversationMember(
            conversation_id=conv.id,
            user_id=user_id,
            role=0,
        ))
        db.session.add(ConversationMember(
            conversation_id=conv.id,
            user_id=target_id,
            role=0,
        ))
        db.session.commit()

        return {
            'id': conv.id,
            'type': conv.type,
            'name': conv.name,
            'is_new': True,
        }

    @staticmethod
    def get_messages(conversation_id, user_id, page=1, per_page=20):
        """获取历史消息（分页），验证用户是否属于该会话"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            .first()
        )
        if membership is None:
            return None

        total = (
            db.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .count()
        )
        messages = (
            db.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        message_list = []
        for msg in reversed(messages):
            sender = db.session.query(User).filter_by(id=msg.sender_id).first()
            message_list.append({
                'id': msg.id,
                'conversation_id': msg.conversation_id,
                'sender_id': msg.sender_id,
                'sender_nickname': sender.nickname if sender else '',
                'sender_avatar': sender.avatar if sender else '',
                'msg_type': msg.msg_type,
                'content': msg.content,
                'file_id': msg.file_id,
                'status': msg.status,
                'created_at': (
                    msg.created_at.isoformat()
                    if msg.created_at else None
                ),
            })

        return {
            'messages': message_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': page * per_page < total,
        }

    @staticmethod
    def save_message(sender_id, conversation_id, msg_type, content,
                     file_id=None):
        """保存消息到数据库"""
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            msg_type=msg_type,
            content=content,
            file_id=file_id,
            status=0,
        )
        db.session.add(message)

        # 更新会话时间戳
        conv = db.session.query(Conversation).filter_by(
            id=conversation_id
        ).first()
        if conv:
            conv.updated_at = datetime.utcnow()

        # 给其他成员增加未读计数
        memberships = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=conversation_id)
            .filter(ConversationMember.user_id != sender_id)
            .all()
        )
        for membership in memberships:
            membership.unread_count = (membership.unread_count or 0) + 1

        db.session.commit()

        sender = db.session.query(User).filter_by(id=sender_id).first()
        return {
            'id': message.id,
            'conversation_id': message.conversation_id,
            'sender_id': message.sender_id,
            'sender_nickname': sender.nickname if sender else '',
            'sender_avatar': sender.avatar if sender else '',
            'msg_type': message.msg_type,
            'content': message.content,
            'file_id': message.file_id,
            'status': message.status,
            'created_at': (
                message.created_at.isoformat()
                if message.created_at else None
            ),
        }

    @staticmethod
    def mark_read(conversation_id, user_id):
        """标记会话已读，清零未读计数"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=conversation_id, user_id=user_id)
            .first()
        )
        if membership:
            membership.unread_count = 0
            db.session.commit()

    @staticmethod
    def get_member_ids(conversation_id):
        """获取会话的所有成员ID列表（用于消息推送）"""
        memberships = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=conversation_id)
            .all()
        )
        return [m.user_id for m in memberships]
