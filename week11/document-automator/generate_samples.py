"""
Script to generate sample PDF documents required for the assignment:
- documents/input_article.pdf (2 pages)
- documents/dummy_doc1.pdf (1 page)
- documents/dummy_doc2.pdf (1 page)
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_sample_docs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base_dir, "documents")
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Create input_article.pdf
    input_article_path = os.path.join(docs_dir, "input_article.pdf")
    c = canvas.Canvas(input_article_path, pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, "Introduction to Automation")
    
    c.setFont("Helvetica", 11)
    text_p1_1 = (
        "Automation is the creation and application of technology to produce and deliver "
        "goods and services with minimal human intervention. The implementation of automation "
        "technologies, techniques, and processes improves the efficiency, reliability, and speed "
        "of many tasks that were previously performed manually."
    )
    text_p1_2 = "This leads to increased productivity, reduced costs, and improved quality."
    
    y = 680
    # Simple line wrapper
    words = text_p1_1.split()
    line = []
    for word in words:
        line.append(word)
        if len(" ".join(line)) > 75:
            c.drawString(72, y, " ".join(line[:-1]))
            line = [word]
            y -= 18
    if line:
        c.drawString(72, y, " ".join(line))
        y -= 25
        
    c.drawString(72, y, text_p1_2)
    c.showPage()  # Move to Page 2
    
    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 720, "Benefits of Automation")
    
    c.setFont("Helvetica", 11)
    benefits = [
        "1. Increased Efficiency: Tasks are completed faster and with higher throughput.",
        "2. Cost Reduction: Lower labor costs and reduced waste.",
        "3. Improved Accuracy: Minimizes human error.",
        "4. Enhanced Safety: Dangerous tasks can be automated.",
        "5. Greater Consistency: Uniform quality in output."
    ]
    
    y = 680
    for b in benefits:
        c.drawString(72, y, b)
        y -= 22
        
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, "Conclusion")
    y -= 25
    c.setFont("Helvetica", 11)
    conc = "Automation is transforming industries globally. Embracing these technologies is crucial for future competitiveness."
    c.drawString(72, y, conc)
    c.showPage()
    c.save()
    print(f"Generated {input_article_path}")

    # 2. Create dummy_doc1.pdf
    dummy1_path = os.path.join(docs_dir, "dummy_doc1.pdf")
    c1 = canvas.Canvas(dummy1_path, pagesize=letter)
    c1.setFont("Helvetica-Bold", 14)
    c1.drawString(72, 700, "Dummy Document 1 - PDF Merging Test")
    c1.setFont("Helvetica", 11)
    c1.drawString(72, 670, "This is the content of dummy document 1.")
    c1.showPage()
    c1.save()
    print(f"Generated {dummy1_path}")

    # 3. Create dummy_doc2.pdf
    dummy2_path = os.path.join(docs_dir, "dummy_doc2.pdf")
    c2 = canvas.Canvas(dummy2_path, pagesize=letter)
    c2.setFont("Helvetica-Bold", 14)
    c2.drawString(72, 700, "Dummy Document 2 - PDF Merging Test")
    c2.setFont("Helvetica", 11)
    c2.drawString(72, 670, "This is the content of dummy document 2.")
    c2.showPage()
    c2.save()
    print(f"Generated {dummy2_path}")

if __name__ == "__main__":
    create_sample_docs()
