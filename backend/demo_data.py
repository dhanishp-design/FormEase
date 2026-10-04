from typing import Dict, Any, List

DEMO_FORM_DATA: Dict[str, Any] = {
    "form_id": "demo-scholarship-form",
    "form_title": "National Post-Matric Scholarship Application Form 2024-25",
    "purpose": "Financial scholarship grant for post-matriculation higher education students under the Direct Benefit Transfer (DBT) scheme.",
    "organization": "National Scholarship Portal, Ministry of Social Justice & Empowerment, Government of India",
    "summary": "Official student scholarship form requiring personal identification, domicile verification, family income declarations, and bank details for direct benefit transfer (DBT).",
    "total_fields": 12,
    "required_fields_count": 9,
    "optional_fields_count": 3,
    "overall_confidence": 0.94,
    "language": "en",
    "is_demo": True,
    "instructions": [
        {"text": "Fill all mandatory details marked with an asterisk (*). Use CAPITAL LETTERS in Black/Blue ink only.", "page": 1, "importance": "high"},
        {"text": "Applicant must be between 18 and 35 years of age as on 01/08/2024.", "page": 1, "importance": "high"},
        {"text": "Annual Family Income must be reported in INR for the preceding financial year.", "page": 1, "importance": "high"},
        {"text": "Bank account must be Aadhaar-seeded for Direct Benefit Transfer (DBT).", "page": 1, "importance": "high"}
    ],
    "sections": [
        {"id": "sec_1", "name": "1. Personal Information", "page": 1},
        {"id": "sec_2", "name": "2. Family & Income Information", "page": 1},
        {"id": "sec_3", "name": "3. Domicile & Residence", "page": 1},
        {"id": "sec_4", "name": "4. Direct Benefit Transfer (DBT) Bank Details", "page": 1},
        {"id": "sec_5", "name": "5. Declaration & Undertaking", "page": 1}
    ],
    "fields": [
        {
            "id": "field_001",
            "name": "Full Name",
            "label": "Full Name (as in SSC Marks)",
            "type": "text",
            "required": True,
            "page": 1,
            "section": "1. Personal Information",
            "what_document_says": "Full Name (as in SSC Marks). Use CAPITAL LETTERS only. Do not add Mr., Ms., or Shri.",
            "what_it_means": "Enter your complete legal name exactly as recorded on your 10th standard certificate or official government ID.",
            "what_user_should_provide": "Your First Name, Middle Name, and Surname in capital letters.",
            "expected_format": "CAPITAL LETTERS (e.g. PRIYA RAMESH SHARMA)",
            "example_from_document": "PRIYA RAMESH SHARMA",
            "validation_rules": ["non_empty", "uppercase"],
            "explanation": "Enter your complete legal name exactly as it appears on your 10th Standard / SSC certificate or official government ID.",
            "what_to_enter": "Your First Name, Middle Name, and Surname in capital letters. Do not add salutations like Mr., Ms., or Shri.",
            "example": "PRIYA RAMESH SHARMA",
            "confidence": 0.98,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 19.5, "width": 45.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "पूरा नाम (10वीं कक्षा के प्रमाणपत्र के अनुसार)। केवल बड़े अक्षरों का प्रयोग करें।",
                    "what_it_means": "अपना पूरा कानूनी नाम ठीक वैसे ही दर्ज करें जैसा आपके 10वीं कक्षा के प्रमाणपत्र या सरकारी पहचान पत्र पर है।",
                    "explanation": "अपना पूरा कानूनी नाम ठीक वैसे ही दर्ज करें जैसा आपके 10वीं कक्षा के प्रमाणपत्र या सरकारी पहचान पत्र पर है।",
                    "what_to_enter": "प्रथम नाम, मध्य नाम और उपनाम बड़े अक्षरों (Capital Letters) में लिखें। श्री, सुश्री आदि न लगाएं।",
                    "example": "प्रिया रमेश शर्मा"
                },
                "mr": {
                    "what_document_says": "पूर्ण नाव (१० वीच्या गुणपत्रकानुसार). फक्त मोठ्या अक्षरांमध्ये लिहा.",
                    "what_it_means": "तुमचे पूर्ण कायदेशीर नाव तुमच्या १० वीच्या प्रमाणपत्रावर किंवा अधिकृत ओळखपत्रावर असल्याप्रमाणेच प्रविष्ट करा.",
                    "explanation": "तुमचे पूर्ण कायदेशीर नाव तुमच्या १० वीच्या प्रमाणपत्रावर किंवा अधिकृत ओळखपत्रावर असल्याप्रमाणेच प्रविष्ट करा.",
                    "what_to_enter": "पहिले नाव, मधले नाव आणि आडनाव इंग्रजी मोठ्या अक्षरांमध्ये लिहा. श्री, कु. अशी पदवी जोडू नका.",
                    "example": "प्रिया रमेश शर्मा"
                }
            }
        },
        {
            "id": "field_002",
            "name": "Date of Birth",
            "label": "Date of Birth (DD/MM/YYYY)",
            "type": "date",
            "required": True,
            "page": 1,
            "section": "1. Personal Information",
            "what_document_says": "Applicant must be between 18 and 35 years as on 01/08/2024. Date format: DD/MM/YYYY.",
            "what_it_means": "The official date on which you were born, used to verify age eligibility criteria (18 to 35 years).",
            "what_user_should_provide": "Day, Month, and Year in DD/MM/YYYY format matching your birth certificate or SSC marksheet.",
            "expected_format": "DD/MM/YYYY (e.g. 15/08/2004)",
            "min_value": "18 years",
            "max_value": "35 years",
            "validation_rules": ["date_format_ddmmyyyy", "age_between_18_35"],
            "example_from_document": "15/08/2004",
            "explanation": "The official date on which you were born, used to verify age eligibility criteria for this scholarship.",
            "what_to_enter": "Day, Month, and Year in DD/MM/YYYY format matching your birth certificate or SSC marksheet.",
            "example": "15/08/2004",
            "confidence": 0.96,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 24.8, "width": 24.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "आवेदक की आयु 01/08/2024 को 18 से 35 वर्ष के बीच होनी चाहिए। प्रारूप: DD/MM/YYYY.",
                    "what_it_means": "आपकी आधिकारिक जन्म तिथि, जिसका उपयोग छात्रवृत्ति के लिए आयु पात्रता (18 से 35 वर्ष) की पुष्टि करने के लिए किया जाता है।",
                    "explanation": "आपकी आधिकारिक जन्म तिथि, जिसका उपयोग छात्रवृत्ति के लिए आयु पात्रता की पुष्टि करने के लिए किया जाता है।",
                    "what_to_enter": "दिन, माह और वर्ष DD/MM/YYYY प्रारूप में दर्ज करें।",
                    "example": "15/08/2004"
                },
                "mr": {
                    "what_document_says": "अर्जदाराचे वय ०१/०८/२०२४ रोजी १८ ते ३५ वर्षांच्या दरम्यान असावे. स्वरूप: DD/MM/YYYY.",
                    "what_it_means": "तुमची अधिकृत जन्मतारीख, जी शिष्यवृत्तीसाठी वयोमर्यादा (१८ ते ३५ वर्षे) पडताळण्यासाठी वापरली जाते.",
                    "explanation": "तुमची अधिकृत जन्मतारीख, जी शिष्यवृत्तीसाठी वयोमर्यादा पडताळण्यासाठी वापरली जाते.",
                    "what_to_enter": "DD/MM/YYYY या स्वरूपात दिवस, महिना आणि वर्ष प्रविष्ट करा.",
                    "example": "15/08/2004"
                }
            }
        },
        {
            "id": "field_003",
            "name": "Annual Family Income",
            "label": "Annual Family Income (in INR)",
            "type": "currency",
            "required": True,
            "page": 1,
            "section": "2. Family & Income Information",
            "what_document_says": "Annual family income during the preceding financial year. Amount must be entered in INR.",
            "what_it_means": "The form asks for your family's total annual income for the previous financial year in Indian Rupees.",
            "what_user_should_provide": "Total combined gross income of all earning family members earned in the previous financial year in INR.",
            "expected_format": "INR (Indian Rupees, e.g. ₹4,80,000)",
            "example_from_document": "₹4,80,000",
            "validation_rules": ["currency_inr", "positive_number"],
            "explanation": "The combined gross income earned by all earning family members (parents/guardians) from all sources in one financial year.",
            "what_to_enter": "Total annual income in Indian Rupees. Must match the competent revenue authority income certificate (Tehsildar/SDM).",
            "example": "₹4,80,000",
            "confidence": 0.94,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 30.5, "width": 30.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "पूर्ववर्ती वित्तीय वर्ष के दौरान वार्षिक पारिवारिक आय। राशि भारतीय रुपयों (INR) में दर्ज की जानी चाहिए।",
                    "what_it_means": "यह फॉर्म पिछले वित्तीय वर्ष के लिए आपके परिवार की कुल वार्षिक आय भारतीय रुपयों में मांगता है।",
                    "explanation": "एक वित्तीय वर्ष में सभी स्रोतों से आपके परिवार (माता-पिता/अभिभावक) द्वारा अर्जित कुल वार्षिक आय।",
                    "what_to_enter": "तहसीलदार या सक्षम राजस्व अधिकारी द्वारा जारी आय प्रमाण पत्र के अनुसार कुल वार्षिक आय।",
                    "example": "₹4,80,000"
                },
                "mr": {
                    "what_document_says": "मागील आर्थिक वर्षातील कुटुंबाचे वार्षिक उत्पन्न. रक्कम भारतीय रुपयांमध्ये (INR) भरणे अनिवार्य आहे.",
                    "what_it_means": "हा अर्ज मागील आर्थिक वर्षातील तुमच्या कुटुंबाचे एकूण वार्षिक एकत्रित उत्पन्न भारतीय रुपयांमध्ये विचारत आहे.",
                    "explanation": "एका आर्थिक वर्षात सर्व स्त्रोतांकडून तुमच्या कुटुंबातील सर्व कमवत्या सदस्यांनी मिळवलेले एकूण एकत्रित वार्षिक उत्पन्न.",
                    "what_to_enter": "तहसीलदार किंवा सक्षम प्राधिकरणाने दिलेल्या उत्पन्न प्रमाणपत्राशी जुळणारे एकूण वार्षिक उत्पन्न रुपयात लिहा.",
                    "example": "₹4,80,000"
                }
            }
        },
        {
            "id": "field_004",
            "name": "Category / Caste",
            "label": "Category (General/OBC/SC/ST/EWS)",
            "type": "dropdown",
            "required": True,
            "page": 1,
            "section": "1. Personal Information",
            "what_document_says": "Select constitutional category. Valid caste certificate required for SC/ST/OBC.",
            "what_it_means": "Your constitutional social category required to determine specific category reservation quotas.",
            "what_user_should_provide": "Select your exact category matching your registered caste certificate.",
            "allowed_values": ["General", "OBC (Non-Creamy)", "SC", "ST", "EWS"],
            "expected_format": "Select from allowed options",
            "example_from_document": "OBC (Non-Creamy)",
            "validation_rules": ["must_be_in_allowed_values"],
            "explanation": "Your constitutional social category (General / OBC / SC / ST / EWS) required to determine specific category reservation quotas.",
            "what_to_enter": "Select your exact category. If applying under reserved categories (SC/ST/OBC), you must possess a valid Caste Certificate.",
            "example": "OBC (Non-Creamy Layer)",
            "confidence": 0.92,
            "sensitive": False,
            "bbox": {"x": 58.0, "y": 24.8, "width": 28.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "संवैधानिक श्रेणी चुनें। आरक्षित श्रेणी (SC/ST/OBC) के लिए वैध जाति प्रमाण पत्र आवश्यक है।",
                    "what_it_means": "आपकी सामाजिक श्रेणी जो छात्रवृत्ति कोटा और पात्रता के लिए आवश्यक है।",
                    "explanation": "आपकी सामाजिक श्रेणी (General / OBC / SC / ST / EWS) जो छात्रवृत्ति कोटा और पात्रता के लिए आवश्यक है।",
                    "what_to_enter": "अपनी सही श्रेणी चुनें। आरक्षित श्रेणी के लिए वैध जाति प्रमाण पत्र आवश्यक है।",
                    "example": "OBC (Non-Creamy Layer)"
                },
                "mr": {
                    "what_document_says": "संवैधानिक प्रवर्ग निवडा. SC/ST/OBC प्रवर्गासाठी वैध जात प्रमाणपत्र आवश्यक आहे.",
                    "what_it_means": "तुमचा सामाजिक प्रवर्ग जो शिष्यवृत्ती सवलतींसाठी आवश्यक असतो.",
                    "explanation": "तुमचा सामाजिक प्रवर्ग (General / OBC / SC / ST / EWS) जो शिष्यवृत्ती सवलतींसाठी आवश्यक असतो.",
                    "what_to_enter": "तुमचा अधिकृत प्रवर्ग निवडा. राखीव प्रवर्गासाठी वैध जात प्रमाणपत्र आवश्यक आहे.",
                    "example": "OBC (Non-Creamy Layer)"
                }
            }
        },
        {
            "id": "field_005",
            "name": "Domicile State",
            "label": "Domicile State (Attach Certificate)",
            "type": "dropdown",
            "required": True,
            "page": 1,
            "section": "3. Domicile & Residence",
            "what_document_says": "Attach valid Domicile Certificate issued by competent Revenue Authority.",
            "what_it_means": "The Indian State or Union Territory where you are officially and legally recognized as a permanent resident.",
            "what_user_should_provide": "The state where you or your parents hold a registered Domicile / Residence Certificate.",
            "allowed_values": ["Maharashtra", "Karnataka", "Delhi", "Gujarat", "Uttar Pradesh", "Other"],
            "expected_format": "State name",
            "example_from_document": "Maharashtra",
            "validation_rules": ["must_be_in_allowed_values"],
            "explanation": "The Indian State or Union Territory where you are officially and legally recognized as a permanent resident.",
            "what_to_enter": "The state where you or your parents hold a registered Domicile / Residence Certificate.",
            "example": "Maharashtra",
            "confidence": 0.95,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 36.2, "width": 30.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "सक्षम राजस्व प्राधिकारी द्वारा जारी वैध अधिवास (Domicile) प्रमाण पत्र संलग्न करें।",
                    "what_it_means": "वह भारतीय राज्य जहां आप आधिकारिक रूप से स्थायी निवासी (Domicile) हैं।",
                    "explanation": "वह भारतीय राज्य या केंद्र शासित प्रदेश जहां आप आधिकारिक रूप से स्थायी निवासी (Domicile) हैं।",
                    "what_to_enter": "उस राज्य का नाम जहां का आपके पास अधिवास (Domicile) प्रमाण पत्र है।",
                    "example": "महाराष्ट्र"
                },
                "mr": {
                    "what_document_says": "सक्षम महसूल प्राधिकरणाने दिलेले वैध अधिवास (Domicile) प्रमाणपत्र जोडा.",
                    "what_it_means": "तुम्ही ज्या भारतीय राज्याचे अधिकृत कायमस्वरूपी रहिवासी आहात ते राज्य.",
                    "explanation": "तुम्ही ज्या भारतीय राज्याचे किंवा केंद्रशासित प्रदेशाचे अधिकृत कायमस्वरूपी रहिवासी आहात ते राज्य.",
                    "what_to_enter": "ज्या राज्याचे तुमचे अधिवास (Domicile) प्रमाणपत्र आहे त्या राज्याचे नाव निवडा.",
                    "example": "महाराष्ट्र"
                }
            }
        },
        {
            "id": "field_006",
            "name": "Mobile Number",
            "label": "Mobile Number (10 digits linked to Aadhaar)",
            "type": "phone",
            "required": True,
            "page": 1,
            "section": "1. Personal Information",
            "what_document_says": "Enter a 10-digit mobile number linked to Aadhaar for OTP verification.",
            "what_it_means": "An active, personal 10-digit mobile number for scholarship status alerts and OTP validation.",
            "what_user_should_provide": "10-digit Indian mobile number without +91 or leading 0.",
            "expected_format": "10 digits (e.g. 9820154321)",
            "example_from_document": "9820154321",
            "validation_rules": ["10_digits_required", "numeric_only"],
            "explanation": "An active, personal 10-digit mobile number for scholarship status alerts, application OTPs, and verification SMS.",
            "what_to_enter": "10-digit Indian mobile number without +91 or leading 0. Must be linked to Aadhaar for DBT verification.",
            "example": "9820154321",
            "confidence": 0.99,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 42.0, "width": 26.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "OTP सत्यापन के लिए आधार से जुड़ा 10 अंकों का मोबाइल नंबर दर्ज करें।",
                    "what_it_means": "एक सक्रिय 10 अंकों का मोबाइल नंबर जिस पर छात्रवृत्ति के अपडेट और OTP भेजे जा सकें।",
                    "explanation": "एक सक्रिय 10 अंकों का मोबाइल नंबर जिस पर छात्रवृत्ति के अपडेट और OTP भेजे जा सकें।",
                    "what_to_enter": "+91 या 0 लगाए बिना 10 अंकों का मोबाइल नंबर। यह आधार से लिंक होना चाहिए।",
                    "example": "9820154321"
                },
                "mr": {
                    "what_document_says": "OTP पडताळणीसाठी आधारशी जोडलेला १० अंकी मोबाईल नंबर प्रविष्ट करा.",
                    "what_it_means": "शिष्यवृत्तीचे संदेश, OTP आणि अपडेट्स मिळण्यासाठी चालू असलेला १० अंकी मोबाईल क्रमांक.",
                    "explanation": "शिष्यवृत्तीचे संदेश, OTP आणि अपडेट्स मिळण्यासाठी चालू असलेला १० अंकी मोबाईल क्रमांक.",
                    "what_to_enter": "+91 न लावता १० अंकी मोबाईल नंबर लिहा. हा नंबर आधार कार्डशी जोडलेला असावा.",
                    "example": "9820154321"
                }
            }
        },
        {
            "id": "field_007",
            "name": "Email Address",
            "label": "Email Address",
            "type": "email",
            "required": True,
            "page": 1,
            "section": "1. Personal Information",
            "what_document_says": "Valid email address for electronic correspondence and status receipts.",
            "what_it_means": "A valid email account where official application receipts and scholarship notices will be sent.",
            "what_user_should_provide": "Your active email address that you check regularly.",
            "expected_format": "email (e.g. name@domain.com)",
            "example_from_document": "priya.sharma@example.com",
            "validation_rules": ["valid_email_format"],
            "explanation": "A valid email account where official application receipts, verification notices, and scholarship award letters will be sent.",
            "what_to_enter": "Your personal active email address that you check regularly.",
            "example": "priya.sharma@example.com",
            "confidence": 0.97,
            "sensitive": False,
            "bbox": {"x": 58.0, "y": 42.0, "width": 34.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "इलेक्ट्रॉनिक पत्राचार और स्थिति रसीदों के लिए वैध ईमेल पता।",
                    "what_it_means": "एक वैध ईमेल पता जहां आवेदन रसीद और छात्रवृत्ति संबंधी सूचनाएं भेजी जाएंगी।",
                    "explanation": "एक वैध ईमेल पता जहां आवेदन रसीद और छात्रवृत्ति संबंधी सूचनाएं भेजी जाएंगी।",
                    "what_to_enter": "अपना व्यक्तिगत और सक्रिय ईमेल आईडी दर्ज करें।",
                    "example": "priya.sharma@example.com"
                },
                "mr": {
                    "what_document_says": "ईमेल संदेश आणि पावतीसाठी वैध ईमेल पत्ता.",
                    "what_it_means": "अधिकृत पावती आणि शिष्यवृत्ती संदर्भातील सूचना प्राप्त करण्यासाठी तुमचा वैध ईमेल पत्ता.",
                    "explanation": "अधिकृत पावती आणि शिष्यवृत्ती संदर्भातील सूचना प्राप्त करण्यासाठी तुमचा वैध ईमेल पत्ता.",
                    "what_to_enter": "नेहमी वापरात असलेला तुमचा ईमेल आयडी प्रविष्ट करा.",
                    "example": "priya.sharma@example.com"
                }
            }
        },
        {
            "id": "field_008",
            "name": "Permanent Residential Address",
            "label": "Permanent Address (with 6-digit PIN)",
            "type": "address",
            "required": True,
            "page": 1,
            "section": "3. Domicile & Residence",
            "what_document_says": "Full permanent residential postal address with mandatory 6-digit PIN code.",
            "what_it_means": "The full postal address of your permanent residence where you or your family permanently reside.",
            "what_user_should_provide": "House/Flat number, Street name, Locality, City, District, State, and 6-digit PIN Code.",
            "expected_format": "Full Postal Address with 6-digit PIN",
            "example_from_document": "Flat 402, Shivneri Heights, Senapati Bapat Road, Pune, Maharashtra - 411016",
            "validation_rules": ["must_contain_pincode"],
            "explanation": "The full postal address of your permanent residence where you or your family permanently reside.",
            "what_to_enter": "House/Flat number, Street name, Locality, City/Taluka, District, State, and 6-digit PIN Code.",
            "example": "Flat 402, Shivneri Heights, Senapati Bapat Road, Pune, Maharashtra - 411016",
            "confidence": 0.93,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 48.0, "width": 68.0, "height": 5.5},
            "translations": {
                "hi": {
                    "what_document_says": "अनिवार्य 6 अंकों के पिन कोड के साथ पूरा स्थायी आवासीय डाक पता।",
                    "what_it_means": "आपके स्थायी निवास का पूरा डाक पता जहां आपका परिवार स्थायी रूप से रहता है।",
                    "explanation": "आपके स्थायी निवास का पूरा डाक पता जहां आपका परिवार स्थायी रूप से रहता है।",
                    "what_to_enter": "मकान नंबर, सड़क, क्षेत्र, शहर, जिला, राज्य और 6 अंकों का पिन कोड लिखें।",
                    "example": "फ्लैट 402, शिवनेरी हाइट्स, सेनापती बापट रोड, पुणे, महाराष्ट्र - 411016"
                },
                "mr": {
                    "what_document_says": "अनिवार्य ६ अंकी पिन कोडसह संपूर्ण कायमचा निवासी पत्ता.",
                    "what_it_means": "तुमच्या कायमस्वरूपी घराचा संपूर्ण पत्ता जेथे तुमचे कुटुंब वास्तव्यास आहे.",
                    "explanation": "तुमच्या कायमस्वरूपी घराचा संपूर्ण पत्ता जेथे तुमचे कुटुंब वास्तव्यास आहे.",
                    "what_to_enter": "घर क्र., गल्ली/रस्ता, परिसर, शहर/तालुका, जिल्हा, राज्य आणि ६ अंकी पिन कोड प्रविष्ट करा.",
                    "example": "फ्लॅट ४०२, शिवनेरी हाइट्स, सेनापती बापट रोड, पुणे, महाराष्ट्र - ४११०१६"
                }
            }
        },
        {
            "id": "field_009",
            "name": "Bank Account Number",
            "label": "Bank Account Number (Aadhaar Seeded)",
            "type": "number",
            "required": True,
            "page": 1,
            "section": "4. Direct Benefit Transfer (DBT) Bank Details",
            "what_document_says": "Active individual savings bank account seeded with Aadhaar. Joint accounts not permitted.",
            "what_it_means": "Your active savings bank account number for direct scholarship fund deposit through government DBT.",
            "what_user_should_provide": "Your individual savings account number in an Aadhaar-linked bank.",
            "expected_format": "9 to 18 digits numeric",
            "example_from_document": "9182736451029",
            "validation_rules": ["numeric_only", "length_between_9_and_18"],
            "explanation": "Your active savings bank account number for direct scholarship fund deposit through government DBT.",
            "what_to_enter": "Your individual savings account number in an Aadhaar-seeded bank. Joint accounts or minor accounts may cause rejection.",
            "example": "9182736451029",
            "confidence": 0.95,
            "sensitive": True,
            "bbox": {"x": 24.0, "y": 57.0, "width": 32.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "आधार से जुड़ा सक्रिय व्यक्तिगत बचत बैंक खाता। संयुक्त खाते की अनुमति नहीं है।",
                    "what_it_means": "छात्रवृत्ति राशि सीधे जमा करने के लिए आपका सक्रिय बचत बैंक खाता संख्या।",
                    "explanation": "छात्रवृत्ति राशि सीधे जमा करने के लिए आपका सक्रिय बचत बैंक खाता संख्या।",
                    "what_to_enter": "आधार से जुड़े अपने बैंक खाते की संख्या दर्ज करें। संयुक्त (Joint) खाता न दें।",
                    "example": "9182736451029"
                },
                "mr": {
                    "what_document_says": "आधारशी जोडलेले वैयक्तिक चालू बचत बँक खाते. संयुक्त खात्यास परवानगी नाही.",
                    "what_it_means": "शिष्यवृत्तीची रक्कम थेट खात्यात जमा होण्यासाठी तुमचा चालू बचत बँक खाते क्रमांक.",
                    "explanation": "शिष्यवृत्तीची रक्कम थेट खात्यात जमा होण्यासाठी तुमचा चालू बचत बँक खाते क्रमांक.",
                    "what_to_enter": "आधार कार्डशी जोडलेला तुमचा वैयक्तिक बँक खाते क्रमांक प्रविष्ट करा.",
                    "example": "9182736451029"
                }
            }
        },
        {
            "id": "field_010",
            "name": "Bank IFSC Code",
            "label": "Bank IFSC Code",
            "type": "text",
            "required": True,
            "page": 1,
            "section": "4. Direct Benefit Transfer (DBT) Bank Details",
            "what_document_says": "11-character IFSC code printed on bank passbook / cheque leaf. 5th character is zero.",
            "what_it_means": "An 11-character alphanumeric code identifying your specific bank and branch for electronic payments.",
            "what_user_should_provide": "11-character code printed on the top of your cheque book leaf or bank passbook.",
            "expected_format": "11 alphanumeric characters (e.g. SBIN0001485)",
            "example_from_document": "SBIN0001485",
            "validation_rules": ["ifsc_format_11_chars"],
            "explanation": "An 11-character alphanumeric code identifying your specific bank and branch for electronic payments.",
            "what_to_enter": "11-character code printed on the top of your cheque book leaf or bank passbook first page.",
            "example": "SBIN0001485",
            "confidence": 0.94,
            "sensitive": True,
            "bbox": {"x": 62.0, "y": 57.0, "width": 28.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "पासबुक/चेक पर मुद्रित 11 वर्णों का IFSC कोड। 5वां वर्ण शून्य होता है।",
                    "what_it_means": "इलेक्ट्रॉनिक फंड ट्रांसफर के लिए बैंक शाखा की पहचान करने वाला 11 वर्णों का कोड।",
                    "explanation": "इलेक्ट्रॉनिक फंड ट्रांसफर के लिए बैंक शाखा की पहचान करने वाला 11 वर्णों का कोड।",
                    "what_to_enter": "अपनी पासबुक या चेक बुक पर मुद्रित 11 अक्षरों का IFSC कोड दर्ज करें।",
                    "example": "SBIN0001485"
                },
                "mr": {
                    "what_document_says": "पासबुक/चेकवर छापलेला ११ अक्षरी IFSC कोड. ५वे अक्षर शून्य असते.",
                    "what_it_means": "इलेक्ट्रॉनिक बँक व्यवहारांसाठी तुमच्या बँकेची शाखा ओळखणारा ११ अंकी सांकेतांक.",
                    "explanation": "इलेक्ट्रॉनिक बँक व्यवहारांसाठी तुमच्या बँकेची शाखा ओळखणारा ११ अंकी सांकेतांक.",
                    "what_to_enter": "पासबुक किंवा चेकबुकच्या पहिल्या पानावर असलेला ११ अक्षरी IFSC कोड प्रविष्ट करा.",
                    "example": "SBIN0001485"
                }
            }
        },
        {
            "id": "field_011",
            "name": "Father's Occupation",
            "label": "Father's Occupation (Optional)",
            "type": "text",
            "required": False,
            "page": 1,
            "section": "2. Family & Income Information",
            "what_document_says": "Primary occupation of father/guardian (Optional).",
            "what_it_means": "The primary profession, trade, business, or employment from which your father earns a living.",
            "what_user_should_provide": "Enter occupation title (e.g. Agriculture / Salaried / Business / Retired). Optional field.",
            "expected_format": "Text",
            "example_from_document": "Private Sector Employee",
            "validation_rules": [],
            "explanation": "The primary profession, trade, business, or employment from which your father earns a living.",
            "what_to_enter": "Enter occupation title (e.g. Agriculture / Salaried / Business / Daily Wage / Retired). Optional field.",
            "example": "Private Sector Employee",
            "confidence": 0.88,
            "sensitive": False,
            "bbox": {"x": 24.0, "y": 64.0, "width": 32.0, "height": 3.8},
            "translations": {
                "hi": {
                    "what_document_says": "पिता/अभिभावक का प्राथमिक व्यवसाय (ऐच्छिक)।",
                    "what_it_means": "आपके पिता का मुख्य पेशा, व्यवसाय, नौकरी या आजीविका का साधन।",
                    "explanation": "आपके पिता का मुख्य पेशा, व्यवसाय, नौकरी या आजीविका का साधन।",
                    "what_to_enter": "पेशा लिखें (जैसे कृषि, निजी नौकरी, व्यापार, दैनिक वेतनभोगी)। यह ऐच्छिक है।",
                    "example": "निजी नौकरी (Private Sector)"
                },
                "mr": {
                    "what_document_says": "वडिलांचा/पालकांचा प्राथमिक व्यवसाय (ऐच्छिक).",
                    "what_it_means": "तुमच्या वडिलांचा मुख्य व्यवसाय, नोकरी किंवा उपजीविकेचे साधन.",
                    "explanation": "तुमच्या वडिलांचा मुख्य व्यवसाय, नोकरी किंवा उपजीविकेचे साधन.",
                    "what_to_enter": "व्यवसायाचे स्वरूप प्रविष्ट करा (उदा. शेती, खाजगी नोकरी, व्यवसाय). हे ऐच्छिक आहे.",
                    "example": "खाजगी नोकरी"
                }
            }
        },
        {
            "id": "field_012",
            "name": "Applicant Signature & Date",
            "label": "Applicant Signature & Date",
            "type": "signature",
            "required": True,
            "page": 1,
            "section": "5. Declaration & Undertaking",
            "what_document_says": "Sign within the marked box in black/blue ink confirming truth of declaration. Enter submission date.",
            "what_it_means": "Your official handwritten or digital signature confirming all supplied information is true and accurate.",
            "what_user_should_provide": "Sign your regular signature in black or blue ink within the marked box, followed by the submission date.",
            "expected_format": "[Signature] DD/MM/YYYY",
            "example_from_document": "[Priya Sharma] 24/10/2024",
            "validation_rules": ["signature_required"],
            "explanation": "Your official handwritten or digital signature confirming all supplied information is true and accurate.",
            "what_to_enter": "Sign your regular signature in black or blue ink within the marked box, followed by the current submission date.",
            "example": "[Priya Sharma] 24/10/2024",
            "confidence": 0.91,
            "sensitive": False,
            "bbox": {"x": 62.0, "y": 80.5, "width": 30.0, "height": 8.0},
            "translations": {
                "hi": {
                    "what_document_says": "घोषणा की सत्यता की पुष्टि करते हुए काली/नीली स्याही में हस्ताक्षर करें। जमा करने की तिथि लिखें।",
                    "what_it_means": "आपका आधिकारिक हस्ताक्षर जो यह प्रमाणित करता है कि दी गई सभी जानकारियां सत्य और सही हैं।",
                    "explanation": "आपका आधिकारिक हस्ताक्षर जो यह प्रमाणित करता है कि दी गई सभी जानकारियां सत्य और सही हैं।",
                    "what_to_enter": "दिए गए बॉक्स में नीली या काली स्याही से हस्ताक्षर करें और आज की तारीख लिखें।",
                    "example": "[हस्ताक्षर] 24/10/2024"
                },
                "mr": {
                    "what_document_says": "माहिती खरी असल्याचे प्रमाणित करणारी काळ्या/निळ्या शाईतील स्वाक्षरी. तारीख प्रविष्ट करा.",
                    "what_it_means": "तुम्ही पुरवलेली सर्व माहिती खरी आणि अचूक असल्याचे प्रमाणित करणारी तुमची स्वाक्षरी.",
                    "explanation": "तुम्ही पुरवलेली सर्व माहिती खरी आणि अचूक असल्याचे प्रमाणित करणारी तुमची स्वाक्षरी.",
                    "what_to_enter": "चौकटीमध्ये काळ्या किंवा निळ्या शाईने स्वाक्षरी करा आणि अर्जाची तारीख टाका.",
                    "example": "[स्वाक्षरी] २४/१०/२०२४"
                }
            }
        }
    ]
}

