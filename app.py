from flask import Flask, render_template, request, jsonify
from google import genai
import PIL.Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Pastikan folder uploads ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inisialisasi client Gemini
client = genai.Client(
    api_key="AIzaSyBc1rGJPG98CDBbqcIJ7P7cpFFeSaU_baQ"
)

def analyze_image(image_path, prompt_type):
    try:
        image = PIL.Image.open(image_path)
        prompt = request.form.get('prompt_type')  # Menggunakan prompt_type dari permintaan HTTP
        if prompt == '1':
            prompt_text = '''"""
                Penjelasan dalam bahasa Indonesia yang formal dan profesional dalam format hanya paragraf 
                ilmiah lengkap dengan semua nama latin terkait kesuburan tanah dan apakah tanah 
                tersebut memerlukan tindakan secara detail dan lengkap. Jangan tulis ulang prompt ini
                dalam bentuk apapun dalam jawaban hasil analisa.
            """'''
        elif prompt == '2':
            prompt_text = '''"""
                Penjelasan dalam bahasa Indonesia yang formal dan profesional dalam format hanya paragraf 
                ilmiah lengkap dengan semua nama latin terkait kesuburan tanaman dan apakah 
                tanaman tersebut memerlukan tindakan secara detail dan lengkap.Jangan tulis ulang prompt ini
                dalam bentuk apapun dalam jawaban hasil analisa.
            """'''
        elif prompt == '3':
            prompt_text = '''"""
                Penjelasan dalam bahasa Indonesia yang formal dan profesional dalam format hanya paragraf 
                ilmiah lengkap dengan semua nama latin terkait hama yang ada pada tanaman dan 
                tindakan yang perlu diambil secara detail dan lengkap.Jangan tulis ulang prompt ini
                dalam bentuk apapun dalam jawaban hasil analisa.
            """'''
        elif prompt == '4':
            prompt_text = '''"""
                Penjelasan dalam bahasa Indonesia yang formal dan profesional dalam format hanya paragraf 
                ilmiah lengkap dengan semua nama latin terkait penyakit tanaman yang terdeteksi dan 
                tindakan yang perlu diambil secara detail dan lengkap.Jangan tulis ulang prompt ini
                dalam bentuk apapun dalam jawaban hasil analisa.
            """'''
        elif prompt == '5':
            prompt_text = '''"""
                Penjelasan dalam bahasa Indonesia yang formal dan profesional dalam format hanya paragraf 
                ilmiah lengkap dengan semua nama latin terkait gulma yang ada dan tindakan yang perlu 
                diambil untuk mengendalikannya secara detail dan lengkap.Jangan tulis ulang prompt ini
                dalam bentuk apapun dalam jawaban hasil analisa.
            """'''
        else:
            return "Pilihan tidak valid."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[prompt_text, image]
        )
        # Format response dalam markdown
        formatted_text = response.text
        # Memastikan format markdown untuk teks
        formatted_text = formatted_text.replace('**', '**')
        formatted_text = formatted_text.replace('*', '*')
        formatted_text = formatted_text.replace('<u>', '<u>').replace('</u>', '</u>')
        markdown_response = f"""
{formatted_text}

---
*Laboratorium Teaching and Research Farm (TRF)*, 
*Fakultas Pertanian Universitas Jambi*,
*Tahun 2024*
"""
        return markdown_response
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = analyze_image(filepath, request.form.get('prompt_type'))
        
        # Hapus file setelah dianalisis
        os.remove(filepath)
        
        return jsonify({'result': result, 'display': True})

if __name__ == '__main__':
    app.run(debug=True)
