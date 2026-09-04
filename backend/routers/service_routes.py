from fastapi import APIRouter, Query
from typing import List, Dict, Any

router = APIRouter(prefix="/api/service", tags=["service"])

CSI_CONTENT = {
    "sunday": {
        "en": [
            {
                "section": "Preparation & Invocation",
                "type": "static",
                "content": "<p><strong>Minister:</strong> Peace be with you.</p><p><strong>Congregation:</strong> And also with you.</p><p><em>(The congregation stands)</em></p><p><strong>Minister:</strong> This is the day that the LORD has made;<br><strong>Congregation:</strong> Let us rejoice and be glad in it.</p><p><strong>Minister:</strong> Let us pray.<br>Almighty God, to whom all hearts are open, all desires known, and from whom no secrets are hid: Cleanse the thoughts of our hearts by the inspiration of your Holy Spirit, that we may perfectly love you, and worthily magnify your holy name; through Christ our Lord. <strong>Amen.</strong></p>"
            },
            {
                "section": "Hymn of Praise",
                "type": "static",
                "content": "<p><em>(The congregation stands to sing the opening hymn of praise.)</em></p><p><strong>Guide:</strong> Choose a hymn that focuses on God's majesty, creation, or the theme of the Sunday (e.g., 'Holy, Holy, Holy' or 'Praise to the Lord, the Almighty').</p>"
            },
            {
                "section": "Confession of Sin",
                "type": "static",
                "content": "<p><em>(The congregation kneels or sits)</em></p><p><strong>Minister:</strong> God is light, and in Him is no darkness at all. If we claim to have fellowship with Him yet walk in the darkness, we lie and do not live by the truth. But if we walk in the light, as He is in the light, we have fellowship with one another, and the blood of Jesus, His Son, purifies us from all sin.</p><p>Let us confess our sins to God.</p><p><strong>All:</strong> Almighty and most merciful Father, we have erred and strayed from your ways like lost sheep. We have followed too much the devices and desires of our own hearts. We have offended against your holy laws. We have left undone those things which we ought to have done; and we have done those things which we ought not to have done; and there is no health in us. But you, O Lord, have mercy upon us, miserable offenders. Spare those, O God, who confess their faults. Restore those who are penitent; according to your promises declared unto mankind in Christ Jesus our Lord. And grant, O most merciful Father, for his sake, that we may hereafter live a godly, righteous, and sober life, to the glory of your holy name. <strong>Amen.</strong></p>"
            },
            {
                "section": "Absolution (Declaration of Forgiveness)",
                "type": "static",
                "content": "<p><strong>Minister:</strong> Almighty God, the Father of our Lord Jesus Christ, who desires not the death of a sinner, but rather that he may turn from his wickedness and live, has given power and commandment to his ministers to declare and pronounce to his people, being penitent, the absolution and remission of their sins. He pardons and absolves all those who truly repent and unfeignedly believe his holy gospel.</p><p>Wherefore let us beseech him to grant us true repentance, and his Holy Spirit, that those things may please him which we do at this present; and that the rest of our life hereafter may be pure and holy; so that at the last we may come to his eternal joy; through Jesus Christ our Lord. <strong>Amen.</strong></p>"
            },
            {
                "section": "The Apostles' Creed",
                "type": "static",
                "content": "<p><em>(The congregation stands)</em></p><p><strong>All:</strong><br>I believe in God, the Father almighty,<br>creator of heaven and earth.<br><br>I believe in Jesus Christ, his only Son, our Lord,<br>who was conceived by the Holy Spirit,<br>born of the Virgin Mary,<br>suffered under Pontius Pilate,<br>was crucified, died, and was buried;<br>he descended to the dead.<br>On the third day he rose again;<br>he ascended into heaven,<br>he is seated at the right hand of the Father,<br>and he will come to judge the living and the dead.<br><br>I believe in the Holy Spirit,<br>the holy catholic Church,<br>the communion of saints,<br>the forgiveness of sins,<br>the resurrection of the body,<br>and the life everlasting.<br><strong>Amen.</strong></p>"
            },
            {
                "section": "Old Testament Lesson",
                "type": "scripture",
                "reference": "Isaiah 40:1"
            },
            {
                "section": "Responsive Reading (Psalm)",
                "type": "scripture",
                "reference": "Psalm 23:1"
            },
            {
                "section": "Epistle (New Testament) Lesson",
                "type": "scripture",
                "reference": "Romans 12:1"
            },
            {
                "section": "The Gospel Reading",
                "type": "scripture",
                "reference": "John 3:16",
                "intro": "<p><em>(The congregation stands)</em></p><p><strong>Minister:</strong> Hear the holy Gospel.<br><strong>Congregation:</strong> Glory to you, O Lord.</p>",
                "outro": "<p><strong>Minister:</strong> This is the Gospel of the Lord.<br><strong>Congregation:</strong> Praise to you, O Christ.</p>"
            },
            {
                "section": "The Sermon",
                "type": "static",
                "content": "<p><em>(The preacher delivers the sermon based on the scripture readings of the day.)</em></p><p><strong>Preacher:</strong> May the words of my mouth and the meditation of our hearts be acceptable in your sight, O LORD, our Rock and our Redeemer. Amen.</p><p><em>Use the Sermon Builder tool above to generate a structured sermon outline for today's Scripture passage.</em></p>"
            },
            {
                "section": "The Lord's Prayer",
                "type": "static",
                "content": "<p><strong>All:</strong><br>Our Father in heaven,<br>hallowed be your name,<br>your kingdom come,<br>your will be done,<br>on earth as in heaven.<br>Give us today our daily bread.<br>Forgive us our sins<br>as we forgive those who sin against us.<br>Lead us not into temptation<br>but deliver us from evil.<br>For the kingdom, the power,<br>and the glory are yours<br>now and for ever. <strong>Amen.</strong></p>"
            },
            {
                "section": "Intercessory Prayers",
                "type": "static",
                "content": "<p><em>(The congregation kneels or sits)</em></p><p><strong>Minister:</strong> Let us pray for the Church and for the world.<br>Grant, Almighty God, that all who confess your Name may be united in your truth, live together in your love, and reveal your glory in the world.<br>Lord, in your mercy.<br><strong>Congregation:</strong> Hear our prayer.</p><p><strong>Minister:</strong> Guide the people of this land, and of all the nations, in the ways of justice and peace; that we may honor one another and serve the common good.<br>Lord, in your mercy.<br><strong>Congregation:</strong> Hear our prayer.</p><p><em>(Additional petitions for the sick, the poor, and the local community may be added.)</em></p><p><strong>Minister:</strong> Hasten, O Father, the coming of your kingdom; and grant that we your servants, who now live by faith, may with joy behold your Son at his coming in glorious majesty; even Jesus Christ, our only Mediator and Advocate. <strong>Amen.</strong></p>"
            },
            {
                "section": "Offertory",
                "type": "static",
                "content": "<p><em>(The congregation sings an offertory hymn while the tithes and offerings are collected.)</em></p><p><strong>Minister:</strong> Let us present our offerings to the Lord with joy and thanksgiving.</p><p><em>(When the offering is brought forward, the congregation stands.)</em></p><p><strong>All:</strong> All things come from you, O Lord, and of your own have we given you. Accept these offerings, and ourselves, as a living sacrifice of praise and thanksgiving, through Jesus Christ our Lord. <strong>Amen.</strong></p>"
            },
            {
                "section": "Benediction & Closing",
                "type": "static",
                "content": "<p><strong>Minister:</strong> The peace of God, which passes all understanding, keep your hearts and minds in the knowledge and love of God, and of his Son Jesus Christ our Lord; and the blessing of God Almighty, the Father, the Son, and the Holy Spirit, be among you, and remain with you always.</p><p><strong>Congregation:</strong> <strong>Amen.</strong></p><p><em>(The closing hymn is sung as the ministers recess.)</em></p><p><strong>Minister:</strong> Go in peace to love and serve the Lord.<br><strong>Congregation:</strong> In the name of Christ. Amen.</p>"
            }
        ],
        "ta": [
            {
                "section": "ஆயத்தமாதல் மற்றும் ஆரம்ப வணக்கம் (Preparation & Invocation)",
                "type": "static",
                "content": "<p><strong>குருவானவர்:</strong> தேவ சமாதானம் உங்களோடிருப்பதாக.</p><p><strong>சபையார்:</strong> உம்மோடும் இருப்பதாக.</p><p><em>(சபையார் எழுந்து நிற்கவும்)</em></p><p><strong>குரு:</strong> இது கர்த்தர் உண்டாக்கின நாள்;<br><strong>சபையார்:</strong> இதில் நாம் மகிழ்ந்து சந்தோஷப்படுவோம்.</p><p><strong>குரு:</strong> ஜெபிப்போமாக.<br>எல்லாம் வல்ல இறைவா, எல்லா இருதயங்களும் உமக்குத் திறந்திருக்கின்றன; எல்லா ஆசைகளும் உமக்குத் தெரிந்திருக்கின்றன; எவ்வித இரகசியமும் உமக்கு மறைவாயிராது. நாங்கள் உம்மை முழுமையாக அன்புகூரவும் உமது திருநாமத்தை மகிமைப்படுத்தவும், பரிசுத்த ஆவியின் ஏவுதலால் எங்கள் இருதயத்தின் சிந்தனைகளைத் தூய்மைப்படுத்தியருளும்; எங்கள் நாதர் இயேசு கிறிஸ்துவினால் வேண்டி நிற்கிறோம். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "துதிப் பாடல் (Hymn of Praise)",
                "type": "static",
                "content": "<p><em>(கர்த்தருடைய மகத்துவத்தை மையமாகக் கொண்ட ஸ்தோத்திரப் பாடல் பாடவும்.)</em></p>"
            },
            {
                "section": "பாவ அறிக்கை (Confession of Sin)",
                "type": "static",
                "content": "<p><em>(சபையார் முழந்தாளிட்டு அல்லது அமர்ந்து)</em></p><p><strong>குரு:</strong> தேவன் ஒளியாயிருக்கிறார்; அவரிடத்தில் இருளே இல்லை. நாம் பாவங்களை அறிக்கையிட்டால், அவர் நம்முடைய பாவங்களை மன்னிக்கவும் எல்லா அநியாயங்களையும் நீக்கி நம்மைச் சுத்திகரிக்கவும் உண்மையும் நீதியுமுள்ளவராயிருக்கிறார்.<br>நம்முடைய பாவங்களை தேவனிடம் அறிக்கையிடுவோம்.</p><p><strong>சபையார்:</strong> சர்வ வல்லமையும் மிகுந்த இரக்கமுமுள்ள பிதாவே, தப்பிப்போன ஆடுகளைப் போல உமது வழிகளைவிட்டு வழுவி அலைந்து போனோம். எங்கள் இருதயத்தின் யோசனைகளுக்கும் விருப்பங்களுக்கும் மிகவுஞ் சாய்ந்து நடந்தோம். உமது பரிசுத்த கற்பனைகளுக்கு விரோதமாகக் குற்றம் செய்தோம். நாங்கள் செய்யவேண்டியவைகளைச் செய்யாமலும், செய்யத்தகாதவைகளைச் செய்தும் வந்தோம். ஆனாலும் ஆண்டவரே, எங்கள் நாதர் இயேசு கிறிஸ்துவினால் உமது வாக்குத்தத்தங்களின்படியே குற்றவாளிகளாகிய எங்களுக்கு இரங்குவீராக. <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "பாவ மன்னிப்பு (Absolution)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> சர்வ வல்லமையுள்ள கடவுள், அன்பின் பிதாவானவர், பாவிகள் சாவுற விரும்பாமல் அவர்கள் தங்கள் பாவங்களை விட்டுத் திரும்பிப் பிழைக்கவே விரும்புகிறார். அவர் தமது மக்களுக்குப் பாவமன்னிப்பை அறிவிக்கவும் கூறவும் தம்முடைய ஊழியக்காரருக்கு அதிகாரம் கொடுத்திருக்கிறார். ஆகவே உண்மையாகவே மனந்திரும்பி அவரது பரிசுத்த சுவிசேஷத்தை விசுவாசிக்கிற யாவருக்கும் அவர் பாவமன்னிப்பளிக்கிறார்.</p><p>ஆதலால் உமது அன்பின் மூலம் எங்களை மன்னித்து, உமது ஆவியானவரை எங்களுக்குத் தந்தருள வேண்டுமென்று ஜெபிப்போமாக; எங்கள் நாதர் இயேசு கிறிஸ்துவினால் வேண்டி நிற்கிறோம். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "அப்போஸ்தலர் விசுவாசப் பிரமாணம் (Apostles' Creed)",
                "type": "static",
                "content": "<p><em>(சபையார் எழுந்து நின்று அறிக்கையிடுவது)</em></p><p><strong>எல்லோரும்:</strong><br>வானத்தையும் பூமியையும் படைத்த சர்வ வல்லமையுள்ள பிதாவாகிய தேவனை விசுவாசிக்கிறேன்.<br>அவருடைய ஒரே குமாரனாகிய நம்முடைய நாதர் இயேசு கிறிஸ்துவையும் விசுவாசிக்கிறேன்.<br>அவர் பரிசுத்த ஆவியினாலே கன்னிமரியாளிடத்தில் உற்பவித்து பிறந்தார்.<br>பொந்தியு பிலாத்துவின்கீழ் பாடுபட்டு, சிலுவையில் அறையுண்டு, மரித்து அடக்கம்பண்ணப்பட்டார்.<br>பாதாளத்தில் இறங்கினார்; மூன்றாம் நாள் மரித்தோரிடத்திலிருந்து எழுந்தருளினார்.<br>பரமண்டலத்துக்கு ஏறி, சர்வ வல்லமையுள்ள பிதாவாகிய தேவனுடைய வலதுபாரிசத்தில் வீற்றிருக்கிறார்.<br>அவ்விடத்திலிருந்து உயிருள்ளோரையும் மரித்தோரையும் நியாயந்தீர்க்க வருவார்.<br>பரிசுத்த ஆவியையும் விசுவாசிக்கிறேன்.<br>பொதுவாயிருக்கிற பரிசுத்த சபையும், பரிசுத்தவான்களுடைய ஐக்கியமும்,<br>பாவ மன்னிப்பும், சரீர உயிர்த்தெழுதலும், நித்திய ஜீவனும் உண்டென்று விசுவாசிக்கிறேன். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "பழைய ஏற்பாடு வாசிப்பு (Old Testament Lesson)",
                "type": "scripture",
                "reference": "ஏசாயா 40:1"
            },
            {
                "section": "சங்கீதம் (Responsive Psalm)",
                "type": "scripture",
                "reference": "சங்கீதம் 23:1"
            },
            {
                "section": "நிருபம் (Epistle Lesson)",
                "type": "scripture",
                "reference": "ரோமர் 12:1"
            },
            {
                "section": "சுவிசேஷ வாசிப்பு (Gospel Reading)",
                "type": "scripture",
                "reference": "யோவான் 3:16",
                "intro": "<p><em>(சபையார் எழுந்து நிற்கவும்)</em></p><p><strong>குரு:</strong> பரிசுத்த சுவிசேஷம் வாசிக்கப்படும்.<br><strong>சபையார்:</strong> கிறிஸ்துவே உமக்கு மகிமை உண்டாவதாக.</p>",
                "outro": "<p><strong>குரு:</strong> இது ஆண்டவரின் சுவிசேஷம்.<br><strong>சபையார்:</strong> கிறிஸ்துவே உமக்குத் துதி உண்டாவதாக.</p>"
            },
            {
                "section": "பிரசங்கம் (Sermon)",
                "type": "static",
                "content": "<p><em>(குருவானவர் அன்றைய வேத வாசிப்புகளின் அடிப்படையில் பிரசங்கிக்கிறார்)</em></p><p><strong>பிரசங்கி:</strong> கர்த்தாவே, என் வாயின் வார்த்தைகளும் என் இருதயத்தின் தியானமும் உமது சமுகத்தில் பிரியமாயிருப்பதாக. ஆமென்.</p>"
            },
            {
                "section": "கர்த்தருடைய ஜெபம் (The Lord's Prayer)",
                "type": "static",
                "content": "<p><strong>எல்லோரும்:</strong><br>பரமண்டலங்களிலிருக்கிற எங்கள் பிதாவே,<br>உம்முடைய நாமம் பரிசுத்தப்படுவதாக;<br>உம்முடைய ராஜ்யம் வருவதாக;<br>உம்முடைய சித்தம் பரமண்டலத்திலே செய்யப்படுகிறதுபோல பூமியிலேயும் செய்யப்படுவதாக.<br>அன்றன்றுள்ள எங்கள் ஆகாரத்தை இன்று எங்களுக்குத் தாரும்.<br>எங்களுக்கு விரோதமாய்க் குற்றம் செய்கிறவர்களுக்கு நாங்கள் மன்னிக்கிறதுபோல எங்கள் குற்றங்களை எங்களுக்கு மன்னியும்.<br>எங்களைச் சோதனைக்குள் பிரவேசிக்கப்பண்ணாமல், தீமையினின்று எங்களை இரட்சித்துக்கொள்ளும்.<br>ராஜ்யமும், வல்லமையும், மகிமையும் என்றென்றைக்கும் உம்முடையவைகளே. <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "மத்தியஸ்த ஜெபம் (Intercessory Prayers)",
                "type": "static",
                "content": "<p><em>(சபையார் முழந்தாளிட்டு அல்லது அமர்ந்திருக்கவும்)</em></p><p><strong>குரு:</strong> சபைக்காகவும் உலகத்திற்காகவும் ஜெபிப்போமாக.<br>கர்த்தாவே எங்கள் ஜெபத்தைக் கேட்டருளும்.<br><strong>சபையார்:</strong> எங்கள் ஜெபத்தை ஏற்றுக்கொள்ளும்.</p><p><em>(நோயாளர்கள், ஏழைகள், மற்றும் சமூகத்திற்காக மனு செய்யலாம்)</em></p><p><strong>குரு:</strong> உமது ராஜ்யத்தின் வருகையை விரைவுப்படுத்தும்; விசுவாசத்தில் வாழும் நாங்கள் உமது குமாரனின் வருகையில் மகிழ்வோம் என்று மன்றாடுகிறோம். எங்கள் நாதர் இயேசு கிறிஸ்துவினால். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "காணிக்கை அர்ப்பணம் (Offertory)",
                "type": "static",
                "content": "<p><em>(காணிக்கை சேகரிக்கப்படும் போது சபையார் கீர்த்தனை பாடவும்)</em></p><p><strong>குரு:</strong> எல்லாம் உம்முடையவைகள் ஆண்டவரே; உமது கரத்திலிருந்து நாங்கள் பெற்றுக்கொண்டதை உமக்குச் செலுத்துகிறோம்.</p><p><em>(காணிக்கை கொண்டு வரும்போது சபையார் எழுந்து நிற்கவும்)</em></p><p><strong>எல்லோரும்:</strong> தேவனே, இந்தக் காணிக்கைகளையும் எங்களையும் உமக்கு உகந்த ஜீவபலியாக ஏற்றுக்கொள்ளும். இயேசு கிறிஸ்துவின் மூலம். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "ஆசீர்வாதம் மற்றும் நிறைவு (Benediction & Closing)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> எல்லாப் புத்திக்கும் மேலான தேவ சமாதானம் உங்கள் இருதயங்களையும் சிந்தைகளையும் கிறிஸ்து இயேசுவுக்குள் காத்துக்கொள்ளக்கடவது. பிதா, குமாரன், பரிசுத்த ஆவியானவருடைய ஆசீர்வாதம் உங்கள் அனைவரோடும் இன்றும் என்றென்றும் இருப்பதாக.</p><p><strong>சபையார்:</strong> <strong>ஆமென்.</strong></p><p><em>(நிறைவுப் பாடல் பாடிக்கொண்டே குருவானவர் செல்கிறார்)</em></p><p><strong>குரு:</strong> அன்பில் கர்த்தரை சேவிக்கச் சென்று வாருங்கள்.<br><strong>சபையார்:</strong> கிறிஸ்துவின் நாமத்தினாலே. ஆமென்.</p>"
            }
        ]
    },
    "wedding": {
        "en": [
            {
                "section": "Processional & Call to Worship",
                "type": "static",
                "content": "<p><em>(The wedding party processes in as the congregation stands and a suitable hymn is sung.)</em></p><p><strong>Minister:</strong> Peace be with you.<br><strong>Congregation:</strong> And also with you.</p><p><strong>Minister:</strong> Dearly beloved, we are gathered here in the sight of God, and in the face of this congregation, to join together this man and this woman in holy matrimony; which is an honourable estate, instituted of God in the time of man's innocency, signifying unto us the mystical union that is betwixt Christ and his Church.</p>"
            },
            {
                "section": "Opening Prayer",
                "type": "static",
                "content": "<p><strong>Minister:</strong> Let us pray.</p><p><strong>All:</strong> Eternal God, creator and preserver of all life, author of salvation, and giver of all grace: Look with favour upon the world you have made, and for which your Son gave his life. Look with favour upon this man and this woman, and grant that they, entering into the covenant of marriage, will know you as the author and finisher of their love; through Jesus Christ our Lord. <strong>Amen.</strong></p>"
            },
            {
                "section": "Declaration of Purpose",
                "type": "static",
                "content": "<p><strong>Minister:</strong> I require and charge you both, here in the presence of God, that if either of you know any reason why you may not be united in marriage, you do now confess it. For be well assured that if any persons are joined together contrary to God's Word, their marriage is not lawful.</p><p><em>(Pause for any response.)</em></p>"
            },
            {
                "section": "Marriage Vows",
                "type": "static",
                "content": "<p><em>(The groom faces the bride and takes her right hand.)</em></p><p><strong>Groom:</strong> I, [Name], take you, [Name], to be my wedded wife, to have and to hold from this day forward, for better, for worse; for richer, for poorer; in sickness and in health; to love and to cherish, till death do us part, according to God's holy ordinance; and thereto I pledge thee my faith.</p><p><em>(The bride faces the groom and takes his right hand.)</em></p><p><strong>Bride:</strong> I, [Name], take you, [Name], to be my wedded husband, to have and to hold from this day forward, for better, for worse; for richer, for poorer; in sickness and in health; to love and to cherish, till death do us part, according to God's holy ordinance; and thereto I pledge thee my faith.</p>"
            },
            {
                "section": "Giving & Blessing of Rings",
                "type": "static",
                "content": "<p><em>(The Minister receives the ring.)</em></p><p><strong>Minister:</strong> Bless, O Lord, these rings, that those who wear them may abide together in your peace, and continue in your favour, until their life's end; through Jesus Christ our Lord. Amen.</p><p><em>(The groom places the ring on the bride's finger.)</em></p><p><strong>Groom:</strong> With this ring I thee wed; with my body I thee honour; and with all my worldly goods I thee endow: In the Name of the Father, and of the Son, and of the Holy Spirit. Amen.</p><p><em>(The bride places the ring on the groom's finger.)</em></p><p><strong>Bride:</strong> With this ring I thee wed; with my body I thee honour; and with all my worldly goods I thee endow: In the Name of the Father, and of the Son, and of the Holy Spirit. Amen.</p>"
            },
            {
                "section": "Declaration of Marriage",
                "type": "static",
                "content": "<p><em>(The Minister joins the couple's right hands.)</em></p><p><strong>Minister:</strong> Those whom God has joined together, let no one put asunder.</p><p>Forasmuch as [Name] and [Name] have consented together in holy wedlock, and have witnessed the same before God and this company, and thereto have given and pledged their faith, I pronounce them Husband and Wife, In the Name of the Father, and of the Son, and of the Holy Spirit. <strong>Amen.</strong></p>"
            },
            {
                "section": "Scripture Reading",
                "type": "scripture",
                "reference": "1 Corinthians 13:4"
            },
            {
                "section": "Nuptial Blessing & Prayer",
                "type": "static",
                "content": "<p><strong>Minister:</strong> Let us pray for this couple.</p><p><strong>All:</strong> O God, you have so consecrated the covenant of marriage that in it is represented the spiritual unity between Christ and his Church. Send therefore your blessing upon these your servants, that they may so love, honour, and cherish each other in faithfulness and patience, in wisdom and true godliness; that their home may be a haven of blessing and peace; through Jesus Christ our Lord, who lives and reigns with you and the Holy Spirit, one God, now and for ever. <strong>Amen.</strong></p>"
            },
            {
                "section": "Benediction",
                "type": "static",
                "content": "<p><strong>Minister:</strong> God the Father, God the Son, God the Holy Spirit, bless, preserve, and keep you; the Lord mercifully with his favour look upon you, and fill you with all spiritual benediction and grace; that ye may so live together in this life, that in the world to come ye may have life everlasting. <strong>Amen.</strong></p><p><em>(The couple processes out. Congregation remains standing for the recessional hymn.)</em></p>"
            }
        ],
        "ta": [
            {
                "section": "ஆரம்பப் பாடல் மற்றும் வணக்கம் (Processional & Invocation)",
                "type": "static",
                "content": "<p><em>(மணமக்கள் ஊர்வலமாக வரும்போது சபையார் எழுந்து நின்று பாடல் பாடவும்.)</em></p><p><strong>குருவானவர்:</strong> தேவ சமாதானம் உங்களோடிருப்பதாக.<br><strong>சபையார்:</strong> உம்மோடும் இருப்பதாக.</p><p><strong>குரு:</strong> பிரியமானவர்களே, திருமணம் தேவனால் ஏற்படுத்தப்பட்ட ஒரு பரிசுத்தமான ஒழுங்கு. கிறிஸ்துவுக்கும் சபைக்கும் இடையிலுள்ள ஆவிக்குரிய ஐக்கியத்தை இது உணர்த்துகிறது. இந்த இரு உள்ளங்களையும் பரிசுத்த கட்டுப்பாட்டிலே ஒன்றுசேர்க்க, தேவனுடைய சமுகத்திலும், இந்தச் சபையார் முன்பாகவும் நாம் இங்கே கூடியுள்ளோம்.</p>"
            },
            {
                "section": "ஆரம்ப ஜெபம் (Opening Prayer)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> ஜெபிப்போமாக.</p><p><strong>எல்லோரும்:</strong> நித்திய தேவனே, சகல ஜீவனின் சிருஷ்டிகரும் பராமரிப்பவரும், இரட்சிப்பின் ஆசிரியரும், எல்லா கிருபைகளையும் தருகின்றவரும் ஆகிய நீர் இந்த மணமக்கள் மேல் தயவாய் கண்ணோக்கியருளும். அவர்கள் திருமண உடன்படிக்கையில் நுழைகையில், நீரே அவர்கள் அன்பின் ஆசிரியரும் நிறைவேற்றுபவருமாயிருப்பீர் என அறிவார்களாக; எங்கள் ஆண்டவர் இயேசு கிறிஸ்துவினால் வேண்டுகிறோம். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "நோக்கத்தின் அறிக்கை (Declaration of Purpose)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> இந்த இரு நபர்களுக்கும் திருமணத்திற்குத் தடையிருப்பதாக யாரேனும் அறிந்திருந்தால், இப்போது அதை வெளிப்படுத்தவும். இல்லாவிட்டால், என்றும் மௌனமாயிருக்கவும்.</p><p><em>(இடைவேளை)</em></p>"
            },
            {
                "section": "திருமண வாக்குறுதி (Marriage Vows)",
                "type": "static",
                "content": "<p><em>(மணமகன் மணமகளின் வலது கையை பிடிக்கிறான்)</em></p><p><strong>மணமகன்:</strong> நான் [மணமகன் பெயர்], இன்றுமுதல் நிரந்தரமாக, இன்பத்திலும் துன்பத்திலும், செல்வத்திலும் வறுமையிலும், உடல் நலத்திலும் நோயிலும், உன்னை நேசித்து, கௌரவித்து, காப்பாற்றி, உன்னோடு வாழ, உன்னை என் மனைவியாக ஏற்றுக்கொள்கிறேன். தேவனின் திருவிருப்பப்படி உயிரோடிருக்கும் வரை உனக்கு உண்மையாயிருக்க உறுதிமொழி கூறுகிறேன்.</p><p><em>(மணமகள் மணமகனின் வலது கையை பிடிக்கிறாள்)</em></p><p><strong>மணமகள்:</strong> நான் [மணமகள் பெயர்], இன்றுமுதல் நிரந்தரமாக, இன்பத்திலும் துன்பத்திலும், செல்வத்திலும் வறுமையிலும், உடல் நலத்திலும் நோயிலும், உன்னை நேசித்து, கௌரவித்து, கீழ்ப்படிந்து, உன்னோடு வாழ, உன்னை என் கணவனாக ஏற்றுக்கொள்கிறேன். தேவனின் திருவிருப்பப்படி உயிரோடிருக்கும் வரை உனக்கு உண்மையாயிருக்க உறுதிமொழி கூறுகிறேன்.</p>"
            },
            {
                "section": "மோதிரம் அணிவித்தல் (Giving of Rings)",
                "type": "static",
                "content": "<p><em>(குரு மோதிரங்களை ஆசீர்வதிக்கிறார்)</em></p><p><strong>குரு:</strong> இந்த மோதிரங்களை ஆண்டவரே ஆசீர்வதியும். இவற்றை அணிவோர் உம்முடைய சமாதானத்தில் நிலைத்திருப்பாராக; அவர்களின் வாழ்நாள் முழுவதும் உமது தயவிலே நிலைத்திருப்பாராக; எங்கள் நாதர் இயேசு கிறிஸ்துவினால். ஆமென்.</p><p><em>(மணமகன் மோதிரத்தை மணமகளின் விரலில் அணிவிக்கிறான்)</em></p><p><strong>மணமகன்:</strong> இந்த மோதிரத்தினால் உன்னை மணக்கிறேன்; என் உடலால் உன்னைக் கௌரவிக்கிறேன்; என்னிடமுள்ள எல்லாவற்றிலும் உன்னைப் பங்காளியாக்குகிறேன்: பிதா, குமாரன், பரிசுத்த ஆவியின் நாமத்தினாலே. ஆமென்.</p>"
            },
            {
                "section": "திருமண அறிவிப்பு (Declaration of Marriage)",
                "type": "static",
                "content": "<p><em>(குரு மணமக்களின் வலது கைகளை சேர்த்து பிடிக்கிறார்)</em></p><p><strong>குரு:</strong> தேவன் இணைத்ததை மனிதன் பிரிக்காதிருக்கக்கடவன்.</p><p>[மணமகன் பெயர்] அவர்களும் [மணமகள் பெயர்] அவர்களும் தேவனுக்கும் இந்தச் சபையார் முன்னிலையிலும் திருமண உடன்படிக்கையில் ஒன்றிணைந்து, தங்கள் உண்மையை வெளிப்படுத்தியிருப்பதால், பிதா, குமாரன், பரிசுத்த ஆவியின் நாமத்தினாலே இவர்கள் இருவரும் கணவனும் மனைவியுமாக இணைக்கப்பட்டிருக்கிறார்கள் என்று அறிவிக்கிறேன். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "வேத வாசிப்பு (Scripture Reading)",
                "type": "scripture",
                "reference": "1 கொரிந்தியர் 13:4"
            },
            {
                "section": "திருமண ஆசீர்வாத ஜெபம் (Nuptial Blessing)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> இந்த தம்பதியினருக்காக ஜெபிப்போமாக.</p><p><strong>எல்லோரும்:</strong> தேவனே, திருமண உடன்படிக்கையை நீர் கிறிஸ்துவிற்கும் சபைக்கும் இடையிலுள்ள ஆவிக்குரிய ஐக்கியத்தை உணர்த்துவதாக புனிதப்படுத்தினீர். எனவே இந்த உம் அடியார்கள் மேல் உமது ஆசீர்வாதத்தை அனுப்பியருளும். நம்பிக்கையிலும் பொறுமையிலும், ஞானத்திலும் உண்மையான தெய்வபக்தியிலும் ஒருவரை ஒருவர் நேசித்து, கௌரவித்து, பாதுகாத்துக்கொள்வார்களாக; அவர்களின் இல்லம் ஆசீர்வாதத்தினாலும் சமாதானத்தினாலும் நிறைந்த ஒரு புகலிடமாயிருப்பதாக; எங்கள் ஆண்டவர் இயேசு கிறிஸ்துவினால் வேண்டுகிறோம். <strong>ஆமென்.</strong></p>"
            },
            {
                "section": "ஆசீர்வாதம் (Benediction)",
                "type": "static",
                "content": "<p><strong>குரு:</strong> பிதாவாகிய தேவன், குமாரனாகிய தேவன், பரிசுத்த ஆவியாகிய தேவன் உங்களை ஆசீர்வதித்து, காத்து, பரிபாலிப்பாராக; கர்த்தர் தம்முடைய தயவான கண்களால் உங்களை நோக்கி, எல்லா ஆவிக்குரிய ஆசீர்வாதங்களாலும் நிரப்புவாராக. நீங்கள் இவ்வுலக வாழ்க்கையில் ஒன்றாக நடந்து, வரும் உலகில் நித்தியஜீவனைப் பெறுவீர்களாக. <strong>ஆமென்.</strong></p><p><em>(மணமக்கள் வௌியே செல்கின்றனர். சபையார் நிறைவுப் பாடல் பாடி நிற்கின்றனர்.)</em></p>"
            }
        ]
    }
}


