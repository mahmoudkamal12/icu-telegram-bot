import random

def get_random_icu_chapter_and_lesson(exclude_chapters=None):
    """
    Selects a random chapter, a random main lesson from that chapter,
    and a random sub-point from that lesson from a predefined ICU book structure.
    Optionally excludes a list of chapter titles.
    """
    # Data for Chapters 1-12 (Original)
    icu_data_chapters_1_12 = [
        {
            "chapter_title": "Chapter 1: Basic Sciences in Critical Care",
            "lessons": [
                {
                    "lesson_title": "1.1 Applied Physiology in Critical Illness",
                    "sub_points": [
                        "1.1.1 Cardiovascular Physiology",
                        "1.1.2 Respiratory Physiology",
                        "1.1.3 Renal Physiology",
                        "1.1.4 Neurological Physiology",
                        "1.1.5 Endocrine and Metabolic Physiology",
                        "1.1.6 Gastrointestinal and Hepatic Physiology"
                    ]
                },
                {
                    "lesson_title": "1.2 Pathophysiology of Organ Dysfunction in Critical Illness",
                    "sub_points": [
                        "1.2.1 Cellular Injury and Death: Hypoxia, Ischemia-Reperfusion, Necrosis, Apoptosis",
                        "1.2.2 Inflammation: SIRS, CARS, Cytokines, Chemokines, Complement System, Arachidonic Acid Metabolites",
                        "1.2.3 Endothelial Dysfunction and Microcirculatory Disturbances",
                        "1.2.4 Pathophysiology of Shock (General and Specific Types)",
                        "1.2.5 Pathophysiology of ARDS, AKI, MODS",
                        "1.2.6 Coagulation Cascade and Pathophysiology of DIC"
                    ]
                },
                {
                    "lesson_title": "1.3 Pharmacology and Pharmacokinetics in the Critically Ill",
                    "sub_points": [
                        "1.3.1 Principles: Absorption, Distribution, Metabolism, Excretion",
                        "1.3.2 Pharmacodynamics: Receptor Theory, Dose-Response Relationships",
                        "1.3.3 Impact of Critical Illness on Drug Handling",
                        "1.3.4 Drug Dosing Strategies: Loading Doses, Maintenance Doses, TDM",
                        "1.3.5 Common Drug Interactions and Adverse Drug Reactions in ICU",
                        "1.3.6 Key Drug Classes Overview"
                    ]
                },
                {
                    "lesson_title": "1.4 Metabolism, Inflammation, and Immunology in Critical Illness",
                    "sub_points": [
                        "1.4.1 Metabolic Response to Injury: Hypermetabolism, Catabolism",
                        "1.4.2 Innate and Adaptive Immunity in Critical Illness",
                        "1.4.3 Immunomodulation and Immunoparalysis",
                        "1.4.4 Role of Oxidative Stress"
                    ]
                },
                {
                    "lesson_title": "1.5 Microbiology and Host Defense",
                    "sub_points": [
                        "1.5.1 Common ICU Pathogens",
                        "1.5.2 Mechanisms of Microbial Pathogenicity",
                        "1.5.3 Host Defense Mechanisms against Infection",
                        "1.5.4 Antimicrobial Resistance",
                        "1.5.5 Principles of Infection Control and Antimicrobial Stewardship"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 2: Resuscitation and Initial Management of the Acutely Ill Patient (CoBaTrICE Domain 1)",
            "lessons": [
                {
                    "lesson_title": "2.1 Recognition of the Critically Ill Patient",
                    "sub_points": [
                        "2.1.1 Early Warning Scores and Track & Trigger Systems",
                        "2.1.2 Structured Assessment: ABCDE Approach"
                    ]
                },
                {
                    "lesson_title": "2.2 Advanced Life Support (ALS)",
                    "sub_points": [
                        "2.2.1 Current Resuscitation Guidelines (ERC/AHA)",
                        "2.2.2 Recognition of Peri-Arrest Rhythms and Cardiac Arrest",
                        "2.2.3 High-Quality Cardiopulmonary Resuscitation (CPR)",
                        "2.2.4 Airway Management in Cardiac Arrest",
                        "2.2.5 Pharmacological Interventions in ALS",
                        "2.2.6 Management of Reversible Causes (Hs and Ts)",
                        "2.2.7 Special Circumstances in ALS"
                    ]
                },
                {
                    "lesson_title": "2.3 Post-Resuscitation Care",
                    "sub_points": [
                        "2.3.1 Targeted Temperature Management (TTM)",
                        "2.3.2 Hemodynamic Optimization Post-Arrest",
                        "2.3.3 Ventilatory Management Post-Arrest",
                        "2.3.4 Neurological Assessment and Prognostication Post-Arrest",
                        "2.3.5 Glycemic Control and Metabolic Considerations Post-Arrest"
                    ]
                },
                {
                    "lesson_title": "2.4 Shock: Recognition and Initial Management",
                    "sub_points": [
                        "2.4.1 Definitions and Classification of Shock",
                        "2.4.2 Pathophysiology and Clinical Presentation of Shock Types",
                        "2.4.3 Initial Resuscitation Goals in Shock",
                        "2.4.4 Fluid Therapy in Shock",
                        "2.4.5 Early Use of Vasoactive Agents in Shock"
                    ]
                },
                {
                    "lesson_title": "2.5 Management of Severe Trauma",
                    "sub_points": [
                        "2.5.1 ATLS Principles: Primary and Secondary Survey",
                        "2.5.2 Damage Control Resuscitation",
                        "2.5.3 Traumatic Brain Injury (TBI): Initial Management",
                        "2.5.4 Thoracic Trauma Management",
                        "2.5.5 Abdominal Trauma Management",
                        "2.5.6 Spinal Cord Injury: Initial Management",
                        "2.5.7 Coagulopathy of Trauma"
                    ]
                },
                {
                    "lesson_title": "2.6 Management of Severe Burns",
                    "sub_points": [
                        "2.6.1 Assessment of Burns (TBSA, Depth, Inhalation Injury)",
                        "2.6.2 Initial Management of Burns (Airway, Breathing, Circulation)",
                        "2.6.3 Management of Inhalation Injury",
                        "2.6.4 Escharotomy/Fasciotomy Indications"
                    ]
                },
                {
                    "lesson_title": "2.7 Triage and Prioritization in ICU",
                    "sub_points": [
                        "2.7.1 Principles of Triage in Resource-Limited Situations",
                        "2.7.2 Criteria for ICU Admission and Discharge",
                        "2.7.3 Ethical Considerations in Triage"
                    ]
                },
                {
                    "lesson_title": "2.8 Mass Casualty Incidents (MCI)",
                    "sub_points": [
                        "2.8.1 ICU Role and Preparedness in MCI",
                        "2.8.2 Triage Systems in MCI"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 3: Diagnosis: Assessment, Investigation, Monitoring, and Data Interpretation (CoBaTrICE Domain 2)",
            "lessons": [
                {
                    "lesson_title": "3.1 Clinical Assessment in the ICU",
                    "sub_points": [
                        "3.1.1 Structured Daily Review and Goal Setting",
                        "3.1.2 Comprehensive Physical Examination",
                        "3.1.3 Neurological Examination in ICU",
                        "3.1.4 Pain, Agitation, and Delirium (PAD) Assessment"
                    ]
                },
                {
                    "lesson_title": "3.2 Hemodynamic Monitoring",
                    "sub_points": [
                        "3.2.1 Non-Invasive Hemodynamic Monitoring",
                        "3.2.2 Invasive Arterial Blood Pressure Monitoring",
                        "3.2.3 Central Venous Pressure (CVP) Monitoring",
                        "3.2.4 Pulmonary Artery Catheter (PAC)",
                        "3.2.5 Less Invasive Cardiac Output Monitoring Techniques",
                        "3.2.6 Assessment of Fluid Responsiveness",
                        "3.2.7 Microcirculatory Monitoring Principles"
                    ]
                },
                {
                    "lesson_title": "3.3 Respiratory Monitoring",
                    "sub_points": [
                        "3.3.1 Pulse Oximetry (SpO₂)",
                        "3.3.2 Capnography (ETCO₂)",
                        "3.3.3 Mechanical Ventilator Waveform Analysis",
                        "3.3.4 Lung Mechanics Assessment",
                        "3.3.5 Advanced Respiratory Monitoring Techniques"
                    ]
                },
                {
                    "lesson_title": "3.4 Neurological Monitoring",
                    "sub_points": [
                        "3.4.1 Intracranial Pressure (ICP) Monitoring",
                        "3.4.2 Cerebral Perfusion Pressure (CPP) Management",
                        "3.4.3 Electroencephalography (EEG) in ICU",
                        "3.4.4 Evoked Potentials",
                        "3.4.5 Transcranial Doppler (TCD)",
                        "3.4.6 Brain Tissue Oxygen Monitoring (PbtO₂)",
                        "3.4.7 Pupillometry and Jugular Venous Oximetry"
                    ]
                },
                {
                    "lesson_title": "3.5 Laboratory Data Interpretation",
                    "sub_points": [
                        "3.5.1 Arterial Blood Gas (ABG) Interpretation",
                        "3.5.2 Acid-Base Disturbances Analysis",
                        "3.5.3 Renal Function Test Interpretation",
                        "3.5.4 Liver Function Test Interpretation",
                        "3.5.5 Hematological Profile Interpretation",
                        "3.5.6 Electrolyte Imbalance Interpretation",
                        "3.5.7 Endocrine Test Interpretation in Critical Illness",
                        "3.5.8 Cardiac Biomarker Interpretation",
                        "3.5.9 Inflammatory Marker Interpretation",
                        "3.5.10 Microbiological Investigation Interpretation"
                    ]
                },
                {
                    "lesson_title": "3.6 Imaging Interpretation in ICU",
                    "sub_points": [
                        "3.6.1 Chest X-Ray (CXR) Interpretation",
                        "3.6.2 Computed Tomography (CT) Interpretation (Head, Chest, Abdomen/Pelvis)",
                        "3.6.3 Ultrasound (POCUS) Interpretation (Cardiac, Lung, Abdominal, Vascular)",
                        "3.6.4 Electrocardiogram (ECG) Interpretation in ICU"
                    ]
                },
                {
                    "lesson_title": "3.7 Integrating Data for Clinical Decision Making",
                    "sub_points": [
                        "3.7.1 Formulating a Differential Diagnosis",
                        "3.7.2 Bayesian Reasoning and Likelihood Ratios",
                        "3.7.3 Dynamic Assessment and Re-evaluation"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 4: Disease Management - Cardiovascular System Disorders",
            "lessons": [
                {"lesson_title": "4.1 Acute Coronary Syndromes (ACS)", "sub_points": ["4.1.1 Pathophysiology and Definitions of ACS", "4.1.2 Diagnosis of ACS", "4.1.3 Initial Management of ACS", "4.1.4 Reperfusion Strategies for STEMI", "4.1.5 Management of NSTEMI/UA", "4.1.6 Complications of Myocardial Infarction"]},
                {"lesson_title": "4.2 Heart Failure (HF) and Cardiogenic Shock", "sub_points": ["4.2.1 Definitions and Types of Heart Failure", "4.2.2 Pathophysiology and Diagnosis of ADHF", "4.2.3 Management of ADHF", "4.2.4 Cardiogenic Shock: Etiologies and Management", "4.2.5 Mechanical Circulatory Support (MCS)", "4.2.6 Right Ventricular Failure Management"]},
                {"lesson_title": "4.3 Arrhythmias in the ICU", "sub_points": ["4.3.1 Approach to Arrhythmias", "4.3.2 Bradyarrhythmias Management", "4.3.3 Tachyarrhythmias Management (AF/Flutter, SVT, VT/VF, Torsades)"]},
                {"lesson_title": "4.4 Valvular Heart Disease in Critical Care", "sub_points": ["4.4.1 Acute Valvular Regurgitation Management", "4.4.2 Critical Valvular Stenosis Management", "4.4.3 Prosthetic Valve Complications", "4.4.4 Infective Endocarditis Management"]},
                {"lesson_title": "4.5 Pulmonary Embolism (PE)", "sub_points": ["4.5.1 Risk Factors and Pathophysiology of PE", "4.5.2 Diagnosis of PE", "4.5.3 Risk Stratification of PE", "4.5.4 Management of PE (Anticoagulation, Thrombolysis, Advanced Therapies)"]},
                {"lesson_title": "4.6 Hypertensive Emergencies", "sub_points": ["4.6.1 Definitions and Assessment", "4.6.2 Management Goals and IV Antihypertensives", "4.6.3 Management in Specific Conditions"]},
                {"lesson_title": "4.7 Pericardial Diseases", "sub_points": ["4.7.1 Acute Pericarditis Management", "4.7.2 Cardiac Tamponade Management"]},
                {"lesson_title": "4.8 Aortic Dissection", "sub_points": ["4.8.1 Classification and Pathophysiology", "4.8.2 Diagnosis of Aortic Dissection", "4.8.3 Medical and Surgical Management of Aortic Dissection"]},
                {"lesson_title": "4.9 Post-Cardiac Surgery ICU Care", "sub_points": ["4.9.1 Routine Post-operative Care", "4.9.2 Common Complications after Cardiac Surgery"]}
            ]
        },
        {
            "chapter_title": "Chapter 5: Disease Management - Respiratory System Disorders",
            "lessons": [
                {"lesson_title": "5.1 Acute Respiratory Distress Syndrome (ARDS)", "sub_points": ["5.1.1 Definition, Etiologies, and Pathophysiology of ARDS", "5.1.2 Diagnosis of ARDS", "5.1.3 Mechanical Ventilation Strategies in ARDS", "5.1.4 Adjunctive Therapies for ARDS (Prone, NMBs, Fluids, ECMO)", "5.1.5 Ventilator-Associated Lung Injury (VALI)"]},
                {"lesson_title": "5.2 Severe Pneumonia", "sub_points": ["5.2.1 Definitions and Classifications of Pneumonia", "5.2.2 Etiology and Risk Factors for MDR Organisms", "5.2.3 Diagnosis and Severity Assessment of Pneumonia", "5.2.4 Antimicrobial Therapy for Pneumonia", "5.2.5 VAP Prevention and Complication Management"]},
                {"lesson_title": "5.3 Obstructive Lung Diseases in ICU", "sub_points": ["5.3.1 Severe Acute Asthma Management", "5.3.2 Acute Exacerbation of COPD (AECOPD) Management (including NIV and Mechanical Ventilation)"]},
                {"lesson_title": "5.4 Pleural Diseases", "sub_points": ["5.4.1 Pleural Effusion Diagnosis and Management", "5.4.2 Parapneumonic Effusion and Empyema Management", "5.4.3 Pneumothorax (Tension and Simple) Management", "5.4.4 Hemothorax and Bronchopleural Fistula"]},
                {"lesson_title": "5.5 Pulmonary Hypertension (PH) in the Critically Ill", "sub_points": ["5.5.1 Classification and Pathophysiology of PH with RV Dysfunction", "5.5.2 Diagnosis of PH in ICU", "5.5.3 Management Principles for PH in ICU"]},
                {"lesson_title": "5.6 Weaning from Mechanical Ventilation and Extubation", "sub_points": ["5.6.1 Readiness Assessment and Weaning Predictors", "5.6.2 Spontaneous Breathing Trials (SBT)", "5.6.3 Extubation Criteria and Post-Extubation Management", "5.6.4 Difficult and Prolonged Weaning (including Tracheostomy)"]},
                {"lesson_title": "5.7 Non-Invasive Ventilation (NIV) (General Principles)", "sub_points": ["5.7.1 Physiology, Interfaces, and Modes of NIV", "5.7.2 Indications and Contraindications for NIV", "5.7.3 Initiation, Titration, and Monitoring of NIV"]},
                {"lesson_title": "5.8 Other Respiratory Conditions", "sub_points": ["5.8.1 Massive Hemoptysis Management", "5.8.2 Fat Embolism Syndrome and Diffuse Alveolar Hemorrhage", "5.8.3 Management of Chest Wall Disorders and Diaphragmatic Dysfunction"]}
            ]
        },
        {
            "chapter_title": "Chapter 6: Disease Management - Sepsis and Septic Shock",
            "lessons": [
                {"lesson_title": "6.1 Definitions and Epidemiology of Sepsis", "sub_points": ["6.1.1 Sepsis-3 Criteria", "6.1.2 Incidence and Global Burden of Sepsis"]},
                {"lesson_title": "6.2 Pathophysiology of Sepsis", "sub_points": ["6.2.1 Host Response and Microbial Factors", "6.2.2 Endothelial Dysfunction and Microcirculatory Failure", "6.2.3 Cardiovascular Dysfunction in Sepsis", "6.2.4 Mechanisms of Organ Dysfunction in Sepsis", "6.2.5 Immunoparalysis in Sepsis"]},
                {"lesson_title": "6.3 Recognition and Diagnosis of Sepsis", "sub_points": ["6.3.1 Clinical Manifestations and Screening Tools", "6.3.2 Biomarkers in Sepsis (Lactate, Procalcitonin)", "6.3.3 Differentiating Sepsis from Non-Infectious SIRS"]},
                {"lesson_title": "6.4 Initial Resuscitation and Management (SSC Guidelines)", "sub_points": ["6.4.1 Hour-1 Bundle Components", "6.4.2 Fluid Resuscitation Strategies", "6.4.3 Vasoactive Medications in Sepsis", "6.4.4 Oxygenation and Ventilatory Support in Sepsis"]},
                {"lesson_title": "6.5 Source Identification and Control", "sub_points": ["6.5.1 Importance and Common Sources of Infection", "6.5.2 Diagnostic Imaging and Interventions for Source Control", "6.5.3 Timing of Source Control"]},
                {"lesson_title": "6.6 Antimicrobial Therapy in Sepsis", "sub_points": ["6.6.1 Principles of Empiric and Directed Therapy", "6.6.2 PK/PD Optimization and De-escalation", "6.6.3 Duration of Therapy and Stewardship"]},
                {"lesson_title": "6.7 Adjunctive Therapies in Sepsis", "sub_points": ["6.7.1 Corticosteroids in Septic Shock", "6.7.2 Blood Product Transfusion in Sepsis", "6.7.3 Other Investigational Adjunctive Therapies"]},
                {"lesson_title": "6.8 Specific Organ Dysfunction Management in Sepsis", "sub_points": ["Overview - cross-reference to organ-specific chapters"]},
                {"lesson_title": "6.9 Monitoring Response to Sepsis Therapy", "sub_points": ["6.9.1 Clinical Parameters and Biomarkers for Monitoring", "6.9.2 Serial Assessment of Organ Function"]},
                {"lesson_title": "6.10 Long-Term Sequelae (Post-Sepsis Syndrome)", "sub_points": ["6.10.1 Physical, Cognitive, and Psychological Impairments after Sepsis"]}
            ]
        },
        {
            "chapter_title": "Chapter 7: Disease Management - Neurological Critical Care",
            "lessons": [
                {"lesson_title": "7.1 Traumatic Brain Injury (TBI)", "sub_points": ["7.1.1 Classification and Pathophysiology of TBI", "7.1.2 Initial Assessment and Neuroimaging in TBI", "7.1.3 ICP/CPP Management Strategies", "7.1.4 Seizure Management and Other Supportive Care in TBI", "7.1.5 Complications of TBI"]},
                {"lesson_title": "7.2 Stroke in ICU", "sub_points": ["7.2.1 Ischemic Stroke: Diagnosis and Acute Management (Thrombolysis, Thrombectomy)", "7.2.2 Hemorrhagic Stroke (ICH & SAH): Diagnosis and Management (BP control, Reversal, Vasospasm)"]},
                {"lesson_title": "7.3 Status Epilepticus", "sub_points": ["7.3.1 Definitions and Etiologies of Status Epilepticus", "7.3.2 Management Algorithm for Status Epilepticus (including Refractory SE)"]},
                {"lesson_title": "7.4 Meningitis and Encephalitis", "sub_points": ["7.4.1 Bacterial Meningitis: Diagnosis and Management", "7.4.2 Viral Meningitis/Encephalitis: Diagnosis and Management"]},
                {"lesson_title": "7.5 Neuromuscular Disorders", "sub_points": ["7.5.1 Guillain-Barré Syndrome (GBS) Management", "7.5.2 Myasthenia Gravis/Myasthenic Crisis Management", "7.5.3 Critical Illness Polyneuropathy (CIP) and Myopathy (CIM)"]},
                {"lesson_title": "7.6 Delirium in the ICU", "sub_points": ["7.6.1 Definition, Assessment, and Risk Factors for Delirium", "7.6.2 Non-Pharmacological and Pharmacological Management of Delirium"]},
                {"lesson_title": "7.7 Brain Death", "sub_points": ["7.7.1 Definition, Clinical Examination, and Confirmatory Tests for Brain Death", "7.7.2 Legal/Ethical Aspects and Family Communication", "7.7.3 Physiological Support of the Organ Donor"]},
                {"lesson_title": "7.8 Acute Spinal Cord Injury", "sub_points": ["7.8.1 Assessment and Initial Management of Acute Spinal Cord Injury", "7.8.2 Respiratory and Hemodynamic Management in Spinal Cord Injury"]}
            ]
        },
        {
            "chapter_title": "Chapter 8: Disease Management - Renal and Genitourinary System Disorders",
            "lessons": [
                {"lesson_title": "8.1 Acute Kidney Injury (AKI)", "sub_points": ["8.1.1 Definition, Classification, and Pathophysiology of AKI", "8.1.2 Diagnosis of AKI (including Biomarkers)", "8.1.3 Prevention and Management of AKI (Fluids, Nephrotoxins, Drug Dosing)"]},
                {"lesson_title": "8.2 Renal Replacement Therapy (RRT)", "sub_points": ["8.2.1 Indications and Timing of RRT", "8.2.2 Modalities of RRT (IHD, CRRT, SLED)", "8.2.3 Vascular Access and Anticoagulation for RRT", "8.2.4 Complications and Weaning from RRT"]},
                {"lesson_title": "8.3 Specific Renal Syndromes", "sub_points": ["8.3.1 Hepatorenal Syndrome (HRS) Management", "8.3.2 Cardiorenal Syndrome (CRS) Management", "8.3.3 Rhabdomyolysis and AKI Management", "8.3.4 Tumor Lysis Syndrome (TLS) and AKI Management"]},
                {"lesson_title": "8.4 Fluid, Electrolyte, and Acid-Base Disturbances (Detailed)", "sub_points": ["8.4.1 Sodium Disorders (Hyponatremia, Hypernatremia)", "8.4.2 Potassium Disorders (Hypokalemia, Hyperkalemia)", "8.4.3 Calcium, Phosphate, Magnesium Disorders", "8.4.4 Complex Acid-Base Disorders Management"]},
                {"lesson_title": "8.5 Urological Emergencies in ICU", "sub_points": ["8.5.1 Management of Acute Urinary Retention/Obstruction", "8.5.2 Management of Fournier's Gangrene and Priapism"]},
                {"lesson_title": "8.6 Obstetric Critical Care", "sub_points": ["8.6.1 Management of Pre-eclampsia/Eclampsia and HELLP Syndrome", "8.6.2 Management of Other Obstetric Emergencies in ICU (AFLP, AFE, PPH, PPCM)"]}
            ]
        },
        {
            "chapter_title": "Chapter 9: Disease Management - Gastrointestinal and Hepatic Disorders",
            "lessons": [
                {"lesson_title": "9.1 Gastrointestinal Bleeding", "sub_points": ["9.1.1 Upper GI Bleed (Variceal/Non-Variceal) Management", "9.1.2 Lower GI Bleed Management", "9.1.3 Stress Ulcer Prophylaxis"]},
                {"lesson_title": "9.2 Acute Pancreatitis", "sub_points": ["9.2.1 Diagnosis and Severity Assessment of Acute Pancreatitis", "9.2.2 Management of Acute Pancreatitis (Fluids, Nutrition, Complications)"]},
                {"lesson_title": "9.3 Acute Liver Failure (ALF)", "sub_points": ["9.3.1 Etiologies and Clinical Features of ALF", "9.3.2 Management of ALF (Supportive Care, Specific Therapies, Transplant Criteria)"]},
                {"lesson_title": "9.4 Acute-on-Chronic Liver Failure (ACLF)", "sub_points": ["9.4.1 Definition, Precipitants, and Management of ACLF"]},
                {"lesson_title": "9.5 Complications of Cirrhosis in ICU", "sub_points": ["Management of Ascites/SBP, Hepatic Encephalopathy, Coagulopathy in Cirrhosis"]},
                {"lesson_title": "9.6 Abdominal Sepsis and Peritonitis", "sub_points": ["9.6.1 Etiologies, Diagnosis, and Management of Abdominal Sepsis"]},
                {"lesson_title": "9.7 Ileus and Bowel Obstruction", "sub_points": ["9.7.1 Differentiating and Managing Paralytic Ileus vs. Mechanical Obstruction", "9.7.2 Management of Ogilvie's Syndrome"]},
                {"lesson_title": "9.8 Mesenteric Ischemia", "sub_points": ["9.8.1 Diagnosis and Management of Occlusive and Non-Occlusive Mesenteric Ischemia"]},
                {"lesson_title": "9.9 Abdominal Compartment Syndrome (ACS) / Intra-Abdominal Hypertension (IAH)", "sub_points": ["9.9.1 Definitions, Measurement, and Management of IAH/ACS"]},
                {"lesson_title": "9.10 Diarrhea and Constipation in ICU", "sub_points": ["9.10.1 Management of C. difficile Infection and Other Causes of Diarrhea", "9.10.2 Management of Constipation in ICU"]},
                {"lesson_title": "9.11 Nutritional Support in the Critically Ill", "sub_points": ["9.11.1 Assessment of Nutritional Needs", "9.11.2 Enteral Nutrition (EN): Benefits, Routes, Complications", "9.11.3 Parenteral Nutrition (PN): Indications, Components, Complications", "9.11.4 Refeeding Syndrome and Immunonutrition"]}
            ]
        },
        {
            "chapter_title": "Chapter 10: Disease Management - Endocrine and Metabolic Disorders",
            "lessons": [
                {"lesson_title": "10.1 Diabetic Emergencies", "sub_points": ["10.1.1 Diabetic Ketoacidosis (DKA) Management", "10.1.2 Hyperosmolar Hyperglycemic State (HHS) Management", "10.1.3 Hypoglycemia Management in ICU"]},
                {"lesson_title": "10.2 Glycemic Control in ICU", "sub_points": ["10.2.1 Stress Hyperglycemia and Glycemic Targets", "10.2.2 Insulin Protocols and Glucose Monitoring"]},
                {"lesson_title": "10.3 Adrenal Insufficiency (CIRCI)", "sub_points": ["10.3.1 Diagnosis and Management of CIRCI (including Hydrocortisone use)"]},
                {"lesson_title": "10.4 Thyroid Emergencies", "sub_points": ["10.4.1 Thyroid Storm Management", "10.4.2 Myxedema Coma Management", "10.4.3 Sick Euthyroid Syndrome (NTIS) Interpretation"]},
                {"lesson_title": "10.5 Disorders of Water Balance", "sub_points": ["10.5.1 Diabetes Insipidus (DI) Management", "10.5.2 Syndrome of Inappropriate Antidiuretic Hormone Secretion (SIADH) Management"]},
                {"lesson_title": "10.6 Calcium, Phosphate, Magnesium Disorders", "sub_points": ["10.6.1 Management of Hypercalcemia/Hypocalcemia", "10.6.2 Management of Hyperphosphatemia/Hypophosphatemia", "10.6.3 Management of Hypermagnesemia/Hypomagnesemia"]},
                {"lesson_title": "10.7 Other Endocrine Conditions", "sub_points": ["Overview of Pheochromocytoma Crisis and Carcinoid Crisis"]}
            ]
        },
        {
            "chapter_title": "Chapter 11: Disease Management - Hematology and Oncology in the ICU",
            "lessons": [
                {"lesson_title": "11.1 Disorders of Hemostasis", "sub_points": ["11.1.1 Approach to the Bleeding Patient and Laboratory Evaluation", "11.1.2 Disseminated Intravascular Coagulation (DIC) Management", "11.1.3 Anticoagulant Reversal Strategies", "11.1.4 Thrombocytopenia Management (including HIT and TTP/HUS)"]},
                {"lesson_title": "11.2 Transfusion Practices", "sub_points": ["11.2.1 Indications and Thresholds for Blood Products (RBCs, Platelets, FFP, Cryo)", "11.2.2 Massive Transfusion Protocols (MTP)", "11.2.3 Transfusion Reactions Management", "11.2.4 Patient Blood Management Principles"]},
                {"lesson_title": "11.3 Venous Thromboembolism (VTE) in ICU", "sub_points": ["11.3.1 Risk Factors and Prophylaxis for VTE", "11.3.2 Diagnosis and Management of Established VTE in ICU"]},
                {"lesson_title": "11.4 Oncological Emergencies", "sub_points": ["11.4.1 Tumor Lysis Syndrome Management", "11.4.2 Febrile Neutropenia Management", "11.4.3 Superior Vena Cava (SVC) Syndrome Management", "11.4.4 Malignant Spinal Cord Compression Management", "11.4.5 Leukostasis/Hyperviscosity Syndrome Management", "11.4.6 Management of Complications from Chemotherapy/Radiotherapy and Immunotherapy"]},
                {"lesson_title": "11.5 Hematopoietic Stem Cell Transplantation (HSCT) Complications in ICU", "sub_points": ["Management of Engraftment Syndrome, GVHD, Infections, Pulmonary Complications, SOS/VOD"]},
                {"lesson_title": "11.6 Ethical Considerations in Oncological Critical Care", "sub_points": ["Goals of Care Discussions and Palliative Care Integration"]}
            ]
        },
        {
            "chapter_title": "Chapter 12: Disease Management - Toxicology and Environmental Hazards",
            "lessons": [
                {"lesson_title": "12.1 General Approach to the Poisoned Patient", "sub_points": ["12.1.1 Initial Assessment, Toxidrome Recognition", "12.1.2 Diagnostic Investigations in Toxicology", "12.1.3 Principles of Decontamination", "12.1.4 Techniques for Enhanced Elimination", "12.1.5 General Use of Antidotes"]},
                {"lesson_title": "12.2 Specific Poisonings", "sub_points": ["Management of Paracetamol Poisoning", "Management of Salicylate Poisoning", "Management of Opioid Overdose", "Management of Benzodiazepine Overdose", "Management of TCA Poisoning", "Management of Serotonin Syndrome", "Management of Beta-Blocker/Calcium Channel Blocker Poisoning", "Management of Digoxin Poisoning", "Management of Toxic Alcohol Poisoning (Methanol, Ethylene Glycol)", "Management of Carbon Monoxide Poisoning", "Management of Cyanide Poisoning", "Management of Organophosphate/Carbamate Poisoning", "Management of Lithium Poisoning", "Management of Cocaine/Amphetamine Poisoning"]},
                {"lesson_title": "12.3 Environmental Hazards", "sub_points": ["12.3.1 Hypothermia Management", "12.3.2 Hyperthermia (Heat Stroke) Management", "12.3.3 Drowning Management", "12.3.4 Electrical/Lightning Injuries Management", "12.3.5 Envenomation Management Principles"]},
                {"lesson_title": "12.4 Withdrawal Syndromes in ICU", "sub_points": ["12.4.1 Alcohol Withdrawal Syndrome (AWS) Management", "12.4.2 Opioid and Benzodiazepine Withdrawal Management"]}
            ]
        }
    ]

    # Data for Chapters 13-21 (Other Domains)
    other_domains_icu_data = [
        {
            "chapter_title": "Chapter 13: Therapeutic Interventions and Organ System Support (CoBaTrICE Domain 4)",
            "lessons": [
                {
                    "lesson_title": "13.1 Advanced Mechanical Ventilation Management",
                    "sub_points": [
                        "13.1.1 Modes of Mechanical Ventilation (Beyond Basics)",
                        "13.1.2 Ventilator-Associated Pneumonia (VAP) Prevention and Management Strategies",
                        "13.1.3 Troubleshooting Complex Ventilator Scenarios",
                        "13.1.4 Liberation from Mechanical Ventilation: Advanced Techniques and Protocols",
                        "13.1.5 Specific Ventilatory Strategies (e.g., APRV, HFOV - principles)"
                    ]
                },
                {
                    "lesson_title": "13.2 Advanced Hemodynamic Support Interventions",
                    "sub_points": [
                        "13.2.1 Detailed Pharmacology of Vasoactive Drugs (Inotropes, Vasopressors, Vasodilators)",
                        "13.2.2 Mechanical Circulatory Support Devices (IABP, VADs, ECMO) - Focus on Implementation and Management",
                        "13.2.3 Goal-Directed Hemodynamic Therapy Protocols",
                        "13.2.4 Management of Refractory Shock"
                    ]
                },
                {
                    "lesson_title": "13.3 Renal Replacement Therapy (RRT) Implementation",
                    "sub_points": [
                        "13.3.1 Practical Aspects of Initiating and Managing CRRT/IHD in ICU",
                        "13.3.2 Anticoagulation Strategies for RRT: Detailed Management",
                        "13.3.3 Troubleshooting RRT Circuits and Complications",
                        "13.3.4 Fluid Removal and Solute Clearance Targets and Adjustments"
                    ]
                },
                {
                    "lesson_title": "13.4 Fluid Management Strategies in Complex Patients",
                    "sub_points": [
                        "13.4.1 Assessing Fluid Status and Responsiveness: Advanced Techniques",
                        "13.4.2 Fluid Stewardship: Phases of Resuscitation (ROSE concept)",
                        "13.4.3 De-resuscitation and Diuretic Strategies",
                        "13.4.4 Management of Fluid Overload and its Consequences"
                    ]
                },
                {
                    "lesson_title": "13.5 Advanced Analgesia, Sedation, and Neuromuscular Blockade Techniques",
                    "sub_points": [
                        "13.5.1 Multimodal Analgesia Strategies",
                        "13.5.2 Sedation Protocols and Titration to Goals (Light vs. Deep Sedation)",
                        "13.5.3 Management of Difficult-to-Sedate Patients",
                        "13.5.4 Appropriate Use and Monitoring of Neuromuscular Blockade"
                    ]
                },
                {
                    "lesson_title": "13.6 Nutritional Therapy Implementation and Monitoring",
                    "sub_points": [
                        "13.6.1 Calculating Nutritional Requirements in Various Disease States",
                        "13.6.2 Optimizing Enteral Nutrition Delivery and Managing Intolerance",
                        "13.6.3 Parenteral Nutrition: Formulation, Administration, and Complication Management",
                        "13.6.4 Monitoring Efficacy and Complications of Nutritional Support"
                    ]
                },
                {
                    "lesson_title": "13.7 Temperature Management Interventions",
                    "sub_points": [
                        "13.7.1 Therapeutic Hypothermia/Targeted Temperature Management: Protocols and Devices",
                        "13.7.2 Management of Fever in Critically Ill Patients",
                        "13.7.3 Rewarming Techniques after Hypothermia"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 14: Practical Procedures (CoBaTrICE Domain 5)",
            "lessons": [
                {
                    "lesson_title": "14.1 Advanced Airway Management Procedures",
                    "sub_points": [
                        "14.1.1 Orotracheal and Nasotracheal Intubation Techniques",
                        "14.1.2 Difficult Airway Management Algorithms and Devices (e.g., Videolaryngoscopy, Fiberoptic Intubation)",
                        "14.1.3 Surgical Airway: Cricothyroidotomy and Tracheostomy (Indications, Techniques, Care)",
                        "14.1.4 Extubation Procedures and Management of Complications",
                        "14.1.5 Diagnostic and Therapeutic Bronchoscopy in ICU"
                    ]
                },
                {
                    "lesson_title": "14.2 Vascular Access Procedures",
                    "sub_points": [
                        "14.2.1 Peripheral Venous Cannulation (including Ultrasound-Guided)",
                        "14.2.2 Central Venous Catheterization (Internal Jugular, Subclavian, Femoral - Ultrasound-Guided, Landmark)",
                        "14.2.3 Arterial Cannulation (Radial, Femoral - Ultrasound-Guided, Landmark)",
                        "14.2.4 Pulmonary Artery Catheter Insertion",
                        "14.2.5 Intraosseous Access"
                    ]
                },
                {
                    "lesson_title": "14.3 Thoracic Procedures",
                    "sub_points": [
                        "14.3.1 Thoracentesis (Diagnostic and Therapeutic)",
                        "14.3.2 Chest Drain Insertion (Intercostal Catheter for Pneumothorax/Effusion/Empyema)",
                        "14.3.3 Needle Decompression for Tension Pneumothorax",
                        "14.3.4 Pericardiocentesis (Indications, Ultrasound Guidance, Technique)"
                    ]
                },
                {
                    "lesson_title": "14.4 Gastrointestinal Procedures (Bedside)",
                    "sub_points": [
                        "14.4.1 Nasogastric and Orogastric Tube Insertion and Confirmation",
                        "14.4.2 Placement of Post-Pyloric Feeding Tubes (Bedside techniques)",
                        "14.4.3 Paracentesis (Abdominal)"
                    ]
                },
                {
                    "lesson_title": "14.5 Neurological Procedures (Bedside)",
                    "sub_points": [
                        "14.5.1 Lumbar Puncture: Indications, Technique, Contraindications",
                        "14.5.2 ICP Monitor Insertion (External Ventricular Drain - EVD, Intraparenchymal Bolt) - Assisting/Understanding Principles"
                    ]
                },
                {
                    "lesson_title": "14.6 Other Essential ICU Procedures",
                    "sub_points": [
                        "14.6.1 Point-of-Care Ultrasound (POCUS) - Application in Procedures",
                        "14.6.2 Basic Suturing and Wound Care",
                        "14.6.3 Continuous Renal Replacement Therapy (CRRT) machine setup and basic troubleshooting"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 15: Peri-Operative Care (CoBaTrICE Domain 6)",
            "lessons": [
                {
                    "lesson_title": "15.1 Pre-operative Risk Assessment and Optimization",
                    "sub_points": [
                        "15.1.1 Identifying High-Risk Surgical Patients",
                        "15.1.2 Cardiovascular and Respiratory Risk Stratification",
                        "15.1.3 Pre-operative Optimization Strategies (e.g., Anemia, Nutrition, Glycemic Control)",
                        "15.1.4 Shared Decision Making and Consent in High-Risk Surgery"
                    ]
                },
                {
                    "lesson_title": "15.2 Intra-operative Considerations for Critically Ill Patients",
                    "sub_points": [
                        "15.2.1 Anesthetic Considerations in Patients with Organ Dysfunction",
                        "15.2.2 Hemodynamic and Ventilatory Management During Surgery for ICU Patients",
                        "15.2.3 Damage Control Surgery Principles"
                    ]
                },
                {
                    "lesson_title": "15.3 Post-operative Management of High-Risk Surgical Patients",
                    "sub_points": [
                        "15.3.1 Routine Post-operative ICU Admission Criteria and Care Bundles",
                        "15.3.2 Early Goal-Directed Therapy (EGDT) in Post-operative Setting - Evidence",
                        "15.3.3 Enhanced Recovery After Surgery (ERAS) Protocols and ICU Role"
                    ]
                },
                {
                    "lesson_title": "15.4 Specific Post-operative Scenarios",
                    "sub_points": [
                        "15.4.1 Post-Cardiac Surgery Management (Reiteration with peri-op focus)",
                        "15.4.2 Post-Thoracic Surgery (Lung Resection, Esophagectomy) Management",
                        "15.4.3 Post-Major Abdominal Surgery Management",
                        "15.4.4 Post-Neurosurgery Management",
                        "15.4.5 Post-Transplant (Solid Organ) ICU Management"
                    ]
                },
                {
                    "lesson_title": "15.5 Management of Common Post-operative Complications",
                    "sub_points": [
                        "15.5.1 Post-operative Bleeding and Coagulopathy",
                        "15.5.2 Post-operative Respiratory Failure and ARDS",
                        "15.5.3 Post-operative Acute Kidney Injury (AKI)",
                        "15.5.4 Post-operative Infections and Sepsis",
                        "15.5.5 Post-operative Delirium and Cognitive Dysfunction",
                        "15.5.6 Post-operative Ileus and GI Dysfunction"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 16: Comfort and Recovery (CoBaTrICE Domain 7)",
            "lessons": [
                {
                    "lesson_title": "16.1 Comprehensive Pain Management in the ICU",
                    "sub_points": [
                        "16.1.1 Pain Assessment in Verbal and Non-Verbal Patients (e.g., BPS, CPOT)",
                        "16.1.2 Pharmacological Pain Management: Opioids, Non-Opioids, Adjuvants",
                        "16.1.3 Regional Analgesia Techniques (e.g., Epidurals, Nerve Blocks - Principles)",
                        "16.1.4 Non-Pharmacological Pain Interventions"
                    ]
                },
                {
                    "lesson_title": "16.2 Sedation Management and Agitation Control",
                    "sub_points": [
                        "16.2.1 Sedation Assessment Scales (e.g., RASS, SAS)",
                        "16.2.2 Goals of Sedation: Light vs. Deep Sedation Strategies",
                        "16.2.3 Choice of Sedative Agents (Propofol, Benzodiazepines, Dexmedetomidine)",
                        "16.2.4 Sedation Interruption / Spontaneous Awakening Trials (SAT)",
                        "16.2.5 Management of Agitation and Aggression"
                    ]
                },
                {
                    "lesson_title": "16.3 Delirium Prevention and Management Strategies",
                    "sub_points": [
                        "16.3.1 Delirium Screening and Assessment (e.g., CAM-ICU, ICDSC)",
                        "16.3.2 Risk Factor Modification and Non-Pharmacological Prevention (ABCDEF Bundle)",
                        "16.3.3 Pharmacological Management of Delirium (Limited Role, Specific Indications)"
                    ]
                },
                {
                    "lesson_title": "16.4 Sleep Promotion in the ICU",
                    "sub_points": [
                        "16.4.1 Factors Affecting Sleep in ICU",
                        "16.4.2 Strategies to Improve Sleep Quality (Environmental, Non-Pharmacological, Pharmacological)"
                    ]
                },
                {
                    "lesson_title": "16.5 Early Mobilization and Rehabilitation in Critical Illness",
                    "sub_points": [
                        "16.5.1 Benefits of Early Mobilization",
                        "16.5.2 Safety Criteria and Protocols for Mobilization",
                        "16.5.3 Multidisciplinary Team Approach to ICU Rehabilitation"
                    ]
                },
                {
                    "lesson_title": "16.6 Psychological Support for Patients and Families",
                    "sub_points": [
                        "16.6.1 Recognizing Psychological Distress in Patients (Anxiety, Depression)",
                        "16.6.2 Communication Strategies to Support Patients",
                        "16.6.3 Supporting Families of Critically Ill Patients (Needs, Communication, Involvement)"
                    ]
                },
                {
                    "lesson_title": "16.7 Addressing Post-Intensive Care Syndrome (PICS)",
                    "sub_points": [
                        "16.7.1 Components of PICS (Physical, Cognitive, Mental Health Impairments)",
                        "16.7.2 Risk Factors for PICS",
                        "16.7.3 Strategies for Mitigation and Follow-up (PICS-F for families)"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 17: End-of-Life Care (CoBaTrICE Domain 8)",
            "lessons": [
                {
                    "lesson_title": "17.1 Ethical and Legal Principles in End-of-Life Decision Making",
                    "sub_points": [
                        "17.1.1 Concepts of Autonomy, Beneficence, Non-Maleficence, Justice in EoL Care",
                        "17.1.2 Determining Medical Futility",
                        "17.1.3 Advance Directives, Living Wills, and Surrogate Decision-Makers",
                        "17.1.4 Legal Frameworks Relevant to EoL Care (Varies by jurisdiction)"
                    ]
                },
                {
                    "lesson_title": "17.2 Communication in End-of-Life Care",
                    "sub_points": [
                        "17.2.1 Discussing Prognosis and Uncertainty",
                        "17.2.2 Establishing Goals of Care with Patients and Families",
                        "17.2.3 Conducting Family Conferences effectively",
                        "17.2.4 Managing Conflict and Disagreement in EoL Decisions"
                    ]
                },
                {
                    "lesson_title": "17.3 Withholding and Withdrawing Life-Sustaining Treatments",
                    "sub_points": [
                        "17.3.1 Ethical Justification and Process",
                        "17.3.2 Differences and Similarities: Withholding vs. Withdrawing",
                        "17.3.3 Common Life-Sustaining Treatments Considered (Ventilation, RRT, Vasoactives, Nutrition/Hydration)",
                        "17.3.4 Ensuring Comfort During and After Withdrawal of Treatment"
                    ]
                },
                {
                    "lesson_title": "17.4 Palliative Care Integration in the ICU",
                    "sub_points": [
                        "17.4.1 Principles of Palliative Care",
                        "17.4.2 Triggers for Palliative Care Consultation in ICU",
                        "17.4.3 Role of the Palliative Care Team",
                        "17.4.4 Concurrent Palliative Care with Curative Intent"
                    ]
                },
                {
                    "lesson_title": "17.5 Symptom Management at the End of Life",
                    "sub_points": [
                        "17.5.1 Managing Pain, Dyspnea, Agitation, Secretions",
                        "17.5.2 Pharmacological and Non-Pharmacological Approaches",
                        "17.5.3 Concept of Palliative Sedation"
                    ]
                },
                {
                    "lesson_title": "17.6 Care After Death and Organ Donation Process",
                    "sub_points": [
                        "17.6.1 Pronouncement of Death and Documentation",
                        "17.6.2 Bereavement Support for Families",
                        "17.6.3 Identifying Potential Organ Donors (Donation after Brain Death - DBD, Donation after Circulatory Death - DCD)",
                        "17.6.4 Approaching Families for Organ Donation Consent",
                        "17.6.5 Physiological Management of the Potential Organ Donor"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 18: Paediatric Care Principles for Adult Intensivists (CoBaTrICE Domain 9)",
            "lessons": [
                {
                    "lesson_title": "18.1 Recognition of the Critically Ill Child",
                    "sub_points": [
                        "18.1.1 Age-Specific Normal Vital Signs and Developmental Considerations",
                        "18.1.2 Paediatric Assessment Triangle (PAT)",
                        "18.1.3 Early Warning Signs of Deterioration in Children"
                    ]
                },
                {
                    "lesson_title": "18.2 Basic Paediatric Resuscitation and Emergency Management",
                    "sub_points": [
                        "18.2.1 Paediatric Basic Life Support (PBLS) and Advanced Life Support (PALS/APLS) Principles",
                        "18.2.2 Airway Management in Children (Anatomical Differences, Equipment)",
                        "18.2.3 Vascular Access in Children (IV, IO)",
                        "18.2.4 Management of Paediatric Shock and Respiratory Failure (Initial Steps)"
                    ]
                },
                {
                    "lesson_title": "18.3 Key Physiological Differences: Child vs. Adult",
                    "sub_points": [
                        "18.3.1 Respiratory System Differences and Implications for Ventilation",
                        "18.3.2 Cardiovascular System Differences",
                        "18.3.3 Renal and Metabolic Differences",
                        "18.3.4 Neurological Development and Assessment"
                    ]
                },
                {
                    "lesson_title": "18.4 Common Paediatric Critical Illnesses (Overview for non-specialists)",
                    "sub_points": [
                        "18.4.1 Severe Bronchiolitis and Asthma",
                        "18.4.2 Sepsis in Children",
                        "18.4.3 Paediatric Trauma Principles",
                        "18.4.4 Common Paediatric Poisonings (Brief Overview)"
                    ]
                },
                {
                    "lesson_title": "18.5 Fluid and Drug Dosing Considerations in Children",
                    "sub_points": [
                        "18.5.1 Weight-Based Calculations for Fluids and Medications",
                        "18.5.2 Common Paediatric Drug Formulations and Concentrations",
                        "18.5.3 Pharmacokinetic Differences in Children"
                    ]
                },
                {
                    "lesson_title": "18.6 Equipment and Monitoring in Paediatric Critical Care",
                    "sub_points": [
                        "18.6.1 Size-Appropriate Equipment (Airway, Catheters, Monitors)",
                        "18.6.2 Differences in Monitoring Techniques and Interpretation"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 19: Transport of the Critically Ill Patient (CoBaTrICE Domain 10)",
            "lessons": [
                {
                    "lesson_title": "19.1 Principles of Safe Critical Care Transport",
                    "sub_points": [
                        "19.1.1 Indications for Intra-hospital and Inter-hospital Transport",
                        "19.1.2 Risk Assessment and Benefit Analysis of Transport",
                        "19.1.3 Levels of Care during Transport"
                    ]
                },
                {
                    "lesson_title": "19.2 Pre-Transport Stabilization and Preparation",
                    "sub_points": [
                        "19.2.1 Comprehensive Patient Assessment and Stabilization Before Transport",
                        "19.2.2 Securing Airway, Ventilation, and Vascular Access",
                        "19.2.3 Communication and Handoff with Referring/Receiving Teams and Transport Team",
                        "19.2.4 Documentation and Checklists"
                    ]
                },
                {
                    "lesson_title": "19.3 Monitoring During Intra-hospital and Inter-hospital Transport",
                    "sub_points": [
                        "19.3.1 Essential Monitoring Parameters (ECG, SpO2, BP, ETCO2, Temperature)",
                        "19.3.2 Advanced Monitoring during Transport (e.g., Invasive pressures, Ventilator parameters)",
                        "19.3.3 Challenges of Monitoring in the Transport Environment"
                    ]
                },
                {
                    "lesson_title": "19.4 Equipment and Personnel Requirements for Transport",
                    "sub_points": [
                        "19.4.1 Essential Transport Equipment (Ventilator, Monitor/Defibrillator, Infusion Pumps, Suction, Oxygen)",
                        "19.4.2 Medications and Fluids for Transport",
                        "19.4.3 Composition and Training of the Critical Care Transport Team (Physician, Nurse, Respiratory Therapist)"
                    ]
                },
                {
                    "lesson_title": "19.5 Risks, Complications, and Mitigation Strategies During Transport",
                    "sub_points": [
                        "19.5.1 Physiological Deterioration (Hypotension, Hypoxia, Arrhythmias)",
                        "19.5.2 Equipment Malfunction or Failure",
                        "19.5.3 Loss of Access (Airway, IV lines)",
                        "19.5.4 Environmental Factors (Motion, Noise, Temperature)"
                    ]
                },
                {
                    "lesson_title": "19.6 Specific Considerations in Transport",
                    "sub_points": [
                        "19.6.1 Transport of the Mechanically Ventilated Patient",
                        "19.6.2 Transport of Patients with Neurological Emergencies (e.g., Raised ICP)",
                        "19.6.3 Transport of Patients on Vasoactive Infusions",
                        "19.6.4 Aeromedical Transport Principles",
                        "19.6.5 Transport of Patients on ECMO (Specialized teams)"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 20: Patient Safety and Health Systems Management (CoBaTrICE Domain 11)",
            "lessons": [
                {
                    "lesson_title": "20.1 Principles of Patient Safety in the ICU",
                    "sub_points": [
                        "20.1.1 Understanding Medical Errors and Systems Thinking (Swiss Cheese Model)",
                        "20.1.2 Creating a Culture of Safety (Reporting, Just Culture)",
                        "20.1.3 Human Factors Engineering in ICU Design and Processes"
                    ]
                },
                {
                    "lesson_title": "20.2 Infection Prevention and Control Strategies",
                    "sub_points": [
                        "20.2.1 Hand Hygiene",
                        "20.2.2 Standard and Transmission-Based Precautions (Contact, Droplet, Airborne)",
                        "20.2.3 Prevention of Catheter-Related Bloodstream Infections (CRBSI)",
                        "20.2.4 Prevention of Ventilator-Associated Pneumonia (VAP)",
                        "20.2.5 Prevention of Catheter-Associated Urinary Tract Infections (CAUTI)",
                        "20.2.6 Antimicrobial Stewardship Programs"
                    ]
                },
                {
                    "lesson_title": "20.3 Medication Safety in the ICU",
                    "sub_points": [
                        "20.3.1 High-Alert Medications in ICU",
                        "20.3.2 Preventing Medication Errors (Prescribing, Dispensing, Administration, Monitoring)",
                        "20.3.3 Reconciliation of Medications",
                        "20.3.4 Smart Pump Technology and Other Safety Tools"
                    ]
                },
                {
                    "lesson_title": "20.4 Preventing Other ICU-Acquired Complications",
                    "sub_points": [
                        "20.4.1 Venous Thromboembolism (VTE) Prophylaxis",
                        "20.4.2 Stress Ulcer Prophylaxis (Indications)",
                        "20.4.3 Prevention of Pressure Injuries (Skin Care, Positioning)",
                        "20.4.4 Delirium Prevention (Reiteration with safety focus)",
                        "20.4.5 ICU-Acquired Weakness Prevention (Early Mobilization)"
                    ]
                },
                {
                    "lesson_title": "20.5 Quality Improvement (QI) Methodologies in Intensive Care",
                    "sub_points": [
                        "20.5.1 QI Models (e.g., PDSA - Plan-Do-Study-Act)",
                        "20.5.2 Use of Clinical Audits and Benchmarking",
                        "20.5.3 Developing and Implementing Care Bundles and Protocols",
                        "20.5.4 Measuring Quality: Structure, Process, and Outcome Indicators"
                    ]
                },
                {
                    "lesson_title": "20.6 Teamwork, Communication, and Handovers",
                    "sub_points": [
                        "20.6.1 Principles of Effective Team Communication (e.g., SBAR, Closed-Loop Communication)",
                        "20.6.2 Structured Handovers/Handoffs",
                        "20.6.3 Multidisciplinary Rounds and Care Planning",
                        "20.6.4 Crisis Resource Management (CRM) Principles"
                    ]
                },
                {
                    "lesson_title": "20.7 Managing Adverse Events and Critical Incidents",
                    "sub_points": [
                        "20.7.1 Incident Reporting Systems",
                        "20.7.2 Root Cause Analysis (RCA) and Morbidity & Mortality (M&M) Reviews",
                        "20.7.3 Disclosure of Medical Errors (Open Disclosure)"
                    ]
                },
                {
                    "lesson_title": "20.8 Understanding and Using ICU Scoring Systems for Quality Assessment",
                    "sub_points": [
                        "20.8.1 Common Scoring Systems (APACHE, SAPS, SOFA) - Strengths and Limitations",
                        "20.8.2 Risk Adjustment and Performance Monitoring",
                        "20.8.3 Use in Research vs. Individual Patient Prognostication"
                    ]
                },
                {
                    "lesson_title": "20.9 Resource Management and Allocation in the ICU",
                    "sub_points": [
                        "20.9.1 Principles of Fair Allocation of Scarce Resources",
                        "20.9.2 Cost-Effectiveness in Critical Care",
                        "20.9.3 ICU Staffing Models and Workload Management"
                    ]
                }
            ]
        },
        {
            "chapter_title": "Chapter 21: Professionalism in Intensive Care (CoBaTrICE Domain 12)",
            "lessons": [
                {
                    "lesson_title": "21.1 Ethical Principles in Intensive Care Practice",
                    "sub_points": [
                        "21.1.1 Deep Dive into Autonomy, Beneficence, Non-Maleficence, Justice",
                        "21.1.2 Veracity and Fidelity in Patient Care",
                        "21.1.3 Managing Ethical Dilemmas in the ICU (Frameworks for decision making)",
                        "21.1.4 Role of Ethics Committees"
                    ]
                },
                {
                    "lesson_title": "21.2 Legal Aspects Relevant to Intensive Care",
                    "sub_points": [
                        "21.2.1 Informed Consent and Capacity Assessment",
                        "21.2.2 Confidentiality and Data Protection (e.g., GDPR/HIPAA principles)",
                        "21.2.3 Medical Negligence and Malpractice Considerations",
                        "21.2.4 Legal Aspects of End-of-Life Care and Brain Death Certification",
                        "21.2.5 Professional Regulation and Accountability"
                    ]
                },
                {
                    "lesson_title": "21.3 Advanced Communication Skills",
                    "sub_points": [
                        "21.3.1 Communicating Bad News and Prognosis",
                        "21.3.2 Conducting Difficult Conversations with Families and Patients",
                        "21.3.3 Conflict Resolution Strategies (with families, within the team)",
                        "21.3.4 Cross-Cultural Communication and Sensitivity"
                    ]
                },
                {
                    "lesson_title": "21.4 Interprofessional Collaboration and Team Dynamics",
                    "sub_points": [
                        "21.4.1 Understanding Roles and Responsibilities within the ICU Team",
                        "21.4.2 Fostering Mutual Respect and Effective Teamwork",
                        "21.4.3 Leadership Skills in the ICU Setting",
                        "21.4.4 Managing Interpersonal Conflicts within the Team"
                    ]
                },
                {
                    "lesson_title": "21.5 Professional Wellbeing: Stress, Burnout, and Resilience",
                    "sub_points": [
                        "21.5.1 Recognizing Symptoms of Stress, Burnout, and Compassion Fatigue",
                        "21.5.2 Individual Strategies for Stress Management and Resilience Building",
                        "21.5.3 System-Level Interventions to Promote Wellbeing in ICU Staff",
                        "21.5.4 Seeking and Providing Peer Support"
                    ]
                },
                {
                    "lesson_title": "21.6 Lifelong Learning, Teaching, and Evidence-Based Practice",
                    "sub_points": [
                        "21.6.1 Maintaining Clinical Competence and Continuing Professional Development (CPD)",
                        "21.6.2 Principles of Adult Learning and Effective Teaching in ICU (Bedside, Didactic)",
                        "21.6.3 Critically Appraising Medical Literature (Evidence-Based Medicine)",
                        "21.6.4 Implementing Evidence into Clinical Practice"
                    ]
                },
                {
                    "lesson_title": "21.7 Research Ethics and Conduct in Critical Care",
                    "sub_points": [
                        "21.7.1 Ethical Principles of Research Involving Critically Ill Patients",
                        "21.7.2 Informed Consent in Research (including waiver of consent, deferred consent)",
                        "21.7.3 Good Clinical Practice (GCP) in Research",
                        "21.7.4 Understanding and Participating in Clinical Trials"
                    ]
                }
            ]
        }
    ]

    # Combine all chapter data
    all_icu_data = icu_data_chapters_1_12 + other_domains_icu_data

    if not all_icu_data:
        return None, None, None

    # 1. Randomly select a chapter (excluding those in exclude_chapters)
    current_pool = all_icu_data
    if exclude_chapters:
        filtered = [ch for ch in all_icu_data if ch["chapter_title"] not in exclude_chapters]
        if filtered:
            current_pool = filtered

    selected_chapter_data = random.choice(current_pool)
    chapter_title = selected_chapter_data["chapter_title"]

    if not selected_chapter_data.get("lessons") or not selected_chapter_data["lessons"]:
        return chapter_title, None, None # Chapter might have no lessons

    # 2. Randomly select a main lesson from that chapter
    selected_lesson_data = random.choice(selected_chapter_data["lessons"])
    lesson_title = selected_lesson_data["lesson_title"]

    if not selected_lesson_data.get("sub_points") or not selected_lesson_data["sub_points"]:
        return chapter_title, lesson_title, None # Lesson might have no sub-points

    # 3. Randomly select a sub-point from that main lesson
    selected_sub_point = random.choice(selected_lesson_data["sub_points"])

    return chapter_title, lesson_title, selected_sub_point


def get_random_aspect(exclude_chapters=None):
    """
    Returns a formatted string with a random chapter, lesson, and sub-point.
    Optionally excludes a list of chapter titles.
    """
    result = get_random_icu_chapter_and_lesson(exclude_chapters=exclude_chapters)
    if result == (None, None, None):
        return "No ICU data available."
    
    chapter_title, lesson_title, sub_point = result
    
    if chapter_title is None:
        return "No ICU chapter data available."
    if lesson_title is None:
        return f"{chapter_title}\n(No lessons available for this chapter)"
    if sub_point is None:
        return f"{chapter_title}\n{lesson_title}\n(No sub-points available for this lesson)"
    
    return f"{chapter_title}\n{lesson_title}\n{sub_point}"


