"""MCC डेटा: ISO 18245 का एक प्रारंभिक उपसमुच्चय, भारतीय keywords के साथ।

ये कोड और नाम शुरुआती सूची हैं। उपयोग से पहले इन्हें आधिकारिक ISO 18245 सूची
और अपने acquirer के दस्तावेज़ों से मिला लें।
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MccEntry:
    code: str
    name: str            # अंग्रेज़ी नाम, संदर्भ के लिए
    hindi: str           # हिंदी लेबल
    keywords: tuple      # नाम या narration में खोजे जाने वाले शब्द (lowercase)


MCC_TABLE = (
    MccEntry("0742", "Veterinary Services", "पशु चिकित्सा", ("veterinary", "vet clinic", "पशु चिकित्सा", "पशु अस्पताल")),
    MccEntry("3020", "Airlines", "एयरलाइन", ("airline", "airways", "flight", "एयरलाइन")),
    MccEntry("4111", "Local and Suburban Commuter Transport", "स्थानीय परिवहन", ("metro", "local train", "suburban", "मेट्रो")),
    MccEntry("4112", "Passenger Railways", "रेलवे", ("railway", "railways", "irctc", "रेलवे")),
    MccEntry("4121", "Taxicabs and Limousines", "टैक्सी", ("taxi", "cab", "टैक्सी")),
    MccEntry("4131", "Bus Lines", "बस सेवा", ("bus", "redbus", "abhibus", "बस")),
    MccEntry("4215", "Courier Services", "कूरियर", ("courier", "logistics", "shipping", "कूरियर")),
    MccEntry("4722", "Travel Agencies and Tour Operators", "यात्रा एजेंसी", ("travel", "tours", "tour operator", "holidays", "यात्रा")),
    MccEntry("4814", "Telecommunication Services", "दूरसंचार", ("telecom", "mobile recharge", "airtel", "jio", "vodafone", "बीएसएनएल", "मोबाइल रिचार्ज")),
    MccEntry("4900", "Utilities", "बिजली, पानी, गैस बिल", ("electricity", "water bill", "gas bill", "utility", "बिजली", "पानी बिल")),
    MccEntry("5411", "Grocery Stores, Supermarkets", "किराना और सुपरमार्केट", ("grocery", "kirana", "supermarket", "provision", "किराना")),
    MccEntry("5541", "Service Stations", "पेट्रोल पंप", ("petrol", "petrol pump", "fuel", "service station", "पेट्रोल", "पेट्रोल पंप")),
    MccEntry("5651", "Family Clothing Stores", "कपड़ों की दुकान", ("clothing", "garments", "apparel", "boutique", "कपड़े")),
    MccEntry("5732", "Electronics Stores", "इलेक्ट्रॉनिक्स", ("electronics", "mobile shop", "computer shop", "इलेक्ट्रॉनिक्स")),
    MccEntry("5812", "Eating Places, Restaurants", "रेस्टोरेंट और ढाबा", ("restaurant", "dhaba", "cafe", "bhojanalaya", "ढाबा", "रेस्टोरेंट", "होटल")),
    MccEntry("5814", "Fast Food Restaurants", "फास्ट फ़ूड", ("fast food", "pizza", "burger", "roll", "chaat", "चाट")),
    MccEntry("5912", "Drug Stores, Pharmacies", "दवा दुकान", ("pharmacy", "medical", "medicals", "chemist", "dawai", "मेडिकल", "दवाई", "दवा")),
    MccEntry("5999", "Miscellaneous and Specialty Retail Stores", "विविध खुदरा दुकान", ()),
    MccEntry("6012", "Financial Institutions", "वित्तीय संस्थान", ("loan", "emi", "nbfc", "लोन", "ईएमआई")),
    MccEntry("6300", "Insurance Sales, Underwriting", "बीमा", ("insurance", "premium", "बीमा")),
    MccEntry("7011", "Hotels, Motels, Resorts", "होटल और रिसॉर्ट", ("hotel", "resort", "lodge", "guest house", "होटल", "रिसॉर्ट")),
    MccEntry("7322", "Debt Collection Agencies", "वसूली एजेंसी", ("debt collection", "recovery agency", "वसूली")),
    MccEntry("7832", "Motion Picture Theaters", "सिनेमा", ("cinema", "movie", "multiplex", "theatre", "सिनेमा")),
    MccEntry("8062", "Hospitals", "अस्पताल", ("hospital", "nursing home", "अस्पताल")),
    MccEntry("8099", "Medical Services and Health Practitioners", "स्वास्थ्य सेवा", ("clinic", "diagnostic", "diagnostics", "lab", "dental", "doctor", "क्लिनिक", "लैब")),
    MccEntry("8211", "Elementary and Secondary Schools", "स्कूल", ("school", "vidyalaya", "स्कूल", "विद्यालय")),
    MccEntry("8220", "Colleges and Universities", "कॉलेज और विश्वविद्यालय", ("college", "university", "institute", "कॉलेज", "विश्वविद्यालय")),
    MccEntry("8398", "Charitable and Social Service Organizations", "दान और सामाजिक संस्था", ("donation", "charity", "trust", "ngo", "दान")),
    MccEntry("9311", "Tax Payments", "कर भुगतान", ("tax", "income tax", "gst payment", "कर")),
    MccEntry("9399", "Government Services", "सरकारी सेवा", ("government", "municipal", "govt", "सरकारी", "नगर निगम")),
)

BY_CODE = {entry.code: entry for entry in MCC_TABLE}
