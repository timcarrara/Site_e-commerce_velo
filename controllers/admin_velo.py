#! /usr/bin/python
# -*- coding:utf-8 -*-
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
# from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_velo = Blueprint('admin_velo', __name__, template_folder='templates')


@admin_velo.route('/admin/velo/show')
def show_velo():
    mycursor = get_db().cursor()
    sql = '''SELECT velo.id_velo, velo.nom_velo, velo.prix_velo, velo.image, velo.type_velo_id, type_velo.libelle_type_velo, SUM(stock) AS stock, MIN(stock) AS min_stock,
             COUNT(id_declinaison_velo) AS nb_declinaisons
             FROM velo
             LEFT JOIN declinaison_velo ON velo.id_velo = declinaison_velo.velo_id
             LEFT JOIN type_velo ON velo.type_velo_id = type_velo.id_type_velo
             GROUP BY id_velo'''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    return render_template('admin/velo/show_velo.html', velos=velos)


@admin_velo.route('/admin/velo/add', methods=['GET'])
def add_velo():
    mycursor = get_db().cursor()
    sql = "SELECT * FROM velo"
    mycursor.execute(sql)
    sql = "SELECT id_type_velo, libelle_type_velo FROM type_velo"
    mycursor.execute(sql)
    type_velo = mycursor.fetchall()
    sql = "SELECT id_taille, libelle_taille FROM taille"
    mycursor.execute(sql)
    tailles = mycursor.fetchall()
    return render_template('admin/velo/add_velo.html', types_velo=type_velo, tailles=tailles)
    # ,couleurs=colors


@admin_velo.route('/admin/velo/add', methods=['POST'])
def valid_add_velo():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    type_velo_id = request.form.get('type_velo_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename = None

    sql = '''INSERT INTO velo (id_velo, nom_velo, prix_velo, type_velo_id, description, image) VALUES (NULL, %s, %s, %s, %s, %s)'''

    tuple_add = (nom, prix, type_velo_id, description, filename,)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'velo ajouté , nom: ', nom, ' - type_velo: ', type_velo_id, ' - prix: ', prix, ' - image: ', image)
    message = u'velo ajouté , nom: ' + nom + ' - type_velo: ' + type_velo_id + ' - prix: ' + prix + ' - image: ' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/delete', methods=['GET'])
def delete_velo():
    id_velo = request.args.get('id_velo')
    mycursor = get_db().cursor()
    sql = '''SELECT COUNT(id_declinaison_velo)
             FROM declinaison_velo
             WHERE velo_id = %s
             GROUP BY velo_id'''
    mycursor.execute(sql, (id_velo,))
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison:
        message = u'il y a des declinaisons dans ce velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = '''SELECT image FROM velo
                 WHERE id_velo = %s'''
        mycursor.execute(sql, (id_velo,))
        velo = mycursor.fetchone()
        print(velo)
        image = velo['image']

        sql = '''DELETE FROM velo 
                 WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        get_db().commit()
        if image is not None:
            os.remove('static/images/' + image)

        print("un velo supprimé, id :", id_velo)
        message = u'un velo supprimé, id : ' + id_velo
        flash(message, 'alert-success')

    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/edit', methods=['GET'])
def edit_velo():
    id_velo = request.args.get('id_velo')
    mycursor = get_db().cursor()
    sql = '''SELECT id_velo, nom_velo AS nom, prix_velo AS prix, type_velo_id, description, image FROM velo
             WHERE id_velo = %s;'''
    mycursor.execute(sql, id_velo)
    velo = mycursor.fetchone()
    print(velo)
    sql = '''SELECT * FROM type_velo'''
    mycursor.execute(sql)
    types_velo = mycursor.fetchall()
    sql = '''SELECT * FROM declinaison_velo
             JOIN couleur ON declinaison_velo.couleur_id = couleur.id_couleur
             JOIN taille ON declinaison_velo.taille_id = taille.id_taille
             WHERE velo_id = %s'''
    mycursor.execute(sql, id_velo)
    declinaisons_velo = mycursor.fetchall()

    return render_template('admin/velo/edit_velo.html', velo=velo, types_velo=types_velo,
                           declinaisons_velo=declinaisons_velo
                           )


@admin_velo.route('/admin/velo/edit', methods=['POST'])
def valid_edit_velo():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    type_velo_id = request.form.get('type_velo_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')
    id_velo = request.form.get('id_velo')
    sql = '''SELECT image FROM velo WHERE id_velo=%s;'''
    mycursor.execute(sql, id_velo)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename
    sql = '''UPDATE velo SET nom_velo = %s, prix_velo = %s, type_velo_id = %s, description = %s, image = %s 
             WHERE id_velo = %s;'''
    mycursor.execute(sql, (nom, prix, type_velo_id, description, image_nom, id_velo))
    print(nom, prix, type_velo_id, image_nom, id_velo)
    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'velo modifié , nom: ' + nom + ' - type_velo: ' + type_velo_id + ' - prix: ' + prix + ' - image: ' + image_nom
    flash(message, 'alert-success')
    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    velo = []
    commentaires = {}
    return render_template('admin/velo/show_avis.html', velo=velo, commentaires=commentaires)


@admin_velo.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    velo_id = request.form.get('idVelo', None)
    userId = request.form.get('idUser', None)
    return admin_avis(velo_id)
