from docx import Document

doc = Document('Asset_Management_System_Current_State_FRS.docx')

# Extract section 3 - Current Functional Requirements
start_capturing = False
for para in doc.paragraphs:
    text = para.text.strip()
    
    if "3. Current Functional Requirements" in text:
        start_capturing = True
    
    if start_capturing:
        if text and "7. Out of Scope" in text:
            break
        print(text)