@router.get("")
async def get_service(
    type: str = Query("sunday", description="Type of service: sunday, wedding"),
    lang: str = Query("en", description="Language: en or ta")
):
    type = type.lower()
    lang = lang.lower()

    if type not in CSI_CONTENT:
        type = "sunday"

    if lang == "dual":
        en_items = CSI_CONTENT[type].get("en", [])
        ta_items = CSI_CONTENT[type].get("ta", [])
        dual_data = []
        for i in range(max(len(en_items), len(ta_items))):
            en = en_items[i] if i < len(en_items) else {}
            ta = ta_items[i] if i < len(ta_items) else {}
            
            en_sec = en.get("section", "")
            ta_sec = ta.get("section", "")
            if en_sec and ta_sec:
                sec_title = f"{en_sec} / {ta_sec}"
            else:
                sec_title = en_sec or ta_sec
                
            dual_data.append({
                "section": sec_title,
                "type": en.get("type") or ta.get("type", "static"),
                "content_en": en.get("content", ""),
                "content_ta": ta.get("content", ""),
                "reference": en.get("reference") or ta.get("reference", ""),
                "intro": en.get("intro", ""),
                "outro": en.get("outro", ""),
                "is_dual": True
            })
        return {"success": True, "data": dual_data, "error": None}

    if lang not in CSI_CONTENT[type]:
        lang = "en"

    return {"success": True, "data": CSI_CONTENT[type][lang], "error": None}
