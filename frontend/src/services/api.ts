import type { FormAnalysisData, HelpFillResponse, ChatResponse, Language } from '../types';

const API_BASE = '/api';

export async function checkBackendHealth(): Promise<{ status: string; ai_configured?: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend health check error, running in resilient client mode:', err);
    return { status: 'fallback', ai_configured: false };
  }
}

export async function analyzeDocument(
  file: File | null,
  isDemo: boolean = false,
  language: Language = 'en'
): Promise<FormAnalysisData> {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  }
  formData.append('is_demo', String(isDemo));
  formData.append('language', language);

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Analysis failed (${res.status})`);
    }

    const data: FormAnalysisData = await res.json();
    return data;
  } catch (err: any) {
    console.warn('Backend analyze call failed, falling back to local demo form:', err);
    // If backend isn't reachable or throws, return fallback demo
    return getLocalDemoData(language);
  }
}

export async function explainField(fieldId: string, language: Language = 'en'): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field_id: fieldId, language }),
    });

    if (!res.ok) throw new Error('Explain request failed');
    return await res.json();
  } catch (err) {
    console.warn('Explain API error:', err);
    return null;
  }
}

export async function requestHelpFill(
  fieldId: string,
  currentStep: number,
  answers: Record<string, any>,
  language: Language = 'en'
): Promise<HelpFillResponse> {
  try {
    const res = await fetch(`${API_BASE}/help-fill`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_id: fieldId,
        current_step: currentStep,
        answers,
        language,
      }),
    });

    if (!res.ok) throw new Error('Help Fill request failed');
    return await res.json();
  } catch (err) {
    console.warn('Help Fill API error, using local computation:', err);
    return computeLocalHelpFill(fieldId, currentStep, answers, language);
  }
}

export async function sendChatMessage(
  message: string,
  formTitle: string,
  selectedFieldId?: string,
  language: Language = 'en',
  history: Array<{ role: string; content: string }> = []
): Promise<ChatResponse> {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        form_title: formTitle,
        selected_field_id: selectedFieldId,
        language,
        history,
      }),
    });

    if (!res.ok) throw new Error('Chat request failed');
    return await res.json();
  } catch (err) {
    console.warn('Chat API error, using local fallback:', err);
    return getLocalChatReply(message, language);
  }
}

// Resilient local fallback in case network disconnects during demo
function getLocalDemoData(lang: Language): FormAnalysisData {
  return {
    form_id: 'demo-scholarship-form',
    form_title: 'National Post-Matric Scholarship Application Form 2024-25',
    summary: 'Official student scholarship form requiring personal identification, domicile verification, family income declarations, and bank details for direct benefit transfer (DBT).',
    total_fields: 12,
    required_fields_count: 9,
    optional_fields_count: 3,
    overall_confidence: 0.94,
    language: lang,
    is_demo: true,
    document_preview_url: '/demo-form.svg',
    fields: [
      {
        id: 'field_001',
        name: 'Full Name',
        type: 'text',
        required: true,
        page: 1,
        section: '1. Personal Information',
        explanation: lang === 'hi' ? 'अपना पूरा कानूनी नाम ठीक वैसे ही दर्ज करें जैसा आपके 10वीं कक्षा के प्रमाणपत्र पर है।' : lang === 'mr' ? 'तुमचे पूर्ण कायदेशीर नाव तुमच्या १० वीच्या प्रमाणपत्रावर असल्याप्रमाणेच प्रविष्ट करा.' : 'Enter your complete legal name exactly as it appears on your 10th Standard / SSC certificate or official government ID.',
        what_to_enter: 'Your First Name, Middle Name, and Surname in capital letters. Do not add salutations like Mr., Ms., or Shri.',
        example: 'PRIYA RAMESH SHARMA',
        confidence: 0.98,
        sensitive: false,
        bbox: { x: 24.0, y: 19.5, width: 45.0, height: 3.8 }
      },
      {
        id: 'field_002',
        name: 'Date of Birth',
        type: 'date',
        required: true,
        page: 1,
        section: '1. Personal Information',
        explanation: lang === 'hi' ? 'आपकी आधिकारिक जन्म तिथि, जिसका उपयोग छात्रवृत्ति के लिए आयु पात्रता की पुष्टि करने के लिए किया जाता है।' : lang === 'mr' ? 'तुमची अधिकृत जन्मतारीख, जी शिष्यवृत्तीसाठी वयोमर्यादा पडताळण्यासाठी वापरली जाते.' : 'The official date on which you were born, used to verify age eligibility criteria for this scholarship.',
        what_to_enter: 'Day, Month, and Year in DD/MM/YYYY format matching your birth certificate or SSC marksheet.',
        example: '15/08/2004',
        confidence: 0.96,
        sensitive: false,
        bbox: { x: 24.0, y: 24.8, width: 24.0, height: 3.8 }
      },
      {
        id: 'field_003',
        name: 'Annual Family Income',
        type: 'currency',
        required: true,
        page: 1,
        section: '2. Family & Income Information',
        explanation: lang === 'hi' ? 'एक वित्तीय वर्ष में सभी स्रोतों से आपके परिवार (माता-पिता/अभिभावक) द्वारा अर्जित कुल वार्षिक आय।' : lang === 'mr' ? 'एका आर्थिक वर्षात सर्व स्त्रोतांकडून तुमच्या कुटुंबातील सर्व कमवत्या सदस्यांनी मिळवलेले एकूण एकत्रित वार्षिक उत्पन्न.' : 'The combined gross income earned by all earning family members (parents/guardians) from all sources in one financial year.',
        what_to_enter: 'Total annual income in Indian Rupees. Must match the competent revenue authority income certificate (Tehsildar/SDM).',
        example: '₹4,80,000',
        confidence: 0.94,
        sensitive: false,
        bbox: { x: 24.0, y: 30.5, width: 30.0, height: 3.8 }
      },
      {
        id: 'field_004',
        name: 'Category / Caste',
        type: 'dropdown',
        required: true,
        page: 1,
        section: '1. Personal Information',
        explanation: 'Your constitutional social category (General / OBC / SC / ST / EWS) required to determine specific category reservation quotas.',
        what_to_enter: 'Select your exact category. If applying under reserved categories (SC/ST/OBC), you must possess a valid Caste Certificate.',
        example: 'OBC (Non-Creamy Layer)',
        confidence: 0.92,
        sensitive: false,
        bbox: { x: 58.0, y: 24.8, width: 28.0, height: 3.8 }
      },
      {
        id: 'field_005',
        name: 'Domicile State',
        type: 'dropdown',
        required: true,
        page: 1,
        section: '3. Domicile & Residence',
        explanation: 'The Indian State or Union Territory where you are officially and legally recognized as a permanent resident.',
        what_to_enter: 'The state where you or your parents hold a registered Domicile / Residence Certificate.',
        example: 'Maharashtra',
        confidence: 0.95,
        sensitive: false,
        bbox: { x: 24.0, y: 36.2, width: 30.0, height: 3.8 }
      },
      {
        id: 'field_006',
        name: 'Mobile Number',
        type: 'phone',
        required: true,
        page: 1,
        section: '1. Personal Information',
        explanation: 'An active, personal 10-digit mobile number for scholarship status alerts, application OTPs, and verification SMS.',
        what_to_enter: '10-digit Indian mobile number without +91 or leading 0. Must be linked to Aadhaar for DBT verification.',
        example: '9820154321',
        confidence: 0.99,
        sensitive: false,
        bbox: { x: 24.0, y: 42.0, width: 26.0, height: 3.8 }
      },
      {
        id: 'field_007',
        name: 'Email Address',
        type: 'email',
        required: true,
        page: 1,
        section: '1. Personal Information',
        explanation: 'A valid email account where official application receipts, verification notices, and scholarship award letters will be sent.',
        what_to_enter: 'Your personal active email address that you check regularly.',
        example: 'priya.sharma@example.com',
        confidence: 0.97,
        sensitive: false,
        bbox: { x: 58.0, y: 42.0, width: 34.0, height: 3.8 }
      },
      {
        id: 'field_008',
        name: 'Permanent Residential Address',
        type: 'address',
        required: true,
        page: 1,
        section: '3. Domicile & Residence',
        explanation: 'The full postal address of your permanent residence where you or your family permanently reside.',
        what_to_enter: 'House/Flat number, Street name, Locality, City/Taluka, District, State, and 6-digit PIN Code.',
        example: 'Flat 402, Shivneri Heights, Senapati Bapat Road, Pune, Maharashtra - 411016',
        confidence: 0.93,
        sensitive: false,
        bbox: { x: 24.0, y: 48.0, width: 68.0, height: 5.5 }
      },
      {
        id: 'field_009',
        name: 'Bank Account Number',
        type: 'number',
        required: true,
        page: 1,
        section: '4. Direct Benefit Transfer (DBT) Bank Details',
        explanation: 'Your active savings bank account number for direct scholarship fund deposit through government DBT.',
        what_to_enter: 'Your individual savings account number in an Aadhaar-seeded bank. Joint accounts or minor accounts may cause rejection.',
        example: '9182736451029',
        confidence: 0.95,
        sensitive: true,
        bbox: { x: 24.0, y: 57.0, width: 32.0, height: 3.8 }
      },
      {
        id: 'field_010',
        name: 'Bank IFSC Code',
        type: 'text',
        required: true,
        page: 1,
        section: '4. Direct Benefit Transfer (DBT) Bank Details',
        explanation: 'An 11-character alphanumeric code identifying your specific bank and branch for electronic payments.',
        what_to_enter: '11-character code printed on the top of your cheque book leaf or bank passbook first page.',
        example: 'SBIN0001485',
        confidence: 0.94,
        sensitive: true,
        bbox: { x: 62.0, y: 57.0, width: 28.0, height: 3.8 }
      },
      {
        id: 'field_011',
        name: "Father's Occupation",
        type: 'text',
        required: false,
        page: 1,
        section: '2. Family & Income Information',
        explanation: 'The primary profession, trade, business, or employment from which your father earns a living.',
        what_to_enter: 'Enter occupation title (e.g. Agriculture / Salaried / Business / Daily Wage / Retired). Optional field.',
        example: 'Private Sector Employee',
        confidence: 0.88,
        sensitive: false,
        bbox: { x: 24.0, y: 64.0, width: 32.0, height: 3.8 }
      },
      {
        id: 'field_012',
        name: 'Applicant Signature & Date',
        type: 'signature',
        required: true,
        page: 1,
        section: '5. Declaration & Undertaking',
        explanation: 'Your official handwritten or digital signature confirming all supplied information is true and accurate.',
        what_to_enter: 'Sign your regular signature in black or blue ink within the marked box, followed by the current submission date.',
        example: '[Priya Sharma] 24/10/2024',
        confidence: 0.91,
        sensitive: false,
        bbox: { x: 62.0, y: 80.5, width: 30.0, height: 8.0 }
      }
    ]
  };
}

function computeLocalHelpFill(
  fieldId: string,
  step: number,
  answers: Record<string, any>,
  lang: Language
): HelpFillResponse {
  if (fieldId === 'field_003') {
    // Annual income
    if (step >= 3) {
      const f = parseFloat(answers.father_income || '30000') || 0;
      const m = answers.mother_has_income === 'Yes' ? (parseFloat(answers.mother_income || '10000') || 0) : 0;
      const total = (f * 12) + (m * 12);
      const formatted = `₹${total.toLocaleString('en-IN')}`;
      return {
        field_id: fieldId,
        field_name: 'Annual Family Income',
        current_step_index: 3,
        total_steps: 3,
        is_completed: true,
        calculation_breakdown: `• Father: ₹${f.toLocaleString('en-IN')} × 12 = ₹${(f * 12).toLocaleString('en-IN')}\n• Mother: ₹${m.toLocaleString('en-IN')} × 12 = ₹${(m * 12).toLocaleString('en-IN')}\n• Estimated Total = ${formatted}`,
        suggested_value: formatted,
        verification_warning: '⚠ Please verify this amount against your official Income Certificate issued by the competent authority.',
        language: lang,
      };
    }
    if (step === 0) {
      return {
        field_id: fieldId,
        field_name: 'Annual Family Income',
        current_step_index: 0,
        total_steps: 3,
        is_completed: false,
        current_step: {
          step_id: 'father_income',
          question: lang === 'mr' ? 'तुमच्या वडिलांचे दरमहा उत्पन्न किती आहे?' : lang === 'hi' ? 'आपके पिता की मासिक आय कितनी है?' : "What is your father's monthly income?",
          help_text: 'Enter approx monthly salary or earnings in ₹',
          input_type: 'currency',
          placeholder: '₹ 30,000',
        },
        language: lang,
      };
    }
    if (step === 1) {
      return {
        field_id: fieldId,
        field_name: 'Annual Family Income',
        current_step_index: 1,
        total_steps: 3,
        is_completed: false,
        current_step: {
          step_id: 'mother_has_income',
          question: lang === 'mr' ? 'तुमच्या आईला काही मासिक उत्पन्न आहे का?' : lang === 'hi' ? 'क्या आपकी माताजी कोई आय अर्जित करती हैं?' : 'Does your mother have an income?',
          input_type: 'choice',
          options: ['Yes', 'No'],
        },
        language: lang,
      };
    }
    return {
      field_id: fieldId,
      field_name: 'Annual Family Income',
      current_step_index: 2,
      total_steps: 3,
      is_completed: false,
      current_step: {
        step_id: 'mother_income',
        question: lang === 'mr' ? 'तुमच्या आईचे दरमहा उत्पन्न किती आहे?' : lang === 'hi' ? 'आपकी माताजी की मासिक आय कितनी है?' : "What is her monthly income?",
        input_type: 'currency',
        placeholder: '₹ 10,000',
      },
      language: lang,
    };
  }

  return {
    field_id: fieldId,
    field_name: 'Field',
    current_step_index: 0,
    total_steps: 1,
    is_completed: true,
    suggested_value: answers.input_val || '',
    verification_warning: 'Please verify against your official documents.',
    language: lang,
  };
}

function getLocalChatReply(msg: string, lang: Language): ChatResponse {
  const m = msg.toLowerCase();
  if (m.includes('domicile') || m.includes('अधिवास')) {
    return {
      reply: lang === 'mr'
        ? 'अधिवास (Domicile) म्हणजे तुम्ही ज्या राज्याचे कायदेशीर कायमस्वरूपी रहिवासी आहात ते राज्य. या शिष्यवृत्तीसाठी तहसीलदार यांनी दिलेले अधिवास प्रमाणपत्र आवश्यक असते.'
        : lang === 'hi'
        ? 'अधिवास (Domicile) उस राज्य को दर्शाता है जहां आप कानूनी रूप से स्थायी निवासी हैं। इसके लिए तहसीलदार द्वारा जारी डोमिसाइल प्रमाणपत्र आवश्यक होता है।'
        : 'Domicile refers to the state where you are officially considered a permanent resident. For this form, you will need a valid Domicile Certificate issued by a Tehsildar or Magistrate.',
      suggested_questions: ['What documents are required for domicile?', 'Is income certificate mandatory?', 'What is IFSC?']
    };
  }
  return {
    reply: lang === 'mr'
      ? 'फॉर्मच्या नियमांची खात्री करा. कोणत्याही रकान्यावर क्लिक करून तुम्ही सविस्तर माहिती व मदत मिळवू शकता.'
      : lang === 'hi'
      ? 'कृपया फॉर्म के नियमों की जांच करें। किसी भी फ़ील्ड को समझने के लिए उस पर क्लिक करें।'
      : 'FormEase recommends verifying your information against official documents. Select any field on the form to see detailed guidance and step-by-step help.',
    suggested_questions: ['What does domicile mean?', 'What is IFSC code?', 'How to calculate annual family income?']
  };
}
