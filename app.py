from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, desc
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'

engine = create_engine('sqlite:///posts.db')
conn = engine.connect()

metadate = MetaData()

PostDB = Table('posts', metadate,
               Column('id', Integer(), primary_key=True),
               Column('title', String(200), nullable=False),
               Column('slug', String(200), nullable=False),
               Column('text', Text, nullable=False),
               Column('date', DateTime, default=datetime.utcnow))

metadate.create_all(engine)


class FormPost(FlaskForm):
    title = StringField("Заголовок: ", validators=[DataRequired()])
    slug = StringField("Кратко: ", validators=[DataRequired()])
    text = TextAreaField("Текст: ", validators=[DataRequired()])
    submit = SubmitField('Отправить')


@app.route('/')
def index():
    t = PostDB.select().order_by(desc(PostDB.c.date))
    r = conn.execute(t)
    ans = r.fetchall()
    return render_template('index.html', objects=ans, title='POST')


@app.route('/post/<int:id>')
def post_id(id):
    pstid = f'POST #{id}'
    t = PostDB.select().where(PostDB.c.id == id)
    r = conn.execute(t)
    tt = r.fetchall()
    print(tt[0][4].date())
    return render_template('post-id.html', title=pstid, object=tt)


@app.route('/post/new', methods=['POST', 'GET'])
def post_new():
    form = FormPost()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = request.form['title']
            slug = request.form['slug']
            text = request.form['text']
            ins = PostDB.insert().values(
                {'title': title, 'slug': slug, 'text': text}
            )
            conn.execute(ins)
            conn.commit()
            return redirect(url_for('index'))
    # flash('Message Received', 'success')
    return render_template('post-new.html', form=form)


@app.route('/post/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    form = FormPost()
    ins = PostDB.select().where(PostDB.c.id == id)
    s = conn.execute(ins)
    ans = s.fetchall()[0]
    form.title.data = ans[1]
    form.slug.data = ans[2]
    form.text.data = ans[3]
    titlep = f'POST-{id} update'
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        text = request.form['text']
        s = PostDB.update().where(PostDB.c.id == id).values(title=title, slug=slug, text=text)
        upd = conn.execute(s)
        conn.commit()
        return redirect(url_for('post_id', id=id))
    return render_template('post-update.html', title=titlep, form=form, ans=ans)


@app.route('/post/<int:id>/delete', methods=['GET', 'POST'])
def post_delete(id):
    if request.method == 'POST':
        if request.form['del'] == 'yes':
            de = PostDB.delete().where(PostDB.c.id == id)
            ed = conn.execute(de)
            conn.commit()
            return redirect(url_for('index'))
        else:
            return redirect(url_for('post_id', id=id))

    titlep = f'delete post #{id}'
    d = PostDB.select().where(PostDB.c.id == id)
    s = conn.execute(d)
    a = s.fetchall()
    name = a[0][1]
    return render_template('post-delete.html', title=titlep, name=name)


if __name__ == '__main__':
    app.run(debug=True)
