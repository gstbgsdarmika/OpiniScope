import os
import csv
import pickle
import numpy as np
import pandas as pd
from database import db
from config import Config
from models.userModel import User
from sklearn.metrics import accuracy_score
from service.userService import UserService
from sklearn.metrics import confusion_matrix
from models.machine.preprocessing.preprocessing import TextPreprocessor
from flask import Flask, request, jsonify, render_template, flash, send_file, redirect, session, url_for, send_from_directory
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__, static_url_path='/static')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + Config.DB_USER + ':' + Config.DB_PASS + '@' + Config.DB_HOST + ':' + Config.DB_PORT + '/' + Config.DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Inisialisasi database
db = db.init_app(app)

# Inisialisasi login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = UserService.login(email, password)
        if user is None:
            error = 'Email atau password salah'
            return render_template('login.html', error=error)
        else:
            login_user(user)
            return redirect(url_for('index', message='Login berhasil'))
    return render_template('login.html')

# Route untuk halaman registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']
        
        if password != password_confirm:
            return render_template('register.html', error='Konfirmasi password tidak sesuai')
        
        # Instansiasi UserService
        user_service = UserService()

        # Periksa apakah email sudah terdaftar
        user = user_service.getUser(email)
        if user is not None:
            return render_template('register.html', error='Email sudah terdaftar')

        # Buat pengguna baru
        user_service.createUser(name, password, email)
        return redirect(url_for('login', message='Pendaftaran berhasil, silakan masuk'))

    return render_template('register.html')

# Route untuk logout
@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('login'))

# Route untuk halaman index / beranda
@app.route("/")
@login_required
def index():
    active_page = 'index'
    return render_template("index.html", active_page=active_page)

# Route untuk halaman analisis
@app.route("/analisis")
def analysis():
    active_page = 'analysis'
    return render_template("analysis.html", active_page=active_page)

