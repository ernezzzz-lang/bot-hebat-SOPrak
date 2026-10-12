from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("HEBAT_USERNAME")
PASSWORD = os.getenv("HEBAT_PASSWORD")

# Mengambil data dari environment variable (bisa dari .env lokal atau GitHub Secrets)
URL_MATKUL = os.getenv("HEBAT_URL_MATKUL")
NAMA_TUGAS = os.getenv("HEBAT_NAMA_TUGAS")
FILE_TUGAS = os.getenv("HEBAT_FILE_TUGAS")

def run_upload_bot():
    if not os.path.exists(FILE_TUGAS):
        print(f"[ERROR] File {FILE_TUGAS} gurung onok nang folder.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
     
        print("otw buka hebat...")
        page.goto("https://hebat.elearning.unair.ac.id/")
        page.get_by_role("link", name="Login").click()
        page.locator("#username").fill(USERNAME)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginbtn").click()
        page.wait_for_load_state("domcontentloaded")
       
        print(f"masuk page matkul: {URL_MATKUL}")
        page.goto(URL_MATKUL)
        page.wait_for_load_state("domcontentloaded")
        
        print(f"cari link tugas yang mengandung kata: '{NAMA_TUGAS}'...")
       
        # Menggunakan pencarian berbasis teks parsial yang lebih fleksibel
        link_tugas = page.get_by_role("link", name=Pendalaman, exact=False)
        
        maksimal_refresh_matkul = 60 # Kita buat 60 kali (total 5 menit penantian)
        tugas_ditemukan = False

        for i in range(maksimal_refresh_matkul):
            # Cek apakah link tugas sudah muncul dan bisa diklik
            if link_tugas.count() > 0 and link_tugas.first.is_visible():
                print(f"[INFO] Link tugas '{NAMA_TUGAS}' udah aktif dan ketemu!")
                link_tugas.first.click()
                page.wait_for_load_state("domcontentloaded")
                tugas_ditemukan = True
                break
            else:
                print(f"[{i+1}/{maksimal_refresh_matkul}] Link tugas blom aktif. Refresh dalam 5 detik...")
                page.wait_for_timeout(5000) # Jeda 5 detik tiap refresh agar tidak memberatkan server
                page.reload()
                page.wait_for_load_state("domcontentloaded")

        if not tugas_ditemukan:
            print("[GAGAL] timeout. tugas ga ditemukan.")
            browser.close()
            return
      
        print("cari button 'Add submission' or 'Edit submission'...")
        tombol_submission = page.locator("button:has-text('submission')")
        
        if tombol_submission.is_visible():
            print("klik button submission...")
            tombol_submission.click()
            page.wait_for_load_state("domcontentloaded")

       
            print("nunggu pop up file manager...")
            page.wait_for_selector('.filemanager', timeout=15000)
            
            print("klik ikon 'Add...'...")
            page.locator('.fp-btn-add, a[title="Add..."]').first.click()
            
            print("nunggu pop-up File picker keluar...")
      
            page.get_by_text("Upload a file").first.wait_for(state="visible", timeout=10000)
            
            print("makesure tab 'Upload a file' diklik...")
            page.get_by_text("Upload a file").first.click()
            
            print("nunggu form upload siap...")

            page.locator('input[name="repo_upload_file"]').wait_for(state="attached", timeout=10000)
            
            print("input file tugas langsung ke sistem...")
    
            page.locator('input[name="repo_upload_file"]').set_input_files(FILE_TUGAS)
            
            print("klik 'Upload this file'...")
            page.locator('button:has-text("Upload this file")').click()

            print("nunggu loading upload masuk ke filemanager (10 seconds)...")
            page.wait_for_timeout(5000)
            

            print("klik 'Save changes'...")
            page.get_by_role("button", name="Save changes").click()
            page.wait_for_load_state("domcontentloaded")

            print("[SUCCESS] tugas terkumpul!")
            page.screenshot(path="screenshots/bukti_kumpul_tugas.png", full_page=True)
        else:
            print("[FAILED] tombol add/edit submission ga ditemuka.")

        print("\n closing browser in 5 seconds...")
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    run_upload_bot()