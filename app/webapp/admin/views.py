# Views for admin blueprint
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import admin
from .forms import AlycForm
from ...extensions import db
from ..models import Share,Alyc,Boleto


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)


# Alyc Views


@admin.route('/alycs', methods=['GET', 'POST'])
@login_required
def list_alycs():
    """
    List all alycs
    """
    check_admin()

    alycs = Alyc.query.all()

    return render_template('admin/alycs/alycs.html',
                           alycs=alycs, title="Alycs")


@admin.route('/alycs/add', methods=['GET', 'POST'])
@login_required
def add_alyc():
    """
    Add a alycs to the database
    """
    check_admin()

    add_alyc = True

    form = AlycForm()
    if form.validate_on_submit():
        alyc = Alyc(name=form.name.data,
                                contraparte=form.contraparte.data,
                                commitent=form.commitent.data,
                                employee_id = form.employee.data.id)
        try:
            # add alyc to the database
            db.session.add(alyc)
            db.session.commit()
            flash('You have successfully added a new alyc.')
        except Exception as e:
            # in case alyc name already exists
            flash(str(e))

        # redirect to alycs page
        return redirect(url_for('admin.list_alycs'))

    # load alyc template
    return render_template('admin/alycs/alyc.html', action="Add",
                           add_alyc=add_alyc, form=form,
                           title="Add Alyc")


@admin.route('/alycs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_alyc(id):
    """
    Edit a alycs
    """
    check_admin()

    add_alyc = False

    alyc = Alyc.query.get_or_404(id)
    form = AlycForm(obj=alyc)
    if form.validate_on_submit():
        alyc.name = form.name.data
        alyc.contraparte = form.contraparte.data
        alyc.commitent = form.commitent.data
        db.session.commit()
        flash('You have successfully edited the alyc.')

        # redirect to the alycs page
        return redirect(url_for('admin.list_alycs'))

    form.contraparte.data = alyc.contraparte
    form.commitent.data = alyc.commitent
    form.name.data = alyc.name
    return render_template('admin/alycs/alyc.html', action="Edit",
                           add_alyc=add_alyc, form=form,
                           alyc=alyc, title="Edit alyc")


@admin.route('/alycs/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_alyc(id):
    """
    Delete a alyc from the database
    """
    check_admin()

    alyc = Alyc.query.get_or_404(id)
    db.session.delete(alyc)
    db.session.commit()
    flash('You have successfully deleted the alyc.')

    # redirect to the alycs page
    return redirect(url_for('admin.list_alycs'))

    return render_template(title="Delete Alyc")
