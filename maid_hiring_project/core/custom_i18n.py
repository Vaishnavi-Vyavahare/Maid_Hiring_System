
import os
import re
import struct
import sys

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def generate_po_file(lang_code, translations):
    """
    Generates a .po file for the given language code and translation dictionary.
    """
    po_content = [
        'msgid ""',
        'msgstr ""',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        f'"Language: {lang_code}\\n"',
        '',
    ]
    
    for msgid, msgstr in translations.items():
        # Escape quotes in msgid and msgstr
        escaped_msgid = msgid.replace('"', '\\"')
        escaped_msgstr = msgstr.replace('"', '\\"')
        
        po_content.append(f'msgid "{escaped_msgid}"')
        po_content.append(f'msgstr "{escaped_msgstr}"')
        po_content.append('')
        
    return "\n".join(po_content)

def write_mo_file(po_file_path, mo_file_path):
    """
    Compiles a .po file to a .mo file.
    This is a simplified MO compiler implemented in Python.
    """
    print(f"Compiling {po_file_path} -> {mo_file_path}")
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    MESSAGES = {}
    current_msgid = None
    current_msgstr = None
    
    # Very basic PO parser (handles single-line mostly, but good enough for our generated files)
    for line in lines:
        line = line.strip()
        if line.startswith('msgid "'):
            current_msgid = line[7:-1].replace('\\"', '"')
        elif line.startswith('msgstr "'):
            current_msgstr = line[8:-1].replace('\\"', '"')
            if current_msgid and current_msgid != "":
                MESSAGES[current_msgid] = current_msgstr

    # MO File Generation
    # Magic number, version, num strings, offset orig, offset trans, hash size, hash offset
    magic = 0x950412de
    version = 0
    num_strings = len(MESSAGES)
    
    # Sort keys to ensure binary search works (standard behavior)
    keys = sorted(MESSAGES.keys())
    
    # Offsets
    ids_offset = 28 # Header size (7 * 4 bytes)
    strs_offset = ids_offset + (num_strings * 8) # 8 bytes per ID pointer (len + offset)
    
    ids_data = b""
    strs_data = b""
    
    # Calculate initial data offset
    # Header + ID pointers + Str pointers
    current_data_offset = strs_offset + (num_strings * 8)
    
    data_buffer = b""
    
    # We need to construct the tables
    # OTable: Length, Offset for msgids
    # TTable: Length, Offset for msgstrs
    
    otable = []
    ttable = []
    
    for msgid in keys:
        msgstr = MESSAGES[msgid]
        
        # Encode strings
        msgid_bytes = msgid.encode('utf-8') + b'\0'
        msgstr_bytes = msgstr.encode('utf-8') + b'\0'
        
        otable.append((len(msgid_bytes) - 1, current_data_offset))
        data_buffer += msgid_bytes
        current_data_offset += len(msgid_bytes)
        
        ttable.append((len(msgstr_bytes) - 1, current_data_offset))
        data_buffer += msgstr_bytes
        current_data_offset += len(msgstr_bytes)

    # Write file
    with open(mo_file_path, 'wb') as f:
        # Header
        f.write(struct.pack('I', magic))
        f.write(struct.pack('I', version))
        f.write(struct.pack('I', num_strings))
        f.write(struct.pack('I', ids_offset))
        f.write(struct.pack('I', strs_offset))
        f.write(struct.pack('I', 0)) # Hash size
        f.write(struct.pack('I', 0)) # Hash offset
        
        # OTable
        for length, offset in otable:
            f.write(struct.pack('II', length, offset))
            
        # TTable
        for length, offset in ttable:
            f.write(struct.pack('II', length, offset))
            
        # Data
        f.write(data_buffer)

# ---------------------------------------------------------
# TRANSLATIONS
# ---------------------------------------------------------

