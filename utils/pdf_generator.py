from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime


def generate_books_pdf(books, filename="books_report.pdf"):

    if not books:
        return None

    output_dir = "temp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filepath = os.path.join(output_dir, filename)

    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.darkgreen
    )

    # Title
    title = Paragraph("📚 Kitoblar Ro'yxati", title_style)
    elements.append(title)

    # Date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_paragraph = Paragraph(f"Sana: {date_str}", styles['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 20))

    # Summary
    total_books = len(books)
    summary_text = f"Jami kitoblar soni: {total_books}"
    summary = Paragraph(summary_text, header_style)
    elements.append(summary)
    elements.append(Spacer(1, 20))

    # Create table data
    table_data = []

    # Table header
    header_row = [
        Paragraph("<b>#</b>", styles['Normal']),
        Paragraph("<b>Sarlavha</b>", styles['Normal']),
        Paragraph("<b>Muallif</b>", styles['Normal']),
        Paragraph("<b>Narx</b>", styles['Normal']),
        Paragraph("<b>Janr</b>", styles['Normal']),
        Paragraph("<b>Miqdor</b>", styles['Normal'])
    ]
    table_data.append(header_row)

    # Table rows
    for i, book in enumerate(books, 1):
        row = [
            str(i),
            book.get('title', 'Noma\'lum'),
            book.get('author', 'Noma\'lum'),
            f"{book.get('price', 0)} so'm",
            book.get('genre', 'Noma\'lum'),
            str(book.get('quantity', 0))
        ]
        table_data.append(row)

    # Create table
    table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1*inch, 1.2*inch, 0.8*inch])

    # Table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Center align the # column
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Left align the title column
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Left align the author column
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Right align the price column
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Center align the genre column
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Center align the quantity column
    ])

    table.setStyle(table_style)
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 30))
    footer_text = f"PDF {datetime.now().strftime('%Y-%m-%d %H:%M')} da yaratildi"
    footer = Paragraph(footer_text, styles['Italic'])
    elements.append(footer)

    # Build PDF
    try:
        doc.build(elements)
        return filepath
    except Exception as e:
        print(f"PDF yaratishda xatolik: {e}")
        return None


def generate_book_details_pdf(book, filename="book_details.pdf"):
    """
    Generate PDF for single book details

    Args:
        book (dict): Book dictionary
        filename (str): Output filename

    Returns:
        str: Path to generated PDF file
    """
    if not book:
        return None

    # Create output directory if it doesn't exist
    output_dir = "temp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filepath = os.path.join(output_dir, filename)

    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    # Title
    title = Paragraph(f"📖 {book.get('title', 'Kitob')}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Book details
    details = []

    if book.get('author'):
        details.append(f"✍️ Muallif: {book['author']}")
    if book.get('price'):
        details.append(f"💰 Narx: {book['price']} so'm")
    if book.get('genre'):
        details.append(f"🏷️ Janr: {book['genre']}")
    if book.get('quantity') is not None:
        details.append(f"📦 Miqdor: {book['quantity']} dona")
    if book.get('description'):
        details.append(f"📝 Tavsif: {book['description']}")

    details_text = "\n".join(details)
    details_paragraph = Paragraph(details_text, styles['Normal'])
    elements.append(details_paragraph)

    # Footer
    elements.append(Spacer(1, 30))
    footer_text = f"PDF {datetime.now().strftime('%Y-%m-%d %H:%M')} da yaratildi"
    footer = Paragraph(footer_text, styles['Italic'])
    elements.append(footer)

    # Build PDF
    try:
        doc.build(elements)
        return filepath
    except Exception as e:
        print(f"PDF yaratishda xatolik: {e}")
        return None