# Route untuk halaman analisis file
@app.route("/analisis-file", methods=['GET', 'POST'])
def analysisInputFile():
    active_page = 'analysis'
    page = request.args.get('page', 1, type=int) 
    
    if request.method == 'POST':
        if 'file-input' not in request.files:
            return render_template('analysisInputFile.html', active_page=active_page, error='File tidak ditemukan')
        
        file = request.files['file-input']
        if file.filename == '':
            return render_template('analysisInputFile.html', active_page=active_page, error='File tidak ditemukan')
        
        try:
            # Memanggil model yang digunakan
            def load_model(file_path):
                with open(file_path, 'rb') as f:
                    model = pickle.load(f)
                return model
            
            tfidf_vectorizer = load_model('models/machine/tfidf_vectorizer.pkl')
            feature_selector = load_model('models/machine/feature_selector.pkl')
            svm_classifier = load_model('models/machine/svm_classifier.pkl')
            
            # Baca file CSV menggunakan Pandas
            filename = file
            df = pd.read_csv(filename, encoding='latin-1')

            # Periksa keberadaan kolom 'tweet' dan 'label'
            if 'tweet' not in df.columns or 'label' not in df.columns:
                return render_template('analysisInputFile.html', active_page=active_page, error='Kolom tweet atau label tidak ditemukan dalam file CSV')

            # Mengambil hanya kolom 'label' dan 'tweet'
            df = df[['label', 'tweet']]

            # Mengubah nilai label positif menjadi 1 dan nilai negatif menjadi 0
            df['label'] = df['label'].replace({'positif': 1, 'negatif': 0})

            # Proses preprocessing data
            preprocessor = TextPreprocessor()
            df['tweet_clean'] = df['tweet'].apply(preprocessor.preprocess_text)

            # Ubah tweet menjadi vektor fitur TF-IDF
            tfidf_features = tfidf_vectorizer.transform(df['tweet_clean'])

            # Lakukan pemilihan fitur
            selected_features = feature_selector.transform(tfidf_features)

            # Buat prediksi menggunakan model SVM
            predictions = svm_classifier.predict(selected_features)

            # Tambahkan prediksi ke DataFrame
            df['prediction'] = predictions

            # Hitung akurasi
            accuracy = accuracy_score(df['label'], predictions)
            accuracy_display = round(accuracy * 100)

            # Hitung confusion matrix
            conf_matrix = confusion_matrix(df['label'], predictions)

            # Hitung persentase prediksi yang benar dan salah
            total_predictions = np.sum(conf_matrix)
            correct_predictions = np.trace(conf_matrix)
            incorrect_predictions = total_predictions - correct_predictions

            # Hitung persentase prediksi yang benar dan salah
            percentage_correct = (correct_predictions / total_predictions) * 100
            percentage_incorrect = (incorrect_predictions / total_predictions) * 100

            # Menghitung jumlah data yang dilabelkan positif dan negatif
            positive_data = sum(predictions == 1)
            negative_data = sum(predictions == 0)

            # Menghitung persentase data positif dan negatif dari hasil prediksi
            total_data = len(df)
            positive_percentage = (positive_data / total_data) * 100
            negative_percentage = (negative_data / total_data) * 100

            # Logika untuk paginasi
            per_page = 10 
            pages = total_data // per_page + (1 if total_data % per_page > 0 else 0) 

            # Batasi data yang ditampilkan berdasarkan nomor halaman
            start_index = (page - 1) * per_page
            end_index = min(start_index + per_page, total_data)
            sliced_df = df.iloc[start_index:end_index]
            
            # Path untuk menyimpan file CSV sementara
            temporary_csv_path = 'database/analysis-results/hasil analisis.csv'
            
            # Membuat file CSV
            csv_columns = ['Komentar', 'Klasifikasi Manual', 'Klasifikasi Sistem']
            with open(temporary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for index, row in df.iterrows():
                    writer.writerow({'Komentar': row['tweet_clean'], 
                            'Klasifikasi Manual': 'positif' if row['label'] == 1 else 'negatif',
                            'Klasifikasi Sistem': 'positif' if row['prediction'] == 1 else 'negatif'})
        
            return render_template('resultInputFile.html', active_page=active_page, 
                    df=df, accuracy=accuracy_display, conf_matrix=conf_matrix, 
                    positive_data=positive_data, negative_data=negative_data,
                    percentage_correct=percentage_correct, percentage_incorrect=percentage_incorrect,
                    positive_percentage=positive_percentage, negative_percentage=negative_percentage,
                    pages=pages, page=page, start_index=start_index, end_index=end_index, total_data=total_data)

        except pd.errors.EmptyDataError:
            return render_template('analysisInputFile.html',active_page=active_page, error='Data tidak ditemukan')
        except pd.errors.ParserError:
            return render_template('analysisInputFile.html', active_page=active_page, error='Data tidak ditemukan')
        except IOError as e:
            print("I/O error:", e)
            return render_template('analysisInputFile.html', active_page=active_page, error='Gagal menyimpan file CSV')
    return render_template("analysisInputFile.html", active_page=active_page)

# Route untuk halaman analisis teks
@app.route("/analisis-teks", methods=['GET', 'POST'])
def analysisInputText():
    active_page = 'analysis'
    if request.method == 'POST':
        text = request.form.get('text-input')
        
        # Periksa apakah teks tidak kosong
        if not text:
            error_message = "Tidak boleh kosong. Silakan masukkan teks!"
            return render_template("analysisInputText.html", active_page=active_page, error_message=error_message)

        # Memanggil model yang digunakan
        def load_model(file_path):
            with open(file_path, 'rb') as f:
                model = pickle.load(f)
            return model
            
        tfidf_vectorizer = load_model('models/machine/tfidf_vectorizer.pkl')
        feature_selector = load_model('models/machine/feature_selector.pkl')
        svm_classifier = load_model('models/machine/svm_classifier.pkl')

        # Proses preprocessing data
        preprocessor = TextPreprocessor()  
        clean_sentence = preprocessor.preprocess_text(text)
        
        # Ubah tweet menjadi vektor fitur TF-IDF
        new_sentence_tfidf = tfidf_vectorizer.transform([clean_sentence])
        
        # Lakukan pemilihan fitur
        new_sentence_feature_selector = feature_selector.transform(new_sentence_tfidf)
        
        # Buat prediksi menggunakan model SVM
        prediction = svm_classifier.predict(new_sentence_feature_selector)
        
        # Mengubah nilai prediksi jadi positif dan negatif
        prediction_label = "positif" if prediction == 1 else "negatif"

        return render_template("resultInputText.html", active_page=active_page, text=text, clean_sentence=clean_sentence, prediction_label=prediction_label)

    return render_template("analysisInputText.html", active_page=active_page)

# Route untuk halaman hasil analisis file
@app.route("/hasil-analisis-file")
def resultInputFile():
    active_page = 'analysis'
    return render_template("resultInputFile.html", active_page=active_page)

# Route untuk halaman hasil analisis teks
@app.route("/hasil-analisis-teks")
def resultInputText():
    active_page = 'analysis'
    return render_template("resultInputText.html", active_page=active_page)

# Route untuk mendownload file hasil analisis
@app.route('/download-csv')
def download_csv():
    filename = 'database/analysis-results/hasil analisis.csv'
    return send_file(filename, as_attachment=True)

# Route untuk halaman 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/preline.js")
def serve_preline_js():
    return send_from_directory("node_modules/preline/dist", "preline.js")

@app.route("/apexcharts.min.js")
def serve_apexcharts_js():
    return send_from_directory("node_modules/apexcharts/dist", "apexcharts.min.js")

@app.route("/lodash.min.js")
def serve_lodash_js():
    return send_from_directory("node_modules/lodash", "lodash.min.js")

@app.route("/apexcharts.min.js")
def serve_apexcharts_css():
    return send_from_directory("node_modules/apexcharts/dist", "apexcharts.css")

if __name__ == '__main__':
    app.run(debug=True)