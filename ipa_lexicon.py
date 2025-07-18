VALID_CHARS = [
        # English
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        
        # Hindi/Devanagari
        'ँ', 'ं', 'ः', 'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ऍ', 'ऎ', 
        'ए', 'ऐ', 'ऑ', 'ऒ', 'ओ', 'औ', 'क', 'क़', 'ख', 'ख़', 'ग', 'ग़', 
        'घ', 'ङ', 'च', 'छ', 'ज', 'ज़', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ड़', 
        'ढ', 'ढ़', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'ऩ', 'प', 'फ', 
        'फ़', 'ब', 'भ', 'म', 'य', 'य़', 'र', 'ऱ', 'ल', 'ळ', 'ऴ', 'व', 
        'श', 'ष', 'स', 'ह', 'ऺ', 'ऻ', '़', 'ऽ', 'ा', 'ि', 'ी', 'ु', 
        'ू', 'ृ', 'ॄ', 'ॅ', 'ॆ', 'े', 'ै', 'ॉ', 'ॊ', 'ो', 'ौ', '्', 
        '॑', '॒', '॔', 'ॕ', 'ॖ', 'ॠ', '।', 'ॲ',
        
        # Bengali
        'ঁ', 'ং', 'ঃ', 'অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ', 'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 
        'ট', 'ঠ', 'ড', 'ড়', 'ঢ', 'ঢ়', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'য়', 'র', 'ল', 'শ', 'ষ', 'স', 
        'হ', '়', 'া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ', '্', 'ৎ', 'ৗ', 'ৰ', 'ৱ',
        
        # Punjabi
        'ਂ', 'ਅ', 'ਆ', 'ਇ', 'ਈ', 'ਉ', 'ਊ', 'ਏ', 'ਐ', 'ਓ', 'ਔ', 'ਕ', 'ਖ', 'ਖ਼', 'ਗ', 'ਗ਼', 'ਘ', 'ਚ', 'ਛ', 'ਜ', 'ਜ਼', 'ਝ', 'ਟ', 'ਠ', 
        'ਡ', 'ਢ', 'ਣ', 'ਤ', 'ਥ', 'ਦ', 'ਧ', 'ਨ', 'ਪ', 'ਫ', 'ਫ਼', 'ਬ', 'ਭ', 'ਮ', 'ਯ', 'ਰ', 'ਲ', 'ਲ਼', 'ਵ', 'ਸ', 'ਸ਼', 'ਹ', '਼', 'ਾ', 
        'ਿ', 'ੀ', 'ੁ', 'ੂ', 'ੇ', 'ੈ', 'ੋ', 'ੌ', '੍', 'ੜ', 'ੰ', 'ੱ', 'ੲ', 'ੳ',
        
        # Gujarati
        'ઁ', 'ં', 'ઃ', 'અ', 'આ', 'ઇ', 'ઈ', 'ઉ', 'ઊ', 'ઋ', 'ઍ', 'એ', 'ઐ', 'ઑ', 'ઓ', 'ઔ', 'ક', 'ખ', 'ગ', 'ઘ', 'ઙ', 'ચ', 'છ', 'જ', 
        'ઝ', 'ઞ', 'ટ', 'ઠ', 'ડ', 'ઢ', 'ણ', 'ત', 'થ', 'દ', 'ધ', 'ન', 'પ', 'ફ', 'બ', 'ભ', 'મ', 'ય', 'ર', 'લ', 'ળ', 'વ', 'શ', 'ષ', 
        'સ', 'હ', '઼', 'ા', 'િ', 'ી', 'ુ', 'ૂ', 'ૃ', 'ૄ', 'ૅ', 'ે', 'ૈ', 'ૉ', 'ો', 'ૌ', '્', 'ૐ', 'ૠ',
        
        # Odia
        'ଁ', 'ଂ', 'ଃ', 'ଅ', 'ଆ', 'ଇ', 'ଈ', 'ଉ', 'ଊ', 'ଋ', 'ଌ', 'ଏ', 'ଐ', 'ଓ', 'ଔ', 'କ', 'ଖ', 'ଗ', 'ଘ', 'ଙ', 'ଚ', 'ଛ', 'ଜ', 'ଝ', 
        'ଞ', 'ଟ', 'ଠ', 'ଡ', 'ଡ଼', 'ଢ', 'ଢ଼', 'ଣ', 'ତ', 'ଥ', 'ଦ', 'ଧ', 'ନ', 'ପ', 'ଫ', 'ବ', 'ଭ', 'ମ', 'ଯ', 'ର', 'ଲ', 'ଳ', 'ଵ', 'ଶ', 
        'ଷ', 'ସ', 'ହ', '଼', 'ା', 'ି', 'ୀ', 'ୁ', 'ୂ', 'ୃ', 'େ', 'ୈ', 'ୋ', 'ୌ', '୍', 'ୖ', 'ୗ', 'ୟ', 'ୱ',
        
        # Tamil
        'ஃ', 'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ', 'க', 'ங', 'ச', 'ஜ', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ன', 'ப', 
        'ம', 'ய', 'ர', 'ற', 'ல', 'ள', 'ழ', 'வ', 'ஷ', 'ஸ', 'ஹ', 'ா', 'ி', 'ீ', 'ு', 'ூ', 'ெ', 'ே', 'ை', 'ொ', 'ோ', 'ௌ', '்', 'ௗ',
        
        # Telugu
        'ఁ', 'ం', 'ః', 'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ', 'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 
        'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ', 'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ఱ', 'ల', 'ళ', 'వ', 'శ', 
        'ష', 'స', 'హ', 'ా', 'ి', 'ీ', 'ు', 'ూ', 'ృ', 'ౄ', 'ె', 'ే', 'ై', 'ొ', 'ో', 'ౌ', '్', 'ౕ', 'ౖ', 'ౙ',
        
        # Kannada
        'ಂ', 'ಃ', 'ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 
        'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಱ', 'ಲ', 'ಳ', 'ವ', 'ಶ', 'ಷ', 
        'ಸ', 'ಹ', '಼', 'ಽ', 'ಾ', 'ಿ', 'ೀ', 'ು', 'ೂ', 'ೃ', 'ೆ', 'ೇ', 'ೈ', 'ೊ', 'ೋ', 'ೌ', '್', 'ೕ', 'ೖ', 'ೞ', 'ೠ',
        
        # Malayalam
        'ം', 'ഃ', 'അ', 'ആ', 'ഇ', 'ഈ', 'ഉ', 'ഊ', 'ഋ', 'എ', 'ഏ', 'ഐ', 'ഒ', 'ഓ', 'ഔ', 'ക', 'ഖ', 'ഗ', 'ഘ', 'ങ', 'ച', 'ഛ', 'ജ', 'ഝ', 
        'ഞ', 'ട', 'ഠ', 'ഡ', 'ഢ', 'ണ', 'ത', 'ഥ', 'ദ', 'ധ', 'ന', 'പ', 'ഫ', 'ബ', 'ഭ', 'മ', 'യ', 'ര', 'റ', 'ല', 'ള', 'ഴ', 'വ', 'ശ', 
        'ഷ', 'സ', 'ഹ', 'ാ', 'ി', 'ീ', 'ു', 'ൂ', 'ൃ', 'െ', 'േ', 'ൈ', 'ൊ', 'ോ', 'ൌ', '്', 'ൎ', 'ൗ', 'ൟ', 'ൺ', 'ൻ', 'ർ', 'ൽ', 'ൾ', 'ൿ',
    ]

PUNCTUATIONS=['!', ',', '.', '।', '?', "'",' ','/']

VALID_NUMBERS = [
    # English
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',

    # Hindi / Marathi
    '०', '१', '२', '३', '४', '५', '६', '७', '८', '९',

    # Bengali
    '০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯',

    # Kannada
    '೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯',

    # Tamil
    '௦', '௧', '௨', '௩', '௪', '௫', '௬', '௭', '௮', '௯',

    # Telugu
    '౦', '౧', '౨', '౩', '౪', '౫', '౬', '౭', '౮', '౯',

    # Malayalam
    '൦', '൧', '൨', '൩', '൪', '൫', '൬', '൭', '൮', '൯',

    # Gujarati
    '૦', '૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯',

    # Punjabi
    '੦', '੧', '੨', '੩', '੪', '੫', '੬', '੭', '੮', '੯',

    # Odia
    '୦', '୧', '୨', '୩', '୪', '୫', '୬', '୭', '୮', '୯',
]


