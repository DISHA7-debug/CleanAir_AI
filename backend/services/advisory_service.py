# Citizen advisory service containing recommendations per AQI category in multiple languages

ADVISORIES = {
    "good": {
        "en": "Air quality is satisfactory, and air pollution poses little or no risk. Safe for outdoor activities.",
        "hi": "वायु गुणवत्ता संतोषजनक है, और वायु प्रदूषण से कोई खतरा नहीं है। बाहरी गतिविधियों के लिए सुरक्षित।",
        "ta": "[Needs Review] காற்றின் தரம் திருப்திகரமாக உள்ளது. வெளிப்புற நடவடிக்கைகளுக்கு பாதுகாப்பானது.",
        "kn": "[Needs Review] ವಾಯು ಗುಣಮಟ್ಟವು ತೃಪ್ತಿಕರವಾಗಿದೆ. ಹೊರಾಂಗಣ ಚಟುವಟಿಕೆಗಳಿಗೆ ಸುರಕ್ಷಿತವಾಗಿದೆ.",
        "bn": "[Needs Review] বাতাসের মান সন্তোষজনক। বাইরের ক্রিয়াকলাপের জন্য নিরাপদ।",
        "mr": "[Needs Review] हवेची गुणवत्ता समाधानकारक आहे. मैदानी क्रियाकलापांसाठी सुरक्षित.",
        "te": "[Needs Review] గాలి నాణ్యత సంతృప్తికరంగా ఉంది. బహిరంగ కార్యకలాపాలకు సురక్షితం."
    },
    "satisfactory": {
        "en": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
        "hi": "वायु गुणवत्ता स्वीकार्य है। हालांकि, कुछ लोगों के लिए विशेष रूप से संवेदनशील लोगों के लिए जोखिम हो सकता है।",
        "ta": "[Needs Review] காற்றின் தரம் ஏற்றுக்கொள்ளத்தக்கது. இருப்பினும், சிலருக்கு ஆபத்து ஏற்படலாம்.",
        "kn": "[Needs Review] ವಾಯು ಗುಣಮಟ್ಟವು ಸ್ವೀಕಾರಾರ್ಹವಾಗಿದೆ. ಆದಾಗ್ಯೂ, ಕೆಲವು ಜನರಿಗೆ ಅಪಾಯವಿರಬಹುದು.",
        "bn": "[Needs Review] বাতাসের মান গ্রহণযোগ্য। তবে কিছু মানুষের জন্য ঝুঁকি থাকতে পারে।",
        "mr": "[Needs Review] हवेची गुणवत्ता स्वीकार्य आहे. तथापि, काही लोकांसाठी धोका असू शकतो.",
        "te": "[Needs Review] గాలి నాణ్యత ఆమోదయోగ్యంగా ఉంది. అయితే, కొంతమందికి ప్రమాదం ఉండవచ్చు."
    },
    "moderate": {
        "en": "Members of sensitive groups may experience health effects. The general public is less likely to be affected. Consider reducing heavy outdoor exertion.",
        "hi": "संवेदनशील समूहों के लोगों को स्वास्थ्य संबंधी प्रभाव महसूस हो सकते हैं। आम जनता के प्रभावित होने की संभावना कम है। बाहरी व्यायाम कम करें।",
        "ta": "[Needs Review] உணர்திறன் குழுக்கள் சுகாதார விளைவுகளை சந்திக்கலாம். வெளிப்புற உழைப்பைக் குறைக்கவும்.",
        "kn": "[Needs Review] ಸೂಕ್ಷ್ಮ ಗುಂಪುಗಳ ಜನರು ಆರೋಗ್ಯದ ಮೇಲೆ ಪರಿಣಾಮ ಬೀರಬಹುದು. ಹೊರಾಂಗಣ ಪರಿಶ್ರಮವನ್ನು ಕಡಿಮೆ ಮಾಡಿ.",
        "bn": "[Needs Review] সংবেদনশীল গোষ্ঠীর মানুষ স্বাস্থ্যগত প্রভাব অনুভব করতে পারে। বাইরের পরিশ্রম কমান।",
        "mr": "[Needs Review] संवेदनशील गटांना आरोग्यावर परिणाम जाणवू शकतात. जास्त शारीरिक कष्ट कमी करा.",
        "te": "[Needs Review] సున్నితమైన సమూహాల ప్రజలు ఆరోగ్య ప్రభావాలను అనుభవించవచ్చు. బహిరంగ శ్రమను తగ్గించండి."
    },
    "poor": {
        "en": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects. Avoid prolonged outdoor exertion.",
        "hi": "सभी को स्वास्थ्य संबंधी प्रभाव महसूस होने लग सकते हैं; संवेदनशील समूहों को अधिक गंभीर प्रभाव हो सकते हैं। लंबे समय तक बाहरी गतिविधियों से बचें।",
        "ta": "[Needs Review] அனைவரும் சுகாதார விளைவுகளை சந்திக்க ஆரம்பிக்கலாம். நீண்ட வெளிப்புற உழைப்பைத் தவிர்க்கவும்.",
        "kn": "[Needs Review] ಪ್ರತಿಯೊಬ್ಬರೂ ಆರೋಗ್ಯದ ಮೇಲೆ ಪರಿಣಾಮ ಬೀರಲು ಪ್ರಾರಂಭಿಸಬಹುದು. ಸುದೀರ್ಘ ಹೊರಾಂಗಣ ಶ್ರಮವನ್ನು ತಪ್ಪಿಸಿ.",
        "bn": "[Needs Review] সবাই স্বাস্থ্যগত প্রভাব অনুভব করতে শুরু করতে পারে। দীর্ঘায়িত বাইরের পরিশ্রম এড়িয়ে চলুন।",
        "mr": "[Needs Review] प्रत्येकाला आरोग्यावर परिणाम जाणवू शकतात. जास्त वेळ बाहेर फिरणे टाळा.",
        "te": "[Needs Review] ప్రతి ఒక్కరూ ఆరోగ్య ప్రభావాలను అనుభవించడం ప్రారంభించవచ్చు. ఎక్కువ సేపు బహిరంగ శ్రమను నివారించండి."
    },
    "very poor": {
        "en": "Health alert: everyone may experience more serious health effects. Outdoor activities should be restricted, especially for children and the elderly.",
        "hi": "स्वास्थ्य चेतावनी: सभी को अधिक गंभीर स्वास्थ्य प्रभाव महसूस हो सकते हैं। बाहरी गतिविधियों को प्रतिबंधित किया जाना चाहिए, विशेषकर बच्चों और बुजुर्गों के लिए।",
        "ta": "[Needs Review] சுகாதார எச்சரிக்கை: அனைவரும் தீவிர சுகாதார விளைவுகளை சந்திக்கலாம். வெளிப்புற நடவடிக்கைகளை கட்டுப்படுத்தவும்.",
        "kn": "[Needs Review] ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆ: ಪ್ರತಿಯೊಬ್ಬರೂ ತೀವ್ರ ಆರೋಗ್ಯದ ಪರಿಣಾಮಗಳನ್ನು ಎದುರಿಸಬಹುದು. ಹೊರಾಂಗಣ ಚಟುವಟಿಕೆಗಳನ್ನು ಮಿತಿಗೊಳಿಸಿ.",
        "bn": "[Needs Review] স্বাস্থ্য সতর্কতা: সবাই মারাত্মক স্বাস্থ্যগত প্রভাবের সম্মুখীন হতে পারে। বাইরের ক্রিয়াকলাপ সীমিত করুন।",
        "mr": "[Needs Review] आरोग्य इशारा: प्रत्येकाला गंभीर आरोग्याचे परिणाम जाणवू शकतात. मैदानी क्रियाकलाप मर्यादित करा.",
        "te": "[Needs Review] ఆరోగ్య హెచ్చరిక: ప్రతి ఒక్కరూ తీవ్రమైన ఆరోగ్య ప్రభావాలను అనుభవించవచ్చు. బహిరంగ కార్యకలాపాలను పరిమితం చేయండి."
    },
    "severe": {
        "en": "Health warning of emergency conditions: everyone is more likely to be affected. Avoid all outdoor physical activity. Remain indoors.",
        "hi": "आपातकालीन स्थितियों की स्वास्थ्य चेतावनी: सभी के प्रभावित होने की अधिक संभावना है। सभी बाहरी गतिविधियों से बचें और घर के भीतर रहें।",
        "ta": "[Needs Review] அவசர சுகாதார எச்சரிக்கை: அனைவரும் பாதிக்கப்படலாம். வெளிப்புற உடற்பயிற்சிகளை முற்றிலும் தவிர்க்கவும்.",
        "kn": "[Needs Review] ತುರ್ತು ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆ: ಪ್ರತಿಯೊಬ್ಬರೂ ಬಾಧಿತರಾಗಬಹುದು. ಹೊರಾಂಗಣ ದೈಹಿಕ ಚಟುವಟಿಕೆಗಳನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ತಪ್ಪಿಸಿ.",
        "bn": "[Needs Review] জরুরি স্বাস্থ্য সতর্কতা: সবাই আক্রান্ত হতে পারে। বাইরের সমস্ত শারীরিক ক্রিয়াকলাপ এড়িয়ে চলুন।",
        "mr": "[Needs Review] आणीबाणीचा इशारा: प्रत्येकावर परिणाम होण्याची शक्यता जास्त. सर्व मैदानी क्रियाकलाप टाळा.",
        "te": "[Needs Review] అత్యవసర ఆరోగ్య హెచ్చరిక: ప్రతి ఒక్కరూ ప్రభావితం కావచ్చు. బహిరంగ శారీరక శ్రమను పూర్తిగా నివారించండి."
    }
}

def get_advisory(aqi_category: str, lang: str = "en") -> dict:
    """
    Returns the advisory message for a given AQI category and language.
    If the language is not supported or missing, falls back to English.
    """
    normalized_category = aqi_category.strip().lower()
    normalized_lang = lang.strip().lower()

    # Fallback to English if category not found (should not happen for valid categories)
    if normalized_category not in ADVISORIES:
        # Check if maybe category needs mapping, e.g. "very_poor" -> "very poor"
        mapped_category = normalized_category.replace("_", " ")
        if mapped_category in ADVISORIES:
            normalized_category = mapped_category
        else:
            # return fallback for Good
            normalized_category = "good"
    
    category_advisories = ADVISORIES[normalized_category]
    
    # Fallback to English if language is not supported
    selected_lang = normalized_lang if normalized_lang in category_advisories else "en"
    
    return {
        "aqi_category": aqi_category,
        "language": selected_lang,
        "advisory": category_advisories[selected_lang]
    }