base_translations = {
    # Navbar & Common
    "Maid Hiring System": {"hi": "मेड हायरिंग सिस्टम", "mr": "मोलकरीण हायरिंग सिस्टम"},
    "Home": {"hi": "होम", "mr": "मुखपृष्ठ"},
    "Sign In": {"hi": "साइन इन", "mr": "साइन इन"},
    "Create Account": {"hi": "खाता बनाएं", "mr": "खाते तयार करा"},
    "Logout": {"hi": "लॉग आउट", "mr": "बाहेर पडा"},
    "Welcome": {"hi": "स्वागत", "mr": "स्वागत"},
    "Register": {"hi": "रजिस्टर", "mr": "नोंदणी"},
    "All rights reserved.": {"hi": "सर्वाधिकार सुरक्षित।", "mr": "सर्व हक्क राखीव."},
    
    # Index/Home Page
    "Find Trusted & Verified Maids for Your Home": {"hi": "अपने घर के लिए विश्वसनीय और सत्यापित मेड खोजें", "mr": "आपल्या घरासाठी विश्वसनीय आणि सत्यापित मोलकरीण शोधा"},
    "Hire reliable professionals for cleaning, cooking, baby care, and household services. Experience a cleaner, more organized life with our verified experts.": {"hi": "सफाई, खाना पकाने, बच्चों की देखभाल और घरेलू सेवाओं के लिए विश्वसनीय पेशेवरों को किराए पर लें। हमारे सत्यापित विशेषज्ञों के साथ एक स्वच्छ, अधिक व्यवस्थित जीवन का अनुभव करें।", "mr": "स्वच्छता, स्वयंपाक, बाळाची काळजी आणि घरगुती कामांसाठी विश्वसनीय व्यावसायिकांना नियुक्त करा. आमच्या सत्यापित तज्ञांसह अधिक स्वच्छ आणि व्यवस्थित जीवनाचा अनुभव घ्या."},
    "Hire a Maid": {"hi": "मेड हायर करें", "mr": "मोलकरीण नेमा"},
    "Register as a Maid": {"hi": "मेड के रूप में रजिस्टर करें", "mr": "मोलकरीण म्हणून नोंदणी करा"},
    "Already a member?": {"hi": "पहले से सदस्य हैं?", "mr": "आधीच सदस्य आहात?"},
    "Verified Maids": {"hi": "सत्यापित मेड्स", "mr": "सत्यापित मोलकरीण"},
    "Every professional undergoes a thorough background check and verification process.": {"hi": "प्रत्येक पेशेवर एक गहन पृष्ठभूमि जांच और सत्यापन प्रक्रिया से गुजरता है।", "mr": "प्रत्येक व्यावसायिकाची पार्श्वभूमी तपासणी आणि सत्यापन प्रक्रिया केली जाते."},
    "Secure Hiring": {"hi": "सुरक्षित हायरिंग", "mr": "सुरक्षित भरती"},
    "Safe and transparent booking system with secure payment processing.": {"hi": "सुरक्षित भुगतान प्रसंस्करण के साथ सुरक्षित और पारदर्शी बुकिंग प्रणाली।", "mr": "सुरक्षित पेमेंट प्रक्रिया आणि पारदर्शक बुकिंग सिस्टम."},
    "Location-based": {"hi": "लोकेशन आधारित", "mr": "स्थानावर आधारित"},
    "Find the best helpers right in your neighborhood for faster availability.": {"hi": "तेजी से उपलब्धता के लिए अपने पड़ोस में सबसे अच्छे सहायकों को खोजें।", "mr": "जलद उपलब्धतेसाठी आपल्या परिसरात सर्वोत्तम मदतनीस शोधा."},
    "Trusted Platform": {"hi": "विश्वसनीय प्लेटफॉर्म", "mr": "विश्वसनीय प्लॅटफॉर्म"},
    "Joining thousands of families who trust our quality of service.": {"hi": "हमारी सेवा की गुणवत्ता पर भरोसा करने वाले हजारों परिवारों में शामिल हों।", "mr": "हजारो कुटुंबांमध्ये सामील व्हा जे आमच्या सेवेवर विश्वास ठेवतात."},
    "Ready to find your perfect home helper?": {"hi": "क्या आप अपने लिए सही घरेलू सहायक खोजने के लिए तैयार हैं?", "mr": "आपला परिपूर्ण घरगुती मदतनीस शोधण्यासाठी तयार आहात?"},
    "Join our community today and make your household management effortless.": {"hi": "आज ही हमारे समुदाय में शामिल हों और अपने घरेलू प्रबंधन को आसान बनाएं।", "mr": "आजच आमच्या समुदायात सामील व्हा आणि आपले घरगुती व्यवस्थापन सोपे करा."},
    "Why Choose Us": {"hi": "हमें क्यों चुनें", "mr": "आम्हाला का निवडावे"},
    "Home Service": {"hi": "घरेलू सेवा", "mr": "घरगुती सेवा"},
    
    # Login & Register
    "Welcome Back": {"hi": "वापसी पर स्वागत है", "mr": "पुन्हा स्वागत आहे"},
    "Sign in to your account": {"hi": "अपने खाते में साइन इन करें", "mr": "आपल्या खात्यात साइन इन करा"},
    "Email Address": {"hi": "ईमेल पता", "mr": "ईमेल पत्ता"},
    "Password": {"hi": "पासवर्ड", "mr": "पासवर्ड"},
    "Don’t have an account?": {"hi": "खाता नहीं है?", "mr": "खाते नाही?"},
    "Join our community today": {"hi": "आज ही हमारे समुदाय में शामिल हों", "mr": "आजच आमच्या समुदायात सामील व्हा"},
    "Full Name": {"hi": "पूरा नाम", "mr": "पूर्ण नाव"},
    "Phone Number": {"hi": "फोन नंबर", "mr": "फोन नंबर"},
    "Select Role": {"hi": "भूमिका चुनें", "mr": "भूमिका निवडा"},
    "Customer (Hire a Maid)": {"hi": "ग्राहक (मेड हायर करें)", "mr": "ग्राहक (मोलकरीण नेमा)"},
    "Maid (Find Work)": {"hi": "मेड (काम खोजें)", "mr": "मोलकरीण (काम शोधा)"},
    "Confirm Password": {"hi": "पासवर्ड की पुष्टि करें", "mr": "पासवर्ड पुष्टी करा"},
    "Register Now": {"hi": "अभी रजिस्टर करें", "mr": "आता नोंदणी करा"},
    "Already have an account?": {"hi": "क्या आपके पास पहले से एक खाता है?", "mr": "आधीच खाते आहे का?"},
    
    # Maid List
    "Find Your Perfect Help": {"hi": "अपनी सही मदद खोजें", "mr": "आपली योग्य मदत शोधा"},
    "Browse our verified network of skilled housemaids ready to help you.": {"hi": "हमारी सत्यापित कुशल मेड के नेटवर्क को ब्राउज़ करें जो आपकी मदद के लिए तैयार हैं।", "mr": "आमच्या सत्यापित कुशल मोलकरणींचे नेटवर्क ब्राउझ करा."},
    "Filters": {"hi": "फिल्टर", "mr": "फिल्टर्स"},
    "Skill Expertise": {"hi": "कौशल विशेषज्ञता", "mr": "कौशल्य"},
    "All Skills": {"hi": "सभी कौशल", "mr": "सर्व कौशल्ये"},
    "Salary Range (₹)": {"hi": "वेतन सीमा (₹)", "mr": "पगार श्रेणी (₹)"},
    "Apply Filters": {"hi": "फिल्टर लागू करें", "mr": "फिल्टर्स लागू करा"},
    "Reset All": {"hi": "सभी रीसेट करें", "mr": "सर्व रीसेट करा"},
    "Verified": {"hi": "सत्यापित", "mr": "सत्यापित"},
    "Expertise": {"hi": "विशेषज्ञता", "mr": "विशेषज्ञता"},
    "Contact Support": {"hi": "समर्थन से संपर्क करें", "mr": "सपोर्टशी संपर्क साधा"},
    "View Profile": {"hi": "प्रोफाइल देखें", "mr": "प्रोफाइल पहा"},
    "No Maids Match Your Filters": {"hi": "आपके फिल्टर से कोई मेड मेल नहीं खाती", "mr": "तुमच्या फिल्टरशी कोणतीही मोलकरीण जुळत नाही"},
    "Try adjusting your filters or search criteria.": {"hi": "अपने फिल्टर या खोज मानदंड को समायोजित करने का प्रयास करें।", "mr": "तुमचे फिल्टर किंवा शोध निकष बदलून पहा."},
    "Clear All Filters": {"hi": "सभी फिल्टर साफ़ करें", "mr": "सर्व फिल्टर्स काढा"},
    "month": {"hi": "महीना", "mr": "महिना"},
    "Location": {"hi": "स्थान", "mr": "स्थान"},
    "e.g. Mumbai": {"hi": "उदा. मुंबई", "mr": "उदा. मुंबई"},
    
    # Profile
    "Profile": {"hi": "प्रोफाइल", "mr": "प्रोफाइल"},
    "Verified Professional": {"hi": "सत्यापित पेशेवर", "mr": "सत्यापित व्यावसायिक"},
    "Expected Salary": {"hi": "अपेक्षित वेतन", "mr": "अपेक्षित पगार"},
    "Mobile Number": {"hi": "मोबाइल नंबर", "mr": "मोबाइल नंबर"},
    "Expertise & Skills": {"hi": "विशेषज्ञता और कौशल", "mr": "विशेषज्ञता आणि कौशल्ये"},
    "Booking feature coming soon!": {"hi": "बुकिंग सुविधा जल्द ही आ रही है!", "mr": "बुकिंग सुविधा लवकरच येत आहे!"},
    "Proceed to Hire": {"hi": "हायर करने के लिए आगे बढ़ें", "mr": "नेमण्यासाठी पुढे जा"},
    "Back to Listings": {"hi": "लिस्टिंग पर वापस जाएं", "mr": "यादीवर परत जा"},
    "Documents of this profile are verified by our team. For safety reasons, direct downloads are not available for customers.": {"hi": "इस प्रोफाइल के दस्तावेजों को हमारी टीम द्वारा सत्यापित किया गया है। सुरक्षा कारणों से, ग्राहकों के लिए सीधे डाउनलोड उपलब्ध नहीं हैं।", "mr": "या प्रोफाइलचे दस्तऐवज आमच्या टीमने सत्यापित केले आहेत. सुरक्षिततेच्या कारणास्तव, ही कागदपत्रे ग्राहकांसाठी थेट उपलब्ध नाहीत."},
    "Email Address": {"hi": "ईमेल पता", "mr": "ईमेल पत्ता"},
    "Send Email": {"hi": "ईमेल भेजें", "mr": "ईमेल पाठवा"},
    
    # Register Maid
    "Register as Maid": {"hi": "मेड के रूप में रजिस्टर करें", "mr": "मोलकरीण म्हणून नोंदणी करा"},
    "Maid Registration Form": {"hi": "मेड पंजीकरण फॉर्म", "mr": "मोलकरीण नोंदणी फॉर्म"},
    "Fill in your details to join our network of experts": {"hi": "विशेषज्ञों के हमारे नेटवर्क में शामिल होने के लिए अपना विवरण भरें", "mr": "आमच्या तज्ञांच्या नेटवर्कमध्ये सामील होण्यासाठी आपले तपशील भरा"},
    "Email Address (Read-only)": {"hi": "ईमेल पता (केवल पढ़ने के लिए)", "mr": "ईमेल पत्ता (केवळ वाचण्यासाठी)"},
    "Expected Monthly Salary (₹)": {"hi": "अपेक्षित मासिक वेतन (₹)", "mr": "अपेक्षित मासिक पगार (₹)"},
    "Aadhaar Document (PDF/JPG/PNG)": {"hi": "आधार दस्तावेज (PDF/JPG/PNG)", "mr": "आधार दस्तऐवज (PDF/JPG/PNG)"},
    "Police Verification (PDF/JPG/PNG)": {"hi": "पुलिस सत्यापन (PDF/JPG/PNG)", "mr": "पोलीस पडताळणी (PDF/JPG/PNG)"},
    "Submit Registration": {"hi": "पंजीकरण जमा करें", "mr": "नोंदणी जमा करा"},
    
    # Forms
    "Enter your full name": {"hi": "अपना पूरा नाम दर्ज करें", "mr": "आपले पूर्ण नाव प्रविष्ट करा"},
    "Enter mobile number": {"hi": "मोबाइल नंबर दर्ज करें", "mr": "मोबाइल नंबर प्रविष्ट करा"},
    "Enter your location": {"hi": "अपना स्थान दर्ज करें", "mr": "आपले स्थान प्रविष्ट करा"},
    "Enter expected monthly salary": {"hi": "अपेक्षित मासिक वेतन दर्ज करें", "mr": "अपेक्षित मासिक पगार प्रविष्ट करा"},
    
    "Cleaning": {"hi": "सफाई", "mr": "साफसफाई"},
    "Cooking": {"hi": "खाना पकाना", "mr": "स्वयंपाक"},
    "Babysitting": {"hi": "बच्चा संभालना (Babysitting)", "mr": "मुलांचा सांभाळ (Babysitting)"},
    "Elder Care": {"hi": "बुजुर्गों की देखभाल", "mr": "वृद्धांची काळजी"},
    "Laundry": {"hi": "कपड़े धोना", "mr": "कपडे धुणे"},
    "Other Household Work": {"hi": "अन्य घरेलू काम", "mr": "इतर घरगुती काम"},
    "Skills": {"hi": "कौशल", "mr": "कौशल्ये"},
    
    "Aadhaar Document": {"hi": "आधार दस्तावेज", "mr": "आधार दस्तऐवज"},
    "Police Verification": {"hi": "पुलिस सत्यापन", "mr": "पोलीस पडताळणी"},
    
    # Views Messages
    "You have already registered as a maid.": {"hi": "आप पहले ही एक मेड के रूप में पंजीकृत हैं।", "mr": "तुम्ही आधीच मोलकरीण म्हणून नोंदणी केली आहे."},
    "Registered as Maid Successfully. Admin will verify your profile soon.": {"hi": "मेड के रूप में सफलतापूर्वक पंजीकृत किया गया। व्यवस्थापक जल्द ही आपकी प्रोफ़ाइल सत्यापित करेगा।", "mr": "मोलकरीण म्हणून यशस्वीरित्या नोंदणीकृत. प्रशासक लवकरच आपल्या प्रोफाइलची पडताळणी करेल."},
    "Passwords do not match.": {"hi": "पासवर्ड मेल नहीं खाते।", "mr": "पासवर्ड जुळत नाहीत."},
    "Email already registered.": {"hi": "ईमेल पहले से पंजीकृत है।", "mr": "ईमेल आधीच नोंदणीकृत आहे."},
    "Account created successfully. Please sign in.": {"hi": "खाता सफलतापूर्वक बनाया गया। कृपया साइन इन करें।", "mr": "खाते यशस्वीरित्या तयार केले. कृपया साइन इन करा."},
    "Invalid email or password.": {"hi": "अमान्य ईमेल या पासवर्ड।", "mr": "अवैध ईमेल किंवा पासवर्ड."},

    # Admin Dashboard
    "Admin Dashboard": {"hi": "एडमिन डैशबोर्ड", "mr": "प्रशासक डॅशबोर्ड"},
    "Manage users, maids, and verifications": {"hi": "उपयोगकर्ताओं, मेड और सत्यापन का प्रबंधन करें", "mr": "वापरकर्ते, मोलकरीण आणि पडताळणी व्यवस्थापित करा"},
    "Total Users": {"hi": "कुल उपयोगकर्ता", "mr": "एकूण वापरकर्ते"},
    "All registered users": {"hi": "सभी पंजीकृत उपयोगकर्ता", "mr": "सर्व नोंदणीकृत वापरकर्ते"},
    "Customers": {"hi": "ग्राहक", "mr": "ग्राहक"},
    "Hiring for services": {"hi": "सेवाओं के लिए हायरिंग", "mr": "सेवांसाठी भरती"},
    "Verified Maids": {"hi": "सत्यापित मेड्स", "mr": "सत्यापित मोलकरीण"},
    "Approved profiles": {"hi": "अनुमोदित प्रोफाइल", "mr": "मंजूर प्रोफाइल"},
    "Pending Approval": {"hi": "अनुमोदन लंबित", "mr": "मंजुरी प्रलंबित"},
    "Needs verification": {"hi": "सत्यापन की आवश्यकता है", "mr": "पडताळणी आवश्यक आहे"},

    # User List
    "Name": {"hi": "नाम", "mr": "नाव"},
    "Email": {"hi": "ईमेल", "mr": "ईमेल"},
    "Action": {"hi": "कार्रवाई", "mr": "कृती"},
    "Back to Dashboard": {"hi": "डैशबोर्ड पर वापस जाएं", "mr": "डॅशबोर्डवर परत जा"},
    "View": {"hi": "देखें", "mr": "पहा"},
    "Not Provided": {"hi": "प्रदान नहीं किया गया", "mr": "दिलेले नाही"},
    "No users found in this category.": {"hi": "इस श्रेणी में कोई उपयोगकर्ता नहीं मिला।", "mr": "या श्रेणीमध्ये कोणतेही वापरकर्ते आढळले नाहीत."},
    "Unverified Maids": {"hi": "असत्यापित मेड्स", "mr": "असत्यापित मोलकरीण"},

    # Maid Detail / Verification
    "Maid Verification": {"hi": "मेड सत्यापन", "mr": "मोलकरीण पडताळणी"},
    "Pending Review": {"hi": "समीक्षा लंबित", "mr": "पुनरावलोकन प्रलंबित"},
    "Expected Salary": {"hi": "अपेक्षित वेतन", "mr": "अपेक्षित पगार"},
    "View / Download": {"hi": "देखें / डाउनलोड करें", "mr": "पहा / डाउनलोड करा"},
    "Approve Registration": {"hi": "पंजीकरण स्वीकृत करें", "mr": "नोंदणी मंजूर करा"},
    "Reject Registration": {"hi": "पंजीकरण अस्वीकार करें", "mr": "नोंदणी नाकारा"},
    "Back to Pending List": {"hi": "लंबित सूची पर वापस जाएं", "mr": "प्रलंबित यादीवर परत जा"},

    # User Profile
    "User Profile": {"hi": "उपयोगकर्ता प्रोफाइल", "mr": "वापरकर्ता प्रोफाइल"},
}


