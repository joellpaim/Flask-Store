from flask import Blueprint, render_template, url_for, flash
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_models import Order, Item, db, User, Banner
from ..admin.forms import AddItemForm, OrderEditForm, AdminRegisterForm, AddBannerForm
from ..funcs import admin_only
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from PIL import Image


admin = Blueprint("admin", __name__, url_prefix="/admin",
                  static_folder="static", template_folder="templates")


@admin.route('/')
@admin_only
def dashboard():
    orders = Order.query.all()
    return render_template("admin/home.html", orders=orders)


@admin.route('/items')
@admin_only
def items():
    items = Item.query.all()
    return render_template("admin/items.html", items=items)


@admin.route('/users')
@admin_only
def users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@admin.route('/banners')
@admin_only
def banners():
    banners = Banner.query.all()
    return render_template("admin/banners.html", banners=banners)


@admin.route('/add', methods=['POST', 'GET'])
@admin_only
def add():
    form = AddItemForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = form.category.data
        details = form.details.data
        form.image.data.save('app/static/uploads/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/{form.image.data.filename}')
        price_id = form.price_id.data
        item = Item(name=name, price=price, category=category,
                    details=details, image=image, price_id=price_id)
        db.session.add(item)
        db.session.commit()
        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.items'))
    return render_template("admin/add.html", form=form)


@admin.route('/addbanner', methods=['POST', 'GET'])
@admin_only
def addbanner():
    form = AddBannerForm()

    if form.validate_on_submit():

        form.image.data.save('app/static/uploads/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/{form.image.data.filename}')
        new_image = Image.open(f'app/{image}')
        new_image = new_image.resize((1920, 360), Image.ANTIALIAS)
        new_image.save(f'app/{image}')
        banner = Banner(image=image)
        db.session.add(banner)
        db.session.commit()

        flash('adicionado com sucesso!', 'success')
        return redirect(url_for('admin.banners'))
    return render_template("admin/addbanner.html", form=form)


@admin.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
def edit(type, id):
    if type == "item":
        item = Item.query.get(id)
        form = AddItemForm(
            name=item.name,
            price=item.price,
            category=item.category,
            details=item.details,
            image=item.image,
            price_id=item.price_id,
        )
        if form.validate_on_submit():
            item.name = form.name.data
            item.price = form.price.data
            item.category = form.category.data
            item.details = form.details.data
            item.price_id = form.price_id.data
            form.image.data.save('app/static/uploads/' +
                                 form.image.data.filename)
            item.image = url_for(
                'static', filename=f'uploads/{form.image.data.filename}')
            db.session.commit()
            return redirect(url_for('admin.items'))
    elif type == "order":
        order = Order.query.get(id)
        form = OrderEditForm(status=order.status)
        if form.validate_on_submit():
            order.status = form.status.data
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
    elif type == "user":
        user = User.query.get(id)
        form = AdminRegisterForm(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=user.password,
            admin=user.admin,
        )
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.password = form.password.data
            user.admin = form.admin.data

            db.session.commit()
            return redirect(url_for('admin.users'))
    return render_template('admin/add.html', form=form)


@admin.route('/delete/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
def delete(type, id):
    if type == "item":
        to_delete = Item.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for('admin.items'))

    elif type == "user":
        to_delete = User.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for('admin.users'))

    elif type == "banner":
        to_delete = Banner.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.image} deletado com sucesso!', 'error')
        return redirect(url_for('admin.banners'))
    return render_template('admin/home.html')


@admin.route('/cleartable/<string:type>', methods=['POST', 'GET'])
@admin_only
def cleartable(type):
    if type == "item":
        db.session.execute("delete from items")
        db.session.commit()
        flash('deletado com sucesso!', 'error')
        return redirect(url_for('admin.items'))

    elif type == "user":
        db.session.execute("delete from users")
        db.session.commit()
        flash('deletado com sucesso!', 'error')
        return redirect(url_for('admin.users'))

    elif type == "banner":
        try:
            db.session.execute("delete from banners")
            db.session.commit()
            flash('deletado com sucesso!', 'error')
        except Exception as e:
            print(f'\n\nErro: {e}\n\n')
        return redirect(url_for('admin.banners'))
    return render_template('admin/home.html')


@admin.route("/adminregister", methods=['POST', 'GET'])
@admin_only
def adminregister():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminRegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(
                f"O Usuário com email {user.email} já existe!!<br> <a href={url_for('login')}>Entrar agora</a>", "error")
            return redirect(url_for('adminregister'))
        new_user = User(name=form.name.data,
                        email=form.email.data,
                        password=generate_password_hash(
                            form.password.data,
                            method='pbkdf2:sha256',
                            salt_length=8),
                        phone=form.phone.data,
                        admin=form.admin.data)

        db.session.add(new_user)
        db.session.commit()
        # send_confirmation_email(new_user.email)
        flash('Administrador registrado com sucesso! Você deve logar agora.', 'success')
        return redirect(url_for('login'))
    return render_template("admin/register.html", form=form)
