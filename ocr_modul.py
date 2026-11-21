"""OCR modülü: sadece sayfadaki normal metni okur.
Tarayıcı çubuğu, sekmeler, görev çubuğu, URL ve simge çöpü elenir."""
import re
from pathlib import Path
import pytesseract
from PIL import Image, ImageOps

_yerel = Path(__file__).parent / "Tesseract-OCR" / "tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = str(
    _yerel if _yerel.exists() else r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

URL_RE = re.compile(r"(https?://|www\.|\.com|\.org|\.net|\.app|\.io|/\?|_source=|campaignid)", re.I)


def _hazirla(img):
    g = img.convert("L")
    if sum(g.resize((64, 64)).getdata()) / 4096 < 128:  # koyu zemin -> ters çevir
        g = ImageOps.invert(g)
    return g.resize((g.width * 2, g.height * 2), Image.LANCZOS)


def _satir_temiz_mi(metin, ort_guven):
    metin = metin.strip()
    if len(metin) < 3 or ort_guven < 55:
        return False
    if URL_RE.search(metin):
        return False
    harf = sum(c.isalpha() for c in metin)
    if harf / len(metin) < 0.6:          # simge/çöp ağırlıklı satır
        return False
    kelimeler = metin.split()
    if len(kelimeler) >= 3 and sum(len(k) <= 2 for k in kelimeler) / len(kelimeler) > 0.6:
        return False                     # "Y © 23 yx ©" gibi parçalar
    return True


def resimden_oku(resim, dil="eng", ust_yok=12, alt_yok=6, min_guven=55):
    """resim: yol ya da PIL Image. ust_yok/alt_yok: yok sayılacak üst/alt yüzde
    (tarayıcı çubuğu ve görev çubuğu)."""
    if isinstance(resim, (str, Path)):
        resim = Image.open(resim)
    resim = resim.convert("RGB")
    w, h = resim.size
    kes = resim.crop((0, int(h * ust_yok / 100), w, int(h * (100 - alt_yok) / 100)))
    veri = pytesseract.image_to_data(_hazirla(kes), lang=dil, config="--psm 3",
                                     output_type=pytesseract.Output.DICT)
    satirlar = {}
    for i, kelime in enumerate(veri["text"]):
        if not kelime.strip():
            continue
        try:
            guven = float(veri["conf"][i])
        except ValueError:
            continue
        if guven < 0:
            continue
        anahtar = (veri["block_num"][i], veri["par_num"][i], veri["line_num"][i])
        satirlar.setdefault(anahtar, []).append((kelime, guven))

    cikti, onceki_blok = [], None
    for (blok, par, _), parcalar in sorted(satirlar.items()):
        metin = " ".join(k for k, _ in parcalar)
        ort = sum(g for _, g in parcalar) / len(parcalar)
        if _satir_temiz_mi(metin, max(ort, min_guven) if min_guven <= 0 else ort):
            if onceki_blok is not None and (blok, par) != onceki_blok:
                cikti.append("")
            cikti.append(metin)
            onceki_blok = (blok, par)
    # dar sütunlarda bölünen satırları paragraf içinde birleştir
    return "\n\n".join(p.strip() for p in "\n".join(cikti).split("\n\n") if p.strip())
