import io
from flask import Flask, render_template, request, jsonify
from PIL import Image
import argostranslate.package as pkg
import argostranslate.translate as tr
from ocr_modul import resimden_oku

import os
KLASOR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=KLASOR)
_onbellek = {}


def cevir_paragraf(p):
    p = p.replace("\n", " ").strip()
    if p not in _onbellek:
        if len(_onbellek) > 500:
            _onbellek.clear()
        _onbellek[p] = tr.translate(p, "en", "tr")
    return _onbellek[p]


def dil_paketi_hazirla():
    kurulu = {(l.code) for l in tr.get_installed_languages()}
    if "en" in kurulu and "tr" in kurulu:
        try:
            if tr.get_translation_from_codes("en", "tr"):
                return
        except Exception:
            pass
    pkg.update_package_index()
    p = next(x for x in pkg.get_available_packages()
             if x.from_code == "en" and x.to_code == "tr")
    pkg.install_from_path(p.download())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cevir", methods=["POST"])
def cevir():
    dosya = request.files.get("resim")
    if not dosya:
        return jsonify(hata="Resim gelmedi."), 400
    ust = int(request.form.get("ust_yok", 12))
    alt = int(request.form.get("alt_yok", 6))
    img = Image.open(io.BytesIO(dosya.read()))
    metin = resimden_oku(img, ust_yok=ust, alt_yok=alt)
    if not metin:
        return jsonify(orijinal="", ceviri="", mesaj="Okunabilir metin bulunamadı.")
    ceviri = "\n\n".join(cevir_paragraf(p) for p in metin.split("\n\n"))
    return jsonify(orijinal=metin, ceviri=ceviri, mesaj="Çeviri tamamlandı (çevrimdışı).")


if __name__ == "__main__":
    dil_paketi_hazirla()
    app.run(host="127.0.0.1", port=5000, debug=False)
