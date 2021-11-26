import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        #验证username和password不为空
        if not username:
            error = '需要填写用户名'
        elif not password:
            error = '需要填写密码'

        #查询数据库
        #使用？占位符自动转义输入值->抵御SQL注入攻击
        #                                                   占位符  填充占位符
        elif db.execute( 'SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        #

        if error is None:
            #执行插入新用户数据的SQL命令
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)',(username,generate_password_hash(password)))
            #保存修改
            db.commit()
            return redirect(url_for('auth.login'))#

        #将error信息存入flash，可以被渲染模块调用
        flash(error)

    return render_template('auth/register.html')#渲染注册表单


@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()


    #查询数据库，username和password是否成对存在
    #如果不存在返回错误信息
    #如果存在执行登录->用户登录信息写入session

        if user is None:
            error = '用户不存在'
        elif not check_password_hash(user['password'], password):
            error = '密码错误'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def loaf_logged_in_user():
    #检查用户 id 是否已经储存在 session 中，
    # 并从数据库中获取用户数据，然后储存在 g.user 中
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))

'''
input: 原视图
output：新视图

检查用户是否已登录
'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


