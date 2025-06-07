import os
import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import time

from ad_generator import AdGenerator
from chatbot import process_image

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development-secret-key")

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Initialize the ad generator
ad_generator = AdGenerator()

# Translations dictionary
translations = {
    'en': {
        'title': 'VisuaLux',
        'description': 'Create stunning video ads from your images and text',
        'upload_label': 'Upload Images (Max 10)',
        'description_label': 'Ad Description',
        'description_placeholder': 'Enter your ad description here...',
        'language_label': 'Output Language',
        'generate_button': 'Generate Video Ad',
        'english': 'English',
        'french': 'French',
        'arabic': 'Arabic',
        'generating': 'Generating your video ad...',
        'result_title': 'Your Generated Video Ad',
        'download_button': 'Download Video',
        'create_new': 'Create Another Ad',
        'error_title': 'Error',
        'chat_title': 'Chat with AI Assistant',
        'chat_placeholder': 'Ask anything about ad creation...',
        'send_button': 'Send',
        'progress': 'Processing: ',
        'step1': 'Optimizing script',
        'step2': 'Generating audio',
        'step3': 'Processing images',
        'step4': 'Creating video',
        'step5': 'Finalizing',
        'footer': '© 2023 VisuaLux',
        'how_it_works': 'How It Works',
        'testimonials_title': 'What Our Clients Say',
        'faq_title': 'Frequently Asked Questions',
        'faq_q1': 'What types of ads can I create with VisuaLux?',
        'faq_a1': 'VisuaLux allows you to create a wide variety of video advertisements including product showcases, promotional campaigns, social media ads, and brand awareness videos. Simply upload your images and provide a description of what you want to achieve.',
        'faq_q2': 'How many images can I upload for a single video?',
        'faq_a2': 'You can upload up to 10 images for each video ad. The platform will arrange them optimally based on your description and create smooth transitions between them.',
        'faq_q3': 'In which languages can I create my video ads?',
        'faq_a3': 'Currently, VisuaLux supports English, French, and Arabic for both the interface and the generated audio narration. We plan to add more languages in future updates.',
        'faq_q4': 'How long does it take to generate a video ad?',
        'faq_a4': 'Most video ads are generated within 1-2 minutes depending on the complexity of your request and the number of images. The platform will show you real-time progress during generation.',
        'faq_q5': 'Can I edit my video after it\'s generated?',
        'faq_a5': 'Currently, VisuaLux offers a one-step generation process. If you want to make changes, you can create a new video with modified inputs. We\'re working on adding editing capabilities in future updates.'
    },
    'fr': {
        'title': 'VisuaLux',
        'description': 'Créez des vidéos publicitaires époustouflantes à partir de vos images et textes',
        'upload_label': 'Télécharger des Images (Max 10)',
        'description_label': 'Description de la Publicité',
        'description_placeholder': 'Entrez votre description publicitaire ici...',
        'language_label': 'Langue de Sortie',
        'generate_button': 'Générer la Vidéo',
        'english': 'Anglais',
        'french': 'Français',
        'arabic': 'Arabe',
        'generating': 'Génération de votre vidéo publicitaire...',
        'result_title': 'Votre Vidéo Publicitaire Générée',
        'download_button': 'Télécharger la Vidéo',
        'create_new': 'Créer une Autre Pub',
        'error_title': 'Erreur',
        'chat_title': 'Discuter avec l\'Assistant IA',
        'chat_placeholder': 'Posez des questions sur la création de pubs...',
        'send_button': 'Envoyer',
        'progress': 'Traitement: ',
        'step1': 'Optimisation du script',
        'step2': 'Génération audio',
        'step3': 'Traitement des images',
        'step4': 'Création de la vidéo',
        'step5': 'Finalisation',
        'footer': '© 2023 VisuaLux',
        'faq_title': 'Questions Fréquentes',
        'faq_q1': 'Quels types de publicités puis-je créer avec VisuaLux ?',
        'faq_a1': 'VisuaLux vous permet de créer une grande variété de publicités vidéo, notamment des présentations de produits, des campagnes promotionnelles, des publicités pour les réseaux sociaux et des vidéos de sensibilisation à la marque. Il vous suffit de télécharger vos images et de fournir une description de ce que vous souhaitez réaliser.',
        'faq_q2': 'Combien d\'images puis-je télécharger pour une seule vidéo ?',
        'faq_a2': 'Vous pouvez télécharger jusqu\'à 10 images pour chaque publicité vidéo. La plateforme les organisera de manière optimale en fonction de votre description et créera des transitions fluides entre elles.',
        'faq_q3': 'Dans quelles langues puis-je créer mes publicités vidéo ?',
        'faq_a3': 'Actuellement, VisuaLux prend en charge l\'anglais, le français et l\'arabe pour l\'interface et la narration audio générée. Nous prévoyons d\'ajouter d\'autres langues dans les futures mises à jour.',
        'faq_q4': 'Combien de temps faut-il pour générer une publicité vidéo ?',
        'faq_a4': 'La plupart des publicités vidéo sont générées en 1 à 2 minutes, selon la complexité de votre demande et le nombre d\'images. La plateforme vous montrera la progression en temps réel pendant la génération.',
        'faq_q5': 'Puis-je modifier ma vidéo après sa génération ?',
        'faq_a5': 'Actuellement, VisuaLux propose un processus de génération en une seule étape. Si vous souhaitez apporter des modifications, vous pouvez créer une nouvelle vidéo avec des entrées modifiées. Nous travaillons à l\'ajout de capacités d\'édition dans les futures mises à jour.'
    },
    'ar': {
        'title': 'فيجوالوكس',
        'description': 'أنشئ إعلانات فيديو مذهلة من صورك ونصوصك',
        'upload_label': 'تحميل الصور (الحد الأقصى 10)',
        'description_label': 'وصف الإعلان',
        'description_placeholder': 'أدخل وصف إعلانك هنا...',
        'language_label': 'لغة الإخراج',
        'generate_button': 'إنشاء فيديو إعلاني',
        'english': 'الإنجليزية',
        'french': 'الفرنسية',
        'arabic': 'العربية',
        'generating': 'جاري إنشاء الفيديو الإعلاني الخاص بك...',
        'result_title': 'الفيديو الإعلاني الذي تم إنشاؤه',
        'download_button': 'تنزيل الفيديو',
        'create_new': 'إنشاء إعلان آخر',
        'error_title': 'خطأ',
        'chat_title': 'الدردشة مع مساعد الذكاء الاصطناعي',
        'chat_placeholder': 'اسأل أي شيء عن إنشاء الإعلانات...',
        'send_button': 'إرسال',
        'progress': 'المعالجة: ',
        'step1': 'تحسين النص',
        'step2': 'إنشاء الصوت',
        'step3': 'معالجة الصور',
        'step4': 'إنشاء الفيديو',
        'step5': 'الانتهاء',
        'footer': '© 2023 فيجوالوكس',
        'faq_title': 'الأسئلة الشائعة',
        'faq_q1': 'ما هي أنواع الإعلانات التي يمكنني إنشاؤها باستخدام فيجوالوكس؟',
        'faq_a1': 'يتيح لك فيجوالوكس إنشاء مجموعة متنوعة من إعلانات الفيديو بما في ذلك عروض المنتجات، والحملات الترويجية، وإعلانات وسائل التواصل الاجتماعي، وفيديوهات التوعية بالعلامة التجارية. ما عليك سوى تحميل صورك وتقديم وصف لما تريد تحقيقه.',
        'faq_q2': 'كم عدد الصور التي يمكنني تحميلها لفيديو واحد؟',
        'faq_a2': 'يمكنك تحميل ما يصل إلى 10 صور لكل إعلان فيديو. ستقوم المنصة بترتيبها بشكل مثالي بناءً على وصفك وإنشاء انتقالات سلسة بينها.',
        'faq_q3': 'بأي لغات يمكنني إنشاء إعلانات الفيديو الخاصة بي؟',
        'faq_a3': 'حاليًا، يدعم فيجوالوكس اللغة الإنجليزية والفرنسية والعربية لكل من الواجهة والتعليق الصوتي الذي يتم إنشاؤه. نخطط لإضافة المزيد من اللغات في التحديثات المستقبلية.',
        'faq_q4': 'كم من الوقت يستغرق إنشاء إعلان فيديو؟',
        'faq_a4': 'يتم إنشاء معظم إعلانات الفيديو في غضون 1-2 دقيقة اعتمادًا على تعقيد طلبك وعدد الصور. ستعرض لك المنصة التقدم في الوقت الفعلي أثناء الإنشاء.',
        'faq_q5': 'هل يمكنني تعديل الفيديو بعد إنشائه؟',
        'faq_a5': 'حاليًا، يقدم فيجوالوكس عملية إنشاء من خطوة واحدة. إذا كنت ترغب في إجراء تغييرات، يمكنك إنشاء فيديو جديد بمدخلات معدلة. نحن نعمل على إضافة قدرات التحرير في التحديثات المستقبلية.'
    }
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_language():
    return session.get('language', 'en')

def get_translation(key):
    lang = get_language()
    return translations[lang].get(key, translations['en'].get(key, key))

@app.context_processor
def inject_translations():
    return dict(t=get_translation, current_lang=get_language())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in translations:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'images' not in request.files:
        flash('No image part')
        return redirect(url_for('index'))
    
    files = request.files.getlist('images')
    description = request.form.get('description', '')
    language = request.form.get('language', 'en')
    
    # Validate inputs
    if not description:
        flash('Description is required')
        return redirect(url_for('index'))
    
    if not files or files[0].filename == '':
        flash('At least one image is required')
        return redirect(url_for('index'))
    
    # Create a unique session ID for this generation
    session_id = str(uuid.uuid4())
    session['current_session'] = session_id
    session['description'] = description
    session['language'] = language
    
    # Save uploaded images
    image_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{session_id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_paths.append(filepath)
    
    session['image_paths'] = image_paths
    
    # Redirect to generation page
    return redirect(url_for('generating'))

@app.route('/generating')
def generating():
    if 'current_session' not in session:
        return redirect(url_for('index'))
    
    return render_template('generating.html')

@app.route('/process-generation', methods=['POST'])
def process_generation():
    if 'current_session' not in session:
        return jsonify({'error': 'No active session'}), 400
    
    try:
        session_id = session['current_session']
        description = session['description']
        language = session['language']
        image_paths = session['image_paths']
        
        # Update progress
        time.sleep(1)  # Simulate initial processing
        progress_update(10, get_translation('step1'))
        
        # Process script with Gemini API
        script = ad_generator.call_gemini_api(description, language)
        progress_update(30, get_translation('step2'))
        
        # Generate audio from script
        audio_path, duration = ad_generator.text_to_speech(script, language)
        progress_update(50, get_translation('step3'))
        
        # Generate video from images
        output_video = os.path.join(app.config['RESULT_FOLDER'], f"{session_id}_video.mp4")
        title = None  # Optional title for the video
        call_to_action = None  # Optional CTA for the video
        
        # Process images and create video
        progress_update(70, get_translation('step4'))
        ad_generator.create_ad_video(image_paths, audio_path, output_video, title, call_to_action)
        progress_update(90, get_translation('step5'))
        
        # Clean up temp files (keep uploads for now)
        # os.remove(audio_path)
        
        # Save result path to session
        session['result_video'] = output_video
        
        time.sleep(1)  # Give time for progress to be seen
        progress_update(100, "Complete")
        
        return jsonify({
            'success': True,
            'redirect': url_for('result')
        })
        
    except Exception as e:
        logger.exception(f"Error during video generation: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

def progress_update(percent, status):
    """Helper function to update progress via Server-Sent Events in a real app.
    For this implementation, we'll just log it."""
    logger.info(f"Progress: {percent}% - {status}")

@app.route('/result')
def result():
    if 'result_video' not in session:
        return redirect(url_for('index'))
    
    video_path = session['result_video']
    video_url = '/' + video_path
    
    return render_template('result.html', video_url=video_url)

@app.route('/reset')
def reset():
    # Clear session data
    session.pop('current_session', None)
    session.pop('description', None)
    session.pop('image_paths', None)
    session.pop('result_video', None)
    
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        query = data.get('query')
        image_path = data.get('image_path')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if image_path:
            # Process with image
            result = process_image(image_path, query)
        else:
            # For now, just echo back for text-only queries
            # This would be replaced with actual chatbot logic
            result = {'answer': f"I received your question: {query}. Please upload an image for me to analyze it."}
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception(f"Chatbot error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-chat-image', methods=['POST'])
def upload_chat_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"chat_{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'image_path': filepath
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
