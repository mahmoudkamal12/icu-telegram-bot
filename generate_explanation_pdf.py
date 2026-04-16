from fpdf import FPDF

class ICU_Bot_Explanation(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MK_ICU_MCQ: AI-Powered Intensive Care Education', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf():
    pdf = ICU_Bot_Explanation()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Introduction
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Introduction', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, (
        "MK_ICU_MCQ is a state-of-the-art Telegram bot designed to support the continuous professional "
        "development of doctors and nurses working in Intensive Care Units (ICUs). By leveraging local "
        "Large Language Models (LLMs), specifically optimized for medical knowledge, the bot provides "
        "high-quality, clinical-grade multiple-choice questions (MCQs) tailored for the European Diploma "
        "in Intensive Care (EDIC) and other professional certifications."
    ))
    pdf.ln(5)

    # Key Features
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Key Features', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, (
        "- AI-Driven Clinical Scenarios: Every question is a realistic patient case, testing diagnostic "
        "reasoning and immediate bedside management.\n"
        "- Automated Learning Schedule: Receives a fresh question every 6 hours to ensure continuous "
        "exposure to medical knowledge without overwhelming the clinician.\n"
        "- Comprehensive Explanations: Each answer is followed by a detailed clinical analysis and "
        "rationale with helpful tips.\n"
        "- Intelligent Variety: Uses a round-robin system across 21 medical chapters to ensure "
        "balanced coverage of all ICU domains."
    ))
    pdf.ln(5)

    # Educational Scope
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Educational Scope', 0, 1)
    pdf.set_font('Arial', '', 11)
    chapters = [
        "Ch 1: Basic Sciences (Physiology, Pharmacology)",
        "Ch 2: Resuscitation & Emergency Management",
        "Ch 3: Monitoring & Data Interpretation",
        "Ch 4-5: Cardio & Respiratory Disorders",
        "Ch 6: Sepsis & Septic Shock",
        "Ch 7: Neurological Critical Care",
        "Ch 8-10: Renal, Gastro, & Endocrine Disorders",
        "Ch 11: Hematology & Oncology",
        "Ch 12: Toxicology & Environmental Hazards",
        "Ch 13-14: Therapeutic Interventions & Procedures",
        "Ch 15: Peri-Operative Care",
        "Ch 16-17: Comfort, Recovery, & End-of-Life Care",
        "Ch 18-21: Pediatrics, Transport, & Patient Safety"
    ]
    for ch in chapters:
        pdf.cell(0, 6, f"  * {ch}", 0, 1)
    pdf.ln(5)

    # Importance
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. Why It Is Important for ICU Clinicians', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, (
        "- High-Stakes Environment: ICU is a fast-paced environment where quick, accurate decisions "
        "save lives. Regular practice with clinical scenarios sharpens these skills.\n"
        "- Exam Preparation: The content is specifically mapped to the CoBaTrICE (Competency-Based "
        "Training in Intensive Care Medicine in Europe) domains, the global standard for ICU training.\n"
        "- Convenience: Clinicians can study during brief downtimes, directly from their smartphones, "
        "making professional and personal life balance easier.\n"
        "- Reliability: Runs on local infrastructure to ensure privacy and availability."
    ))
    pdf.ln(5)

    # How to Start
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5. How to Start', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, (
        "Find the bot on Telegram and use these commands:\n"
        "/start  - Register and receive your first question.\n"
        "/next   - Get a new question immediately.\n"
        "/stop   - Pause the scheduled questions.\n"
        "/resume - Continue receiving periodic questions.\n"
        "/help   - View this guide at any time."
    ))

    pdf.output("ICU_Bot_Explanation.pdf")
    print("PDF generated successfully: ICU_Bot_Explanation.pdf")

if __name__ == "__main__":
    generate_pdf()
