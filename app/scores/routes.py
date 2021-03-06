from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint, current_app)
from flask_login import current_user, login_required
from app import db, logging, raw_songdata
from app.models import Post, WeeklyPost, User
from app.users.utils import update_user_sp
from app.scores.forms import ScoreForm, WeeklyForm
from app.scores.utils import *
import os
import json
from weekly import get_current_weekly, randomize_weekly
from calc_performance import calc_performance

scores = Blueprint('scores', __name__)

@scores.context_processor
def add_songdata():
    return dict(songdata=raw_songdata)

@scores.route('/post/new_score', methods=["GET", "POST"])
@login_required
def new_score():
    form = ScoreForm()
    current_app.logger.info(request.form)
    if form.validate_on_submit():
        current_app.logger.info("Form validated.")
        difficulty = request.form.get('diffDrop')
        try:
            file = request.files['file']
        except:
            picture_file = "None"
            file = None
            flash('No file uploaded', 'info')
        if file.filename != '':
            if file and allowed_file(file.filename):
                picture_file = save_picture(file)
                flash('File uploaded successfully!', 'success')
            elif file and not allowed_file(file.filename):
                picture_file = "None"
                flash('You can\'t upload that!', 'error')
        else:
            picture_file = "None"
        current_app.logger.info("Converting to post type...")
        post = Post(
            song = form.song.data, 
            song_id = int(songname_to_id(form.song.data), 16) if songname_to_id(form.song.data) != '' else None, 
            score = form.score.data,
            exscore = calc_exscore(form.perfect.data, form.great.data, form.good.data, form.bad.data, form.miss.data),
            lettergrade = form.lettergrade.data, 
            type = get_difftype(difficulty),
            difficulty = difficulty, 
            difficultynum = get_diffnum(difficulty),
            platform = form.platform.data, 
            stagepass = form.stagepass.data, 
            perfect = form.perfect.data,
            great = form.great.data,
            good = form.good.data,
            bad = form.bad.data,
            miss = form.miss.data,
            maxcombo = form.maxcombo.data,
            modifiers = mods_to_int(request.form.getlist('modifiers'), form.judgement.data),
            noteskin = form.noteskin.data,
            rushspeed = form.rushspeed.data if form.rushspeed.data != None else 1.0,
            ranked = form.ranked.data, 
            length = raw_songdata[form.song.data]['length'], 
            acsubmit = 'False',
            author = current_user, 
            image_file = picture_file
        )
        post.sp = calc_performance(post.song, post.difficulty, post.difficultynum, post.perfect, post.great, post.good, post.bad, post.miss, int_to_judge(post.modifiers), post.rushspeed, post.stagepass == "True")
        update_user_sp(current_user)
        current_app.logger.info("Converted.")
        db.session.add(post)
        current_app.logger.info("Committing to database...")
        db.session.commit()
        flash('Score has been submitted!', 'success')
        return redirect(url_for('main.home'))
    return render_template("new_score.html", title="New Score", form=form, songdata=raw_songdata)

@scores.route('/post/<int:score_id>')
def score(score_id):
    bluegrades = ['a', 'b', 'c', 'd']
    goldgrades = ['s', 'ss', 'sss']
    redgrades = ['f']
    score = Post.query.get_or_404(score_id)
    return render_template('score.html', score=score, songdata=raw_songdata, bluegrades=bluegrades, goldgrades=goldgrades, redgrades=redgrades, int_to_mods=int_to_mods, modlist_to_modstr=modlist_to_modstr, int_to_noteskin=int_to_noteskin)

@scores.route('/post/<int:score_id>/delete', methods=["POST"])
def delete_score(score_id):
    score = Post.query.get_or_404(score_id)
    if score.author == current_user or current_user.id == 1:
        if score.image_file != "None":
            try:
                os.remove(os.path.join(current_app.root_path, 'static/score_screenshots', score.image_file))
            except:
                flash('Score screenshot couldn\'t be found.', 'info')
        db.session.delete(score)
        db.session.commit()
        update_user_sp(current_user)
        flash('Your score has been deleted!', 'success')
        return redirect(url_for('main.home'))
    elif score.author != current_user:
        abort(403)