def compile_dict_to_mo(translations, mo_file_path):
    """
    Compiles a translation dictionary directly to a .mo file.
    """
    # Prepare messages with header
    MESSAGES = translations.copy()
    
    # Ensure header is present and correct
    header = (
        'MIME-Version: 1.0\n'
        'Content-Type: text/plain; charset=UTF-8\n'
        'Content-Transfer-Encoding: 8bit\n'
    )
    MESSAGES[''] = header

    # MO File Generation
    magic = 0x950412de
    version = 0
    num_strings = len(MESSAGES)
    
    keys = sorted(MESSAGES.keys())
    
    ids_offset = 28
    strs_offset = ids_offset + (num_strings * 8)
    
    ids_data = b""
    strs_data = b""
    
    current_data_offset = strs_offset + (num_strings * 8)
    data_buffer = b""
    
    otable = []
    ttable = []
    
    for msgid in keys:
        msgstr = MESSAGES[msgid]
        
        msgid_bytes = msgid.encode('utf-8') + b'\0'
        msgstr_bytes = msgstr.encode('utf-8') + b'\0'
        
        otable.append((len(msgid_bytes) - 1, current_data_offset))
        data_buffer += msgid_bytes
        current_data_offset += len(msgid_bytes)
        
        ttable.append((len(msgstr_bytes) - 1, current_data_offset))
        data_buffer += msgstr_bytes
        current_data_offset += len(msgstr_bytes)

    with open(mo_file_path, 'wb') as f:
        f.write(struct.pack('I', magic))
        f.write(struct.pack('I', version))
        f.write(struct.pack('I', num_strings))
        f.write(struct.pack('I', ids_offset))
        f.write(struct.pack('I', strs_offset))
        f.write(struct.pack('I', 0))
        f.write(struct.pack('I', 0))
        
        for length, offset in otable:
            f.write(struct.pack('II', length, offset))
            
        for length, offset in ttable:
            f.write(struct.pack('II', length, offset))
            
        f.write(data_buffer)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locale_dir = os.path.join(base_dir, 'locale')
    ensure_dir(locale_dir)
    
    languages = ['hi', 'mr']
    
    for lang in languages:
        lang_dir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
        ensure_dir(lang_dir)
        
        # Prepare translations dict for this language
        translations = {k: v[lang] for k, v in base_translations.items() if lang in v}
        
        # Write PO (Optional but good for debug)
        po_path = os.path.join(lang_dir, 'django.po')
        po_content = generate_po_file(lang, translations)
        with open(po_path, 'w', encoding='utf-8') as f:
            f.write(po_content)
        print(f"Generated {po_path}")
        
        # Compile directly to MO
        mo_path = os.path.join(lang_dir, 'django.mo')
        try:
            compile_dict_to_mo(translations, mo_path)
            print(f"Compiled {mo_path}")
        except Exception as e:
            print(f"Error compiling {lang}: {e}")

if __name__ == "__main__":
    main()
