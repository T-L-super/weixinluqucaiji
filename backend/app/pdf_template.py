"""
PDF 报告模板生成模块（2026-05-08 修复中文乱码）
使用 reportlab CID 字体支持中文，无需外部字体文件
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io

# 注册 CID 中文字体
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT_CN = 'STSong-Light'


def _safe_str(val, default='-'):
    if val is None:
        return default
    s = str(val).strip()
    return s if s else default


def create_pdf_report(records, filters=None):
    """
    创建 PDF 录取报告（修复中文乱码 + 支持自定义字段）
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # === 自定义样式（全部使用 CID 中文字体）===
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=FONT_CN,
        leading=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName=FONT_CN,
        leading=16
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=10,
        spaceBefore=8,
        fontName=FONT_CN,
        leading=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName=FONT_CN,
        textColor=colors.HexColor('#333333'),
        leading=15
    )
    
    # === 标题 ===
    elements.append(Paragraph("贝优教育 - 大学录取报告", title_style))
    
    report_date = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    elements.append(Paragraph(f"报告生成时间：{report_date}", subtitle_style))
    
    # 筛选条件
    if filters:
        filter_parts = []
        if filters.get('country'):
            filter_parts.append(f"国家：{filters['country']}")
        if filters.get('university'):
            filter_parts.append(f"大学：{filters['university']}")
        if filters.get('major'):
            filter_parts.append(f"专业：{filters['major']}")
        if filters.get('year_start'):
            y_end = filters.get('year_end', '至今')
            filter_parts.append(f"年份：{filters['year_start']} ~ {y_end}")
        
        if filter_parts:
            elements.append(Paragraph("筛选条件：" + " | ".join(filter_parts), normal_style))
            elements.append(Spacer(1, 0.2*cm))
    
    elements.append(Spacer(1, 0.3*cm))
    
    # === 统计信息 ===
    stats = calculate_statistics(records)
    elements.append(Paragraph("统计摘要", heading_style))
    
    stats_data = [
        ['总录取数', '已验证', '待验证', '获奖学金'],
        [str(stats['total']), str(stats['verified']), str(stats['pending']), str(stats['with_scholarship'])]
    ]
    
    stats_table = Table(stats_data, colWidths=[3.5*cm]*4)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_CN),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e8f0fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # === 录取详情表格（支持自定义字段）===
    elements.append(Paragraph("录取详情", heading_style))
    
    # 字段定义
    FIELD_DEFINITIONS = {
        'student_name_cn': {'label': '学生姓名', 'width': 2.5, 'transform': lambda v: _safe_str(v)},
        'student_name_en': {'label': '英文名', 'width': 2.5, 'transform': lambda v: _safe_str(v)},
        'data_source': {'label': '数据来源', 'width': 2.5, 'transform': lambda v: _safe_str(v)},
        'country': {'label': '国家', 'width': 2, 'transform': lambda v: _safe_str(v)},
        'university_cn': {'label': '录取大学', 'width': 3.5, 'transform': lambda v: _safe_str(v)},
        'university_en': {'label': '大学（英文）', 'width': 3.5, 'transform': lambda v: _safe_str(v)},
        'university_type': {'label': '大学类型', 'width': 2, 'transform': lambda v: _safe_str(v)},
        'university_ranking': {'label': '大学排名', 'width': 2, 'transform': lambda v: f'第{v}名' if v else '-'},
        'major_cn': {'label': '专业', 'width': 2.5, 'transform': lambda v: _safe_str(v)},
        'major_en': {'label': '专业（英文）', 'width': 2.5, 'transform': lambda v: _safe_str(v)},
        'major_category': {'label': '专业类别', 'width': 2, 'transform': lambda v: _safe_str(v)},
        'degree': {'label': '学位', 'width': 1.5, 'transform': lambda v: _safe_str(v)},
        'admission_type': {'label': '录取类型', 'width': 2, 'transform': lambda v: _safe_str(v)},
        'admission_status': {'label': '录取状态', 'width': 2, 'transform': lambda v: _safe_str(v)},
        'admission_year': {'label': '录取年份', 'width': 1.8, 'transform': lambda v: _safe_str(v)},
        'scholarship_amount': {'label': '奖学金', 'width': 2.5, 'transform': lambda v, r: format_scholarship(v, r)},
        'is_verified': {'label': '验证', 'width': 1.8, 'transform': lambda v: '已验证' if v else '待验证'},
    }
    
    # 获取用户选择的字段
    selected_fields = filters.get('fields', []) if filters else []
    if not selected_fields:
        selected_fields = ['student_name_cn', 'country', 'university_cn']
    
    # 过滤有效的字段
    valid_fields = [f for f in selected_fields if f in FIELD_DEFINITIONS]
    if not valid_fields:
        valid_fields = ['student_name_cn', 'country', 'university_cn']
    
    # 构建表头
    col_headers = [FIELD_DEFINITIONS[f]['label'] for f in valid_fields]
    col_widths = [FIELD_DEFINITIONS[f]['width'] * cm for f in valid_fields]
    
    table_data = [col_headers]
    
    for r in records:
        row_data = []
        for field in valid_fields:
            transform = FIELD_DEFINITIONS[field].get('transform', _safe_str)
            if field == 'scholarship_amount':
                row_data.append(transform(r.get(field), r))
            else:
                row_data.append(transform(r.get(field)))
        table_data.append(row_data)
    
    # 创建表格
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_CN),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8ff')]),
    ]
    
    table.setStyle(TableStyle(style_cmds))
    elements.append(table)
    
    # 页脚
    elements.append(Spacer(1, 0.5*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        fontName=FONT_CN
    )
    elements.append(Paragraph(f" 2026 贝优教育 - 共 {len(records)} 条记录 | 内部资料，请勿外传", footer_style))
    
    # 构建 PDF
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def format_scholarship(amt, record):
    """格式化奖学金金额"""
    if not amt:
        return '-'
    currency = record.get('scholarship_currency', '')
    return f"{currency} {amt:,}" if currency else f"{amt:,}"


def calculate_statistics(records):
    """计算统计数据"""
    total = len(records)
    verified = sum(1 for r in records if r.get('is_verified', 0) in (1, True))
    pending = total - verified
    with_scholarship = sum(1 for r in records if r.get('scholarship_amount') or r.get('scholarship'))
    
    return {
        'total': total,
        'verified': verified,
        'pending': pending,
        'with_scholarship': with_scholarship
    }
