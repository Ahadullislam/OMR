from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
from process_omr import process_omr
from generate_results import generate_results, save_results_to_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_customization(data):
    with open('customization.json', 'w') as f:
        json.dump(data, f)

def get_customization():
    try:
        with open('customization.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/customize', methods=['POST'])
def customize():
    num_questions = int(request.form['num_questions'])
    num_choices = int(request.form['num_choices'])
    answer_key = [x.strip().upper() for x in request.form['answer_key'].split(',')]
    
    if len(answer_key) != num_questions:
        return "Error: Number of answers must match the number of questions.", 400
    
    customization = {
        'num_questions': num_questions,
        'num_choices': num_choices,
        'answer_key': answer_key
    }
    save_customization(customization)
    return redirect(url_for('upload'))

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return redirect(url_for('upload'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('upload'))
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get settings
        customization = get_customization()
        if not customization:
            return redirect(url_for('home'))
        
        # Process OMR
        marked_answers = process_omr(
            filepath,
            customization['num_questions'],
            customization['num_choices']
        )
        if marked_answers is None:
            return "Error: Could not detect the correct number of bubbles. Check the image and settings.", 500
        
        # Generate results
        results = generate_results(marked_answers, customization['answer_key'])
        
        # Save PDF
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results.pdf')
        save_results_to_pdf(results, pdf_path)
        
        return render_template('results.html',
                             results=results.to_dict('records'),
                             score=results['Score'].iloc[0],
                             total=len(results))
    
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)