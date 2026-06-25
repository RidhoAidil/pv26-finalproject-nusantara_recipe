import csv
import os
from datetime import datetime


def export_to_csv(recipes: list, filepath: str) -> tuple:
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["No", "Nama Resep", "Kategori", "Daerah Asal",
                             "Waktu Masak (menit)", "Porsi", "Ditambahkan"])
            for i, r in enumerate(recipes, 1):
                writer.writerow([
                    i, r["name"], r.get("category_name", ""),
                    r.get("origin_region", ""), r.get("cook_time_minutes", 0),
                    r.get("servings", 1), r.get("created_at", ""),
                ])
        return True, filepath
    except Exception as e:
        return False, str(e)


def export_recipe_to_pdf(recipe: dict, ingredients: list, steps: list, filepath: str) -> tuple:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        PRIMARY = HexColor("#8B4513")
        ACCENT = HexColor("#D2691E")
        LIGHT_BG = HexColor("#FFF8F0")
        DARK_TEXT = HexColor("#2C1810")

        title_style = ParagraphStyle("Title", parent=styles["Title"],
                                     fontSize=22, textColor=PRIMARY,
                                     spaceAfter=6, fontName="Helvetica-Bold",
                                     alignment=TA_CENTER)
        sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
                                   fontSize=11, textColor=ACCENT,
                                   spaceAfter=4, alignment=TA_CENTER)
        h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                                  fontSize=13, textColor=PRIMARY,
                                  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                    fontSize=10, textColor=DARK_TEXT,
                                    leading=16, spaceAfter=4)
        step_style = ParagraphStyle("Step", parent=styles["Normal"],
                                    fontSize=10, textColor=DARK_TEXT,
                                    leading=16, spaceAfter=6, leftIndent=10)

        elements = []

        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(recipe["name"], title_style))
        elements.append(Paragraph(f"Kategori: {recipe.get('category_name', '-')}  |  "
                                  f"Daerah: {recipe.get('origin_region', '-')}", sub_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

        meta_data = [
            ["⏱ Waktu Masak", f"{recipe.get('cook_time_minutes', 0)} menit",
             "🍽 Porsi", f"{recipe.get('servings', 1)} orang"]
        ]
        meta_table = Table(meta_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("TEXTCOLOR", (0, 0), (-1, -1), DARK_TEXT),
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, ACCENT),
            ("ROUNDEDCORNERS", [4]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.4*cm))

        if recipe.get("description"):
            elements.append(Paragraph("Deskripsi", h2_style))
            elements.append(Paragraph(recipe["description"], body_style))

        elements.append(Paragraph("Bahan-Bahan", h2_style))
        if ingredients:
            ing_data = [["Bahan", "Jumlah", "Satuan"]]
            for ing in ingredients:
                ing_data.append([ing["name"], ing.get("amount", ""), ing.get("unit", "")])
            ing_table = Table(ing_data, colWidths=[9*cm, 4*cm, 4*cm])
            ing_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E0C0A0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(ing_table)
        else:
            elements.append(Paragraph("Belum ada bahan.", body_style))

        elements.append(Paragraph("Cara Memasak", h2_style))
        if steps:
            for s in steps:
                elements.append(Paragraph(
                    f"<b>{s['step_no']}.</b>  {s['instruction']}", step_style
                ))
        else:
            elements.append(Paragraph("Belum ada langkah.", body_style))

        elements.append(Spacer(1, 1*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        elements.append(Paragraph(
            f"<i>Diekspor dari Nusantara Recipe · {datetime.now().strftime('%d %B %Y %H:%M')}</i>",
            ParagraphStyle("Footer", parent=styles["Normal"],
                           fontSize=8, textColor=HexColor("#999999"), alignment=TA_CENTER)
        ))

        doc.build(elements)
        return True, filepath
    except ImportError:
        return False, "reportlab belum terinstall. Jalankan: pip install reportlab"
    except Exception as e:
        return False, str(e)