"""
Social Battery & Recharging Engine Tool
Digunakan oleh AI Agent untuk mendiagnosis tingkat kelelahan sosial dan
menghitung waktu recharge yang dibutuhkan.
"""

def clamp_number(val, min_val: int, max_val: int) -> int:
    """Memastikan angka berada dalam batas min dan max yang valid."""
    try:
        num = int(val)
        return max(min_val, min(num, max_val))
    except (ValueError, TypeError):
        return min_val


def calculator_depresi(
    small_talk_count: int = 0,
    meetings_hours: int = 0,
    unexpected_calls: int = 0,
    crowd_hours: int = 0
) -> str:
    """
    Menghitung sisa daya baterai sosial dan waktu me-time yang diperlukan.
    
    Argumen:
        small_talk_count: Jumlah obrolan basa-basi (rentang: 0 - 30).
        meetings_hours: Durasi meeting formal dalam jam (rentang: 0 - 12).
        unexpected_calls: Jumlah telepon/video call mendadak (rentang: 0 - 10).
        crowd_hours: Jam berada di kerumunan publik (rentang: 0 - 12).
    """
    # 1. Validasi / Normalisasi Input yang aman
    small_talk = clamp_number(small_talk_count, 0, 30)
    meetings = clamp_number(meetings_hours, 0, 12)
    calls = clamp_number(unexpected_calls, 0, 10)
    crowd = clamp_number(crowd_hours, 0, 12)

    # 2. Bobot pengurasan energi sosial
    drain = (
        (small_talk * 4.5)
        + (meetings * 11.0)
        + (calls * 14.0)
        + (crowd * 6.5)
    )

    initial_battery = 100.0
    remaining_battery = max(0.0, initial_battery - drain)

    # 3. Formula recharging (menit isolasi/me-time yang dibutuhkan)
    deficit = 100.0 - remaining_battery
    recharge_minutes = int(deficit * 2.2)

    # 4. Klasifikasi status & mode
    if remaining_battery > 70:
        status = "Stabil (Siap menyapa orang lain)"
        mode = "Normal - tidak perlu tindakan darurat."
    elif remaining_battery > 40:
        status = "Menipis (Toleransi basa-basi menurun drastis)"
        mode = "Hemat Daya - aktifkan headphone tanpa lagu sebagai sinyal visual 'jangan ganggu'."
    elif remaining_battery > 15:
        status = "Kritis (Zona bahaya 'cemberut tanpa sadar')"
        mode = "Mode Hening - tolak ajakan nongkrong tambahan, cari sudut ruangan yang sunyi."
    else:
        status = "Drop / Blackout Sosial"
        mode = "Karantina Mandiri Total - tutup pintu kamar, matikan notifikasi, jauhi interaksi verbal."

    hours = recharge_minutes // 60
    minutes = recharge_minutes % 60

    result = (
        "-------------------------------------------------------\n"
        "[HASIL DIAGNOSIS SOCIAL BATTERY]\n"
        "-------------------------------------------------------\n"
        f"Sisa Daya Baterai     : {remaining_battery:.1f}%\n"
        f"Kondisi Saat Ini      : {status}\n"
        f"Protokol Direkomendasi: {mode}\n"
        f"Waktu Recharging Wajib: {hours} jam {minutes} menit waktu sunyi/solo\n"
        "-------------------------------------------------------"
    )
    return result


if __name__ == "__main__":
    # Test eksekusi
    output = calculator_depresi(small_talk_count=10, meetings_hours=2, unexpected_calls=5, crowd_hours=6)
    print(output)
