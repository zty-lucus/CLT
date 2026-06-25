"""
群组服务：群组创建、成员管理、解散业务逻辑
依赖: models/
"""
from datetime import datetime

from app import db
from app.models import User, Conversation, ConversationMember, Message


class GroupService:
    """群组业务逻辑封装"""

    @staticmethod
    def get_user_groups(user_id):
        """获取用户加入的所有群组"""
        memberships = (
            db.session.query(ConversationMember)
            .filter_by(user_id=user_id)
            .all()
        )
        conv_ids = [m.conversation_id for m in memberships]

        groups = (
            db.session.query(Conversation)
            .filter(
                Conversation.id.in_(conv_ids),
                Conversation.type == 2,
            )
            .all()
        )
        result = []
        for group in groups:
            member_count = (
                db.session.query(ConversationMember)
                .filter_by(conversation_id=group.id)
                .count()
            )
            result.append({
                'id': group.id,
                'name': group.name,
                'avatar': group.avatar,
                'creator_id': group.creator_id,
                'member_count': member_count,
                'created_at': (
                    group.created_at.isoformat()
                    if group.created_at else None
                ),
            })
        return result

    @staticmethod
    def get_group_detail(group_id, user_id):
        """获取群组详情（含成员列表）"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None:
            return None

        conv = (
            db.session.query(Conversation)
            .filter_by(id=group_id, type=2)
            .first()
        )
        if conv is None:
            return None

        memberships = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id)
            .all()
        )
        member_list = []
        for m in memberships:
            user = db.session.query(User).filter_by(id=m.user_id).first()
            member_list.append({
                'user_id': m.user_id,
                'nickname': user.nickname if user else '',
                'avatar': user.avatar if user else '',
                'role': m.role,
                'joined_at': (
                    m.joined_at.isoformat()
                    if m.joined_at else None
                ),
            })

        return {
            'id': conv.id,
            'name': conv.name,
            'avatar': conv.avatar,
            'announcement': conv.announcement if hasattr(conv, 'announcement') else '',
            'creator_id': conv.creator_id,
            'my_role': membership.role,
            'members': member_list,
            'created_at': (
                conv.created_at.isoformat()
                if conv.created_at else None
            ),
        }

    @classmethod
    def create_group(cls, name, creator_id, member_ids):
        """创建群组：创建会话 + 添加成员"""
        conv = Conversation(
            type=2,
            name=name,
            creator_id=creator_id,
        )
        db.session.add(conv)
        db.session.flush()

        # 添加群主
        db.session.add(ConversationMember(
            conversation_id=conv.id,
            user_id=creator_id,
            role=2,
        ))
        # 添加初始成员
        member_ids = [mid for mid in member_ids if mid != creator_id]
        for mid in member_ids:
            user = db.session.query(User).filter_by(id=mid).first()
            if user:
                db.session.add(ConversationMember(
                    conversation_id=conv.id,
                    user_id=mid,
                    role=0,
                ))

        # 系统消息
        db.session.add(Message(
            conversation_id=conv.id,
            sender_id=creator_id,
            msg_type=4,
            content='群组已创建',
        ))
        db.session.commit()

        return {
            'id': conv.id,
            'name': conv.name,
            'type': conv.type,
            'creator_id': conv.creator_id,
        }

    @staticmethod
    def update_group(group_id, user_id, name=None, avatar=None,
                     announcement=None):
        """修改群信息（管理员及以上权限）"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None or membership.role < 1:
            return None

        conv = (
            db.session.query(Conversation)
            .filter_by(id=group_id, type=2)
            .first()
        )
        if conv is None:
            return None

        if name is not None:
            conv.name = name
        if avatar is not None:
            conv.avatar = avatar
        if announcement is not None:
            conv.announcement = announcement
        db.session.commit()

        return {
            'id': conv.id,
            'name': conv.name,
            'avatar': conv.avatar,
            'announcement': getattr(conv, 'announcement', ''),
        }

    @staticmethod
    def get_group_members(group_id, user_id):
        """获取群成员列表"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None:
            return None

        memberships = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id)
            .all()
        )
        member_list = []
        for m in memberships:
            user = db.session.query(User).filter_by(id=m.user_id).first()
            member_list.append({
                'user_id': m.user_id,
                'nickname': user.nickname if user else '',
                'avatar': user.avatar if user else '',
                'role': m.role,
                'joined_at': (
                    m.joined_at.isoformat()
                    if m.joined_at else None
                ),
            })
        return member_list

    @staticmethod
    def invite_members(group_id, user_id, invitee_ids):
        """邀请成员加入群组"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None:
            return None

        added = []
        for mid in invitee_ids:
            user = db.session.query(User).filter_by(id=mid).first()
            if user is None:
                continue
            existing = (
                db.session.query(ConversationMember)
                .filter_by(conversation_id=group_id, user_id=mid)
                .first()
            )
            if existing:
                continue
            db.session.add(ConversationMember(
                conversation_id=group_id,
                user_id=mid,
                role=0,
            ))
            added.append(mid)

        if added:
            names = []
            for mid in added:
                u = db.session.query(User).filter_by(id=mid).first()
                names.append(u.nickname if u else str(mid))
            db.session.add(Message(
                conversation_id=group_id,
                sender_id=user_id,
                msg_type=4,
                content=f'{"、".join(names)} 加入了群组',
            ))
            db.session.commit()

        return {'added_members': added}

    @staticmethod
    def remove_member(group_id, operator_id, target_id):
        """踢出群成员（管理员/群主踢人，不可踢自己或群主）"""
        operator_membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=operator_id)
            .first()
        )
        if operator_membership is None or operator_membership.role < 1:
            return None

        target_membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=target_id)
            .first()
        )
        if target_membership is None:
            return None
        # 不可踢群主
        if target_membership.role == 2:
            return None

        db.session.delete(target_membership)
        db.session.add(Message(
            conversation_id=group_id,
            sender_id=operator_id,
            msg_type=4,
            content=f'一位成员被移出群组',
        ))
        db.session.commit()
        return True

    @staticmethod
    def leave_group(group_id, user_id):
        """退出群组"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None:
            return None
        # 群主不可直接退出
        if membership.role == 2:
            return None

        db.session.delete(membership)
        db.session.commit()
        return True

    @staticmethod
    def dismiss_group(group_id, user_id):
        """解散群组（仅群主）"""
        membership = (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id, user_id=user_id)
            .first()
        )
        if membership is None or membership.role != 2:
            return None

        conv = (
            db.session.query(Conversation)
            .filter_by(id=group_id, type=2)
            .first()
        )
        if conv is None:
            return None

        # 删除所有成员
        (
            db.session.query(ConversationMember)
            .filter_by(conversation_id=group_id)
            .delete()
        )
        # 删除消息
        (
            db.session.query(Message)
            .filter_by(conversation_id=group_id)
            .delete()
        )
        # 删除会话
        db.session.delete(conv)
        db.session.commit()
        return True
