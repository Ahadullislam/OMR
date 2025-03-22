import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_results(marked_answers, answer_key):
    score = sum(1 for m, c in zip(marked_answers, answer_key) if m == c)
    results = pd.DataFrame({
        'Question': list(range(1, len(answer_key) + 1)),
        'Marked': marked_answers,
        'Correct': answer_key,
        'Score': [score]*len(answer_key)
    })
    return results

def save_results_to_pdf(results, filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("OMR Results Report", styles['Title']))
    
    data = [results.columns.tolist()] + results.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Paragraph(f"Total Score: {results['Score'].iloc[0]}/{len(results)}", styles['Heading2']))
    doc.build(elements)