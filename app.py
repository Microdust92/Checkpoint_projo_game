from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_reviews.db'



@app.route('/Game_Review', methods=['GET', 'POST'])
def game_review():
    if request.method == 'POST':
        # Handle form submission
        title = request.form['title']
        review = request.form['review']
        rating = request.form['rating']
        # Save the review to the database
        return redirect(url_for('game_review'))
    return render_template('game_review.html')

@app.route('/Game_play', methods=['GET', 'POST'])
def game_play():
    game_module = __import__('game_Module')
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = game_module.process_input(user_input)
        return render_template('game_play.html', response=response)
