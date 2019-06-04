from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired
from app import songlist_pairs, raw_songdata

class SearchForm(FlaskForm):
    filters = (
    ("verified-score", "Verified, Score"),
    ("verified-difficulty", "Verified, Single Difficulty"),
    ("unverified-score", "Unverified, Score"),
    ("unverified-difficulty", "Unverified, Difficulty"))
    song = SelectField('Song', coerce=str, choices=[tuple(map(lambda x: x.decode('utf-8'), tup)) for tup in songlist_pairs])
    length = SelectField('Length', coerce=str, choices=(('Arcade', 'Arcade'), ('Full Song', 'Full Song'), ('Short Cut', 'Short Cut')), validators=[DataRequired()])
    filters = SelectField('Filter', coerce=str, choices=filters)
    submit = SubmitField('Search')

class TournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired()])
    description = StringField('Description')
    bracketlink = StringField('Bracket Link (Challonge or other)')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit = SubmitField('Submit')
    contactinfo = StringField('Contact Information')
    skill_lvl = SelectField('Skill Level', coerce=str, choices=(('Beginner', 'Beginner'),
                                                                ('Intermediate', 'Intermediate'),
                                                                ('Advanced', 'Advanced')),
                                                                validators=[DataRequired()])

class TournamentEditForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired()])
    description = StringField('Description')
    bracketlink = StringField('Bracket Link (Challonge or other)')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit = SubmitField('Submit')
    contactinfo = StringField('Contact Information')
    skill_lvl = SelectField('Skill Level', coerce=str, choices=(('Beginner', 'Beginner'),
                                                                ('Intermediate', 'Intermediate'),
                                                                ('Advanced', 'Advanced')),
                                                                validators=[DataRequired()])
