from typing import List
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def build_project_pdf(project, boards) -> BytesIO:
    """
    Builds a PDF for the given project and list of boards (with columns and tasks).
    Returns a BytesIO containing the generated PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=1
    )

    board_style = ParagraphStyle(
        'BoardTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#2c3e50')
    )

    column_style = ParagraphStyle(
        'ColumnTitle',
        parent=styles['Heading3'],
        fontSize=13,
        spaceAfter=8,
        spaceBefore=10,
        textColor=colors.HexColor('#34495e')
    )

    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d')
    )

    elements = []

    elements.append(Paragraph(f"{project.name}", title_style))
    if project.description:
        elements.append(Paragraph(f"Description: {project.description}", description_style))
    elements.append(Spacer(1, 20))

    priority_colors = {
        'high': colors.HexColor("#d68d85"),
        'medium': colors.HexColor("#f3d19a"),
        'low': colors.HexColor("#78aa8d"),
    }

    for board in boards:
        elements.append(Paragraph(f"Board: {board.name}", board_style))
        if getattr(board, 'description', None):
            elements.append(Paragraph(board.description, description_style))

        sorted_columns = sorted(board.columns, key=lambda c: c.position)
        for column in sorted_columns:
            elements.append(Paragraph(f"Column: {column.name}", column_style))
            sorted_tasks = sorted(column.tasks, key=lambda t: t.position)
            if sorted_tasks:
                table_data = [
                    [
                        Paragraph('<b>Name</b>', styles['Normal']),
                        Paragraph('<b>Priority</b>', styles['Normal']),
                        Paragraph('<b>Due Date</b>', styles['Normal']),
                        Paragraph('<b>Description</b>', styles['Normal'])
                    ]
                ]

                for task in sorted_tasks:
                    due_date_str = task.due_date.strftime('%Y-%m-%d') if getattr(task, 'due_date', None) else '-'
                    description_text = task.description if getattr(task, 'description', None) else '-'
                    if len(description_text) > 100:
                        description_text = description_text[:100] + '...'
                    table_data.append([
                        Paragraph(task.title, styles['Normal']),
                        Paragraph(task.priority.capitalize(), styles['Normal']),
                        Paragraph(due_date_str, styles['Normal']),
                        Paragraph(description_text, styles['Normal'])
                    ])

                col_widths = [4*cm, 2.5*cm, 2.5*cm, 8*cm]
                table = Table(table_data, colWidths=col_widths)
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ])

                for i, task in enumerate(sorted_tasks, start=1):
                    # normalize priority: strip whitespace and lowercase before lookup
                    raw_priority = (getattr(task, 'priority', '') or '')
                    normalized = raw_priority.strip().lower()
                    priority_color = priority_colors.get(normalized, colors.HexColor('#95a5a6'))

                    # set cell background for priority column
                    table_style.add('BACKGROUND', (1, i), (1, i), priority_color)

                    # choose contrasting text color based on luminance
                    try:
                        r, g, b = priority_color.red, priority_color.green, priority_color.blue
                        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                    except Exception:
                        luminance = 0.0

                    text_color = colors.white if luminance < 0.6 else colors.black
                    table_style.add('TEXTCOLOR', (1, i), (1, i), text_color)

                table.setStyle(table_style)
                elements.append(table)
            else:
                elements.append(Paragraph("<i>No tasks in this column</i>", description_style))
            elements.append(Spacer(1, 10))
        elements.append(Spacer(1, 15))

    if not boards:
        elements.append(Paragraph("<i>Project contains no boards</i>", description_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
