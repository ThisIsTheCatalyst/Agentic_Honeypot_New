import random

TEMPLATES = {
    "english": {
        "delay": [
            "Wait a second, I’m trying to understand this.",
            "Give me a moment, this is confusing.",
            "I’m not sure what you mean yet.",
            "Can you explain this step by step?",
            "I need a minute to check something.",
            "This is a bit unclear to me.",
            "Hold on, I’m trying to figure this out.",
            "Let me understand properly first."
        ],

        "verify_claim": [
            "Why is this happening all of a sudden?",
            "I didn’t receive any bank message about this.",
            "Which bank branch are you calling from?",
            "Can you explain why my account is affected?",
            "This doesn’t make sense to me yet.",
            "How did this issue start?",
            "Why wasn’t I informed earlier?",
            "Are you sure this is related to my account?"
        ],

        "extract_payment": [
            "Why do you need my UPI ID for this?",
            "How will sharing my UPI help here?",
            "Is there any other way to resolve this?",
            "I don’t understand why payment details are needed.",
            "What exactly am I supposed to send?",
            "Why is UPI involved in this issue?"
        ],

        "extract_identity": [
            "Who exactly are you calling from?",
            "Can you tell me your department name?",
            "Is there any official reference number?",
            "How can I verify your identity?",
            "Which office are you representing?",
            "Can you explain your role clearly?"
        ],

        "extract_bank": [
            "Which bank account are you talking about?",
            "What bank is this related to?",
            "Is this savings or current account?",
            "Can you tell me which bank branch this is?",
            "Why is my bank account involved here?"
        ],

        "terminate": [
            "I don’t think I’m comfortable continuing this.",
            "I’ll check this directly with my bank.",
            "I’m ending this conversation now.",
            "I’ll verify this through official channels.",
            "I don’t want to proceed further."
        ]
    },

    "hinglish": {
        "delay": [
            "Ek minute ruko, samajhne do.",
            "Thoda time do, ye clear nahi hai.",
            "Main abhi samajh nahi pa raha hoon.",
            "Zara detail mein batao na.",
            "Ruko, main check kar raha hoon.",
            "Abhi clear nahi lag raha mujhe.",
            "Thoda ruk jao, main dekh raha hoon.",
            "Ek second, ye confuse kar raha hai."
        ],

        "verify_claim": [
            "Ye achanak kaise ho gaya?",
            "Mujhe bank se koi message nahi aaya.",
            "Aap kaunse branch se bol rahe ho?",
            "Mera account ismein kaise aa gaya?",
            "Ye sab ka reason kya hai?",
            "Pehle aisa kabhi nahi hua.",
            "Aapne pehle inform kyun nahi kiya?",
            "Ye kaise confirm ho raha hai?"
        ],

        "extract_payment": [
            "UPI ID kyun chahiye iske liye?",
            "UPI dene se problem kaise solve hogi?",
            "Iske liye payment detail kyun lag rahi hai?",
            "Mujhe samajh nahi aa raha UPI ka role.",
            "Main kya bheju exactly?",
            "UPI ka kya kaam hai ismein?"
        ],

        "extract_identity": [
            "Aap exactly kaun bol rahe ho?",
            "Aapka department ka naam kya hai?",
            "Koi official ID ya reference number hai?",
            "Main kaise verify karun aapko?",
            "Aap kaunsi office se ho?",
            "Aap apna role clearly batao."
        ],

        "extract_bank": [
            "Kaunsa bank account ki baat ho rahi hai?",
            "Ye kis bank se related hai?",
            "Savings account hai ya current?",
            "Kaunsi branch ka issue hai?",
            "Mera bank account kyun involve ho raha hai?"
        ],

        "terminate": [
            "Mujhe lagta hai main aage baat nahi karunga.",
            "Main direct bank se confirm karunga.",
            "Main ye conversation yahin end karta hoon.",
            "Main official channel se check karunga.",
            "Ab main proceed nahi karna chahta."
        ]
    }
}


def get_template_reply(strategy, language, used_lines):
    # 🔒 Safety fallback
    language = language if language in TEMPLATES else "english"
    strategy = strategy if strategy in TEMPLATES[language] else "delay"

    options = [
        line for line in TEMPLATES[language][strategy]
        if line not in used_lines
    ]

    if not options:
        options = TEMPLATES[language][strategy]

    return random.choice(options)
