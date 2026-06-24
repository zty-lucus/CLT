import re

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}


def validate_username(username: str) -> tuple:
    if not username:
        return False, '用户名不能为空'
    if len(username) < 3 or len(username) > 20:
        return False, '用户名长度需为3~20个字符'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, '用户名只能包含字母、数字和下划线'
    return True, None


def validate_password(password: str) -> tuple:
    if not password:
        return False, '密码不能为空'
    if len(password) < 6 or len(password) > 32:
        return False, '密码长度需为6~32个字符'
    return True, None


def validate_email(email: str) -> tuple:
    if not email:
        return True, None
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确'
    return True, None


def validate_file(filename: str) -> tuple:
    if not filename or '.' not in filename:
        return False, '文件名无效'
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f'不支持的文件类型，允许：{", ".join(sorted(ALLOWED_EXTENSIONS))}'
    return True, None