# Guided question flows for "Help Me Fill This" / Document-Aware Guided Filling
HELP_FILL_FLOWS: Dict[str, List[Dict[str, Any]]] = {
    "field_003": [
        {
            "step_id": "father_income",
            "what_document_says": "Enter income for the previous financial year in INR.",
            "what_it_means": "The form asks for your family's annual income in Indian Rupees. We will calculate it from monthly earnings.",
            "question": {
                "en": "According to the form, income must be reported in INR. What is your father's (or guardian's) monthly income?",
                "hi": "फॉर्म के अनुसार, आय INR में होनी चाहिए। आपके पिता (या अभिभावक) की मासिक आय कितनी है?",
                "mr": "अर्जातील नियमानुसार उत्पन्न रुपयात (INR) असणे आवश्यक आहे. तुमच्या वडिलांचे दरमहा उत्पन्न किती आहे?"
            },
            "help_text": {
                "en": "Enter approx monthly salary or earnings in ₹. If not earning or retired without pension, enter 0.",
                "hi": "अनुमानित मासिक आय दर्ज करें। यदि आय नहीं है तो 0 लिखें।",
                "mr": "अंदाजे मासिक उत्पन्न प्रविष्ट करा. उत्पन्न नसल्यास 0 लिहा."
            },
            "input_type": "currency",
            "placeholder": "₹ 30,000",
            "unit": "₹ / month",
            "validation_rule": "currency_inr"
        },
        {
            "step_id": "mother_has_income",
            "what_document_says": "Include income from all earning family members during preceding financial year.",
            "what_it_means": "Check if mother has an active income source.",
            "question": {
                "en": "Does your mother earn an income?",
                "hi": "क्या आपकी माताजी कोई आय अर्जित करती हैं?",
                "mr": "तुमच्या आईला काही मासिक उत्पन्न आहे का?"
            },
            "help_text": {
                "en": "Select Yes if employed, in business, or having pension; No if homemaker.",
                "hi": "यदि गृहिणी हैं तो नहीं (No) चुनें।",
                "mr": "गृहिणी असल्यास नाही (No) निवडा."
            },
            "input_type": "choice",
            "options": ["Yes", "No"]
        },
        {
            "step_id": "mother_income",
            "what_document_says": "Enter monthly earnings for mother (applicable only if selected Yes).",
            "what_it_means": "Mother's monthly contribution to family income.",
            "question": {
                "en": "What is her monthly income?",
                "hi": "आपकी माताजी की मासिक आय कितनी है?",
                "mr": "तुमच्या आईचे दरमहा उत्पन्न किती आहे?"
            },
            "help_text": {
                "en": "Enter her monthly earnings in ₹.",
                "hi": "मासिक आय दर्ज करें।",
                "mr": "मासिक उत्पन्न प्रविष्ट करा."
            },
            "input_type": "currency",
            "placeholder": "₹ 10,000",
            "unit": "₹ / month",
            "conditional_on": {"step_id": "mother_has_income", "value": "Yes"},
            "validation_rule": "currency_inr"
        },
        {
            "step_id": "other_annual_income",
            "what_document_says": "Include any other family income per year (agriculture, rent, investments).",
            "what_it_means": "Total gross income from other family assets.",
            "question": {
                "en": "Any other family income per year (agriculture, rent, investments)?",
                "hi": "क्या अन्य स्रोतों से कोई वार्षिक आय है (जैसे कृषि, किराया आदि)?",
                "mr": "कुटुंबाला शेती, भाडे किंवा इतर मार्गाने काही वार्षिक उत्पन्न आहे का?"
            },
            "help_text": {
                "en": "Enter total yearly amount or 0 if none.",
                "hi": "वार्षिक राशि लिखें या 0 दर्ज करें।",
                "mr": "वार्षिक रक्कम लिहा किंवा काही नसल्यास 0 टाका."
            },
            "input_type": "currency",
            "placeholder": "₹ 0",
            "unit": "₹ / year",
            "validation_rule": "currency_inr"
        }
    ],
    "field_002": [
        {
            "step_id": "birth_date",
            "what_document_says": "Applicant must be between 18 and 35 years as on 01/08/2024. Format: DD/MM/YYYY.",
            "what_it_means": "The form specifies an age eligibility window of 18 to 35 years.",
            "question": {
                "en": "The form specifies an age range of 18–35 years. What is your date of birth?",
                "hi": "फॉर्म में 18-35 वर्ष की आयु सीमा निर्दिष्ट है। आपकी जन्म तिथि क्या है?",
                "mr": "अर्जात १८ ते ३५ वयोगटाची अट नमूद आहे. तुमची जन्मतारीख काय आहे?"
            },
            "help_text": {
                "en": "Must match your 10th marksheet or birth certificate. (Format: DD/MM/YYYY or select date)",
                "hi": "यह आपकी 10वीं की अंकतालिका या जन्म प्रमाण पत्र से मेल खानी चाहिए।",
                "mr": "१० वीचे गुणपत्रक किंवा जन्म दाखल्याशी जुळणारी तारीख निवडा."
            },
            "input_type": "date",
            "placeholder": "YYYY-MM-DD",
            "validation_rule": "age_between_18_35"
        }
    ],
    "field_006": [
        {
            "step_id": "phone_number",
            "what_document_says": "Enter a 10-digit mobile number linked to Aadhaar for OTP verification.",
            "what_it_means": "The form requires a valid 10-digit Indian phone number.",
            "question": {
                "en": "The form requires a 10-digit mobile number. What is your mobile number?",
                "hi": "फॉर्म में 10 अंकों का मोबाइल नंबर आवश्यक है। आपका मोबाइल नंबर क्या है?",
                "mr": "अर्जात १० अंकी मोबाईल नंबर आवश्यक आहे. तुमचा मोबाईल नंबर काय आहे?"
            },
            "help_text": {
                "en": "Ensure this number is linked to your Aadhaar card for DBT verification.",
                "hi": "सुनिश्चित करें कि यह नंबर आपके आधार कार्ड से जुड़ा हुआ है।",
                "mr": "हा नंबर आधार कार्डशी जोडलेला असणे आवश्यक आहे."
            },
            "input_type": "text",
            "placeholder": "9820154321",
            "validation_rule": "10_digits_required"
        }
    ],
    "field_005": [
        {
            "step_id": "domicile_state",
            "what_document_says": "Attach valid Domicile Certificate issued by competent Revenue Authority.",
            "what_it_means": "Choose the state where your official Domicile certificate was issued.",
            "question": {
                "en": "Which state do you hold a permanent residence / domicile certificate for?",
                "hi": "आपके पास किस राज्य का अधिवास (Domicile) प्रमाण पत्र है?",
                "mr": "तुमच्याकडे कोणत्या राज्याचे अधिवास (Domicile) प्रमाणपत्र आहे?"
            },
            "help_text": {
                "en": "Choose the state where your official certificate was issued.",
                "hi": "उस राज्य का चयन करें जिसने आपका प्रमाणपत्र जारी किया है।",
                "mr": "ज्या राज्याने तुमचे प्रमाणपत्र जारी केले आहे ते राज्य निवडा."
            },
            "input_type": "choice",
            "options": ["Maharashtra", "Karnataka", "Delhi", "Gujarat", "Uttar Pradesh", "Other"]
        }
    ],
    "field_004": [
        {
            "step_id": "category_selection",
            "what_document_says": "Select constitutional category: General, OBC (Non-Creamy), SC, ST, EWS.",
            "what_it_means": "Choose the exact category matching your official records.",
            "question": {
                "en": "What is your constitutional category according to your official documents?",
                "hi": "आपके आधिकारिक दस्तावेजों के अनुसार आपकी सामाजिक श्रेणी क्या है?",
                "mr": "तुमच्या अधिकृत कागदपत्रांनुसार तुमचा सामाजिक प्रवर्ग कोणता आहे?"
            },
            "help_text": {
                "en": "If selecting SC, ST, or OBC, you must submit a valid Caste Certificate.",
                "hi": "आरक्षित श्रेणी के लिए वैध जाति प्रमाण पत्र संलग्न करना आवश्यक होगा।",
                "mr": "राखीव प्रवर्गासाठी वैध जात प्रमाणपत्र असणे अनिवार्य आहे."
            },
            "input_type": "choice",
            "options": ["General", "OBC (Non-Creamy)", "SC", "ST", "EWS"]
        }
    ],
    "field_007": [
        {
            "step_id": "email_input",
            "what_document_says": "Valid email address for electronic correspondence.",
            "what_it_means": "Active email to receive application receipts.",
            "question": {
                "en": "What is your personal email address?",
                "hi": "आपका व्यक्तिगत ईमेल पता क्या है?",
                "mr": "तुमचा वैयक्तिक ईमेल आयडी काय आहे?"
            },
            "help_text": {
                "en": "You will receive application alerts and updates here.",
                "hi": "छात्रवृत्ति की जानकारी इस ईमेल पर भेजी जाएगी।",
                "mr": "सर्व अधिकृत अपडेट्स या ईमेलवर पाठवले जातील."
            },
            "input_type": "text",
            "placeholder": "example@email.com",
            "validation_rule": "valid_email"
        }
    ],
    "field_009": [
        {
            "step_id": "bank_account",
            "what_document_says": "Active individual savings bank account seeded with Aadhaar. Joint accounts not permitted.",
            "what_it_means": "Bank account number for DBT government transfer.",
            "question": {
                "en": "What is your savings bank account number?",
                "hi": "आपका बचत बैंक खाता संख्या क्या है?",
                "mr": "तुमचा बचत बँक खाते क्रमांक काय आहे?"
            },
            "help_text": {
                "en": "Please ensure the account is in your name and seeded with Aadhaar.",
                "hi": "कृपया सुनिश्चित करें कि खाता आपके नाम पर है और आधार से लिंक है।",
                "mr": "खाते स्वतःच्या नावावर आणि आधारशी जोडलेले असल्याची खात्री करा."
            },
            "input_type": "text",
            "placeholder": "Enter account number",
            "validation_rule": "bank_account"
        }
    ]
}
