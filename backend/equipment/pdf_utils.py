"""
PDF report generation utilities for equipment datasets using ReportLab.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak
from django.utils import timezone
from .models import Dataset, Equipment


def generate_dataset_report_pdf(dataset):
    """
    Generate a PDF report for a given dataset.
    
    Args:
        dataset: Dataset model instance
        
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    normal_style = styles['Normal']
    
    # Build the story (PDF content)
    story = []
    
    # Title
    story.append(Paragraph("Chemical Equipment Dataset Report", title_style))
    story.append(Spacer(1, 20))
    
    # Dataset Information Section
    story.append(Paragraph("Dataset Information", heading_style))
    
    dataset_info = [
        ['Dataset Name:', dataset.name],
        ['Upload Date:', dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if dataset.uploaded_at else 'N/A'],
        ['Original Filename:', dataset.original_filename or 'N/A'],
        ['Uploaded By:', dataset.uploaded_by.username if dataset.uploaded_by else 'N/A']
    ]
    
    info_table = Table(dataset_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Summary Section
    story.append(Paragraph("Summary Statistics", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', str(dataset.total_count or 0)],
        ['Average Flowrate', f"{dataset.avg_flowrate:.2f}" if dataset.avg_flowrate is not None else 'N/A'],
        ['Average Pressure', f"{dataset.avg_pressure:.2f}" if dataset.avg_pressure is not None else 'N/A'],
        ['Average Temperature', f"{dataset.avg_temperature:.2f}" if dataset.avg_temperature is not None else 'N/A']
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Type Distribution Section
    if dataset.type_distribution:
        story.append(Paragraph("Equipment Type Distribution", heading_style))
        
        type_data = [['Equipment Type', 'Count']]
        for equipment_type, count in dataset.type_distribution.items():
            type_data.append([str(equipment_type), str(count)])
        
        type_table = Table(type_data, colWidths=[3*inch, 2*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(type_table)
        story.append(Spacer(1, 20))
    
    # Equipment Records Section (First 10 records)
    equipment_records = Equipment.objects.filter(dataset=dataset).order_by('id')[:10]
    
    if equipment_records.exists():
        story.append(Paragraph("Sample Equipment Records (First 10)", heading_style))
        
        records_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        
        for equipment in equipment_records:
            records_data.append([
                equipment.name or 'N/A',
                equipment.type or 'N/A',
                f"{equipment.flowrate:.2f}" if equipment.flowrate is not None else 'N/A',
                f"{equipment.pressure:.2f}" if equipment.pressure is not None else 'N/A',
                f"{equipment.temperature:.2f}" if equipment.temperature is not None else 'N/A'
            ])
        
        records_table = Table(records_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        records_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(records_table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
        normal_style
    ))
    
    # Build PDF
    doc.build(story)
    
    # Move buffer position to beginning
    buffer.seek(0)
    
    return buffer


def generate_pdf_response(dataset):
    """
    Generate PDF and return Django HttpResponse.
    
    Args:
        dataset: Dataset model instance
        
    Returns:
        HttpResponse: PDF file response
    """
    buffer = generate_dataset_report_pdf(dataset)
    
    from django.http import HttpResponse
    
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"dataset_{dataset.id}_report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