@scores.route('/challenge/weekly/<int:score_id>/delete', methods=["POST"])
def delete_weekly(score_id):
    score = WeeklyPost.query.get_or_404(score_id)
    if score.author != current_user:
        abort(403)
    if score.image_file != "None":
        os.remove(os.path.join(current_app.root_path, 'static/score_screenshots', score.image_file))
    db.session.delete(score)
    db.session.commit()
    flash('Your score has been deleted!', 'success')
    return redirect(url_for('main.home'))

@scores.route('/challenge/weekly', methods=["GET", "POST"])
@login_required
def weekly():
    current_weekly = get_current_weekly()
    form = WeeklyForm()
    if form.validate_on_submit():
        try:
            file = request.files['file']
        except:
            flash('Score not submitted. Verification screenshot required.')
            return redirect(url_for('main.home'))
        if file != None:
            if file.filename == '':
                flash('Score not submitted. Verification screenshot required.')
                return redirect(url_for('main.home'))
            if file and allowed_file(file.filename):
                picture_file = save_picture(file)
                flash('File uploaded successfully!', 'success')
                post = WeeklyPost(song = current_weekly[0], score = form.score.data, lettergrade = form.lettergrade.data, type=current_weekly[1], difficulty = form.difficulty.data, platform = form.platform.data, stagepass = form.stagepass.data, ranked = form.ranked.data, author = current_user, image_file = picture_file)
                db.session.add(post)
                db.session.commit()
            elif file and not allowed_file(file.filename):
                    flash('Score not submitted. Verification screenshot required.')
                    return redirect(url_for('main.home'))
        flash('Score has been submitted!', 'success')
        return redirect(url_for('scores.weekly'))
    ldb = WeeklyPost.query.order_by(WeeklyPost.score.desc()).all()
    return render_template('weekly.html', current_weekly=current_weekly, form=form, ldb=ldb)

@scores.route('/challenge/weekly/<int:score_id>')
def weeklyscore(score_id):
    bluegrades = ['a', 'b', 'c', 'd']
    goldgrades = ['s', 'ss', 'sss']
    redgrades = ['f']
    score = WeeklyPost.query.get_or_404(score_id)
    return render_template('weeklyscore.html', score=score, bluegrades=bluegrades, goldgrades=goldgrades, redgrades=redgrades)

@scores.route('/leaderboard/main')
def main_ldb():
    users = User.query.filter(User.sp != 0).order_by(User.sp.desc()).all()
    ldbtype = "Main"
    return render_template('ldbsp.html', users=users, ldbtype=ldbtype)

@scores.route('/leaderboard/total')
def total_ldb():
    users = User.query.all()
    scores = {}
    ldbtype = "Total Score"
    for user in users:
        usertotal = []
        allscores = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
        for score in allscores:
            usertotal.append(score.score)
        total = sum(usertotal)
        if total != 0:
            scores[user.username] = total
        scores = {k:v for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)}
    return render_template('ldb.html', scores=scores, ldbtype=ldbtype)

@scores.route('/leaderboard/singles')
def singles_ldb():
    users = User.query.all()
    scores = {}
    ldbtype = "Singles Total"
    for user in users:
        usertotal = []
        allscores = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
        for score in allscores:
            if score.type.startswith('s'):
                usertotal.append(score.score)
        total = sum(usertotal)
        if total != 0:
            scores[user.username] = total
        scores = {k:v for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)}
    return render_template('ldb.html', scores=scores, ldbtype=ldbtype)

@scores.route('/leaderboard/doubles')
def doubles_ldb():
    users = User.query.all()
    scores = {}
    ldbtype = "Doubles Total"
    for user in users:
        usertotal = []
        allscores = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
        for score in allscores:
            if score.type.startswith('d'):
                usertotal.append(score.score)
        total = sum(usertotal)
        if total != 0:
            scores[user.username] = total
        scores = {k:v for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)}
    return render_template('ldb.html', scores=scores, ldbtype=ldbtype)

@scores.route('/completion/<string:user>')
@login_required
def completion(user):
    completion = return_completion(user, "singles")
    return render_template('completion.html', completion=completion)
