import secrets
import os
from PIL import Image
from flask import abort, render_template, url_for, flash, redirect, request
from flask_login import login_required, login_user, current_user, logout_user
from application import app,db,bcrypt
from application.forms import RegistrationForm, LoginForm, SearchForm, UpdateAccountForm, factorForm


from application.models import User, Factor

#Pass stuff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict (form=form)
 

# create Search function
@app.route("/search", methods=[ 'POST'])
def search():
    form = SearchForm()
    factors=Factor.query
    if form.validate_on_submit():
        #Get data from submitted form

       factor.searched = form.searched.data
       #Query the Database
       factors =factors.filter(Factor.content.like('%'+factor.searched+'%'))
       factors=factors.order_by(Factor.title).all()
       return render_template("search.html",
       form=form,
       searched = factor.searched,
       factors=factors)  



@app.route("/")
@app.route("/home")
def home():
   
     factors=Factor.query.all()
     page = request.args.get('page', 1, type=int)
     factors = Factor.query.order_by(Factor.date_posted.desc()).paginate(page=page, per_page=5)

     return render_template('home.html', factors=factors)


@app.route("/about")
def about():
   
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()   
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
      else:
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename) 
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

  output_size = (125, 125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)
  
  return picture_fn 

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/factor/new", methods=['GET', 'POST'])
@login_required
def new_factor():   
    form = factorForm() 
    if form.validate_on_submit():
        factor = Factor(title=form.title.data, content=form.content.data, idf=form.idf.data, theme=form.theme.data,gri=form.gri.data,odd=form.odd.data, author=current_user)
        db.session.add(factor)
        db.session.commit()
        flash('Your factor has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_factor.html', title='New factor', form=form,legend='New factor')
                           
@app.route("/factor/<int:factor_idf>")
def factor(factor_idf):
     
        factors=Factor.query.all()
   
        factor = Factor.query.get_or_404(factor_idf)
        return render_template('factor.html', title=factor.title,factor=factor)
             

@app.route("/factor/<int:factor_idf>/update",methods=['GET', 'POST'])
@login_required
def update_factor(factor_idf):
    factor = Factor.query.get_or_404(factor_idf)
    if factor.author != current_user:
        abort(403)
    form = factorForm()
    if form.validate_on_submit():
        factor.title = form.title.data
        factor.content = form.content.data
        factor.gri = form.gri.data
        factor.odd = form.odd.data
        factor.theme = form.theme.data
        db.session.commit()
        flash('Your factor has been updated!', 'success')
        return redirect(url_for('factor', factor_idf=factor.idf))
    elif request.method == 'GET':
        form.title.data = factor.title
        form.content.data = factor.content
        form.gri.data = factor.gri
        form.odd.data = factor.odd
        form.theme.data = factor.theme



        return render_template('create_factor.html', title='Update factor',
                           form=form, legend='Update factor')

@app.route("/factor/<int:factor_idf>/delete", methods=['POST'])
@login_required
def delete_factor(factor_idf):
    factor= Factor.query.get_or_404(factor_idf)
    print("factor.author", factor.author)
    print("current_user", current_user)
    if factor.author != current_user: 
        abort(403)
    db.session.delete(factor)
    db.session.commit()
    flash('Your factor has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_factors(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    factors = Factor.query.filter_by(author=user)\
        .order_by(Factor.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_factors.html', factors=factors, user=user)






    