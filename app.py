import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Tire definitions
TIRE_TYPES = {
    "Soft": {"base_lap_time": 90, "tire_wear_rate": 0.35},
    "Medium": {"base_lap_time": 91, "tire_wear_rate": 0.25},
    "Hard": {"base_lap_time": 92, "tire_wear_rate": 0.15}
}

def calculate_lap_time(base_lap, lap_num, wear_rate, fuel_effect=0.1):
    return base_lap + (lap_num * wear_rate) - ((50 - lap_num) * fuel_effect)

def simulate_stint(laps, tire_type, fuel_effect=0.1):
    base_lap = TIRE_TYPES[tire_type]["base_lap_time"]
    wear_rate = TIRE_TYPES[tire_type]["tire_wear_rate"]
    return [calculate_lap_time(base_lap, lap, wear_rate, fuel_effect) for lap in range(1, laps + 1)]

def simulate_strategy(stints, pit_time=25):
    total_time = 0
    lap_times = []
    pit_laps = []
    lap_counter = 1
    for i, stint in enumerate(stints):
        laps = stint["laps"]
        tire_type = stint["tire"]
        stint_times = simulate_stint(laps, tire_type)
        lap_times.extend(stint_times)
        total_time += sum(stint_times)
        lap_counter += laps
        if i < len(stints) - 1:
            total_time += pit_time
            pit_laps.append(lap_counter)
    return total_time, lap_times, pit_laps

def generate_comparison_pdf(time1, laps1, stints1, pits1, time2, laps2, stints2, pits2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Race Strategy Comparison - Insights", ln=True, align="C")
    pdf.ln(10)

    # Strategy A
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Strategy A Summary:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Total Time: {time1:.2f} seconds", ln=True)
    for i, stint in enumerate(stints1):
        avg = sum(laps1[sum(s["laps"] for s in stints1[:i]):sum(s["laps"] for s in stints1[:i+1])]) / stint["laps"]
        pdf.cell(0, 10, f"Stint {i+1} ({stint['tire']}) Avg Lap: {avg:.2f}s", ln=True)
    pdf.cell(0, 10, f"Pit Stops After: {', '.join(map(str, pits1)) if pits1 else 'None'}", ln=True)
    pdf.ln(5)

    # Strategy B
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Strategy B Summary:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Total Time: {time2:.2f} seconds", ln=True)
    for i, stint in enumerate(stints2):
        avg = sum(laps2[sum(s["laps"] for s in stints2[:i]):sum(s["laps"] for s in stints2[:i+1])]) / stint["laps"]
        pdf.cell(0, 10, f"Stint {i+1} ({stint['tire']}) Avg Lap: {avg:.2f}s", ln=True)
    pdf.cell(0, 10, f"Pit Stops After: {', '.join(map(str, pits2)) if pits2 else 'None'}", ln=True)
    pdf.ln(10)

    # Decision
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Conclusion:", ln=True)
    pdf.set_font("Arial", "", 11)
    if time1 < time2:
        decision = f"Strategy A was better with a lower total race time ({time1:.2f}s vs {time2:.2f}s)."
    elif time2 < time1:
        decision = f"Strategy B was better with a lower total race time ({time2:.2f}s vs {time1:.2f}s)."
    else:
        decision = "Both strategies performed equally well in terms of total race time."

    pdf.multi_cell(0, 10, decision)
    pdf.multi_cell(0, 10, "The result is based on total race time, influenced by tire degradation, compound type, and pit stop loss.")

    # Return PDF as byte stream
    pdf_output = pdf.output(dest="S").encode("latin1")
    pdf_bytes = io.BytesIO()
    pdf_bytes.write(pdf_output)
    pdf_bytes.seek(0)
    return pdf_bytes

# Streamlit UI
st.title("🏎️ Race Strategy Simulator – Compare Two Strategies")

# Strategy A Input
st.header("🔵 Strategy A")
num_stints_a = st.slider("Number of Stints (A)", 1, 3, 2, key="a_stints")
stints_a = []
for i in range(num_stints_a):
    st.subheader(f"Stint {i+1} - Strategy A")
    laps = st.number_input(f"Laps in Stint {i+1} (A)", 1, 50, 20, key=f"a_laps_{i}")
    tire = st.selectbox(f"Tire Type for Stint {i+1} (A)", list(TIRE_TYPES.keys()), key=f"a_tire_{i}")
    stints_a.append({"laps": laps, "tire": tire})

# Strategy B Input
st.header("🔴 Strategy B")
num_stints_b = st.slider("Number of Stints (B)", 1, 3, 2, key="b_stints")
stints_b = []
for i in range(num_stints_b):
    st.subheader(f"Stint {i+1} - Strategy B")
    laps = st.number_input(f"Laps in Stint {i+1} (B)", 1, 50, 20, key=f"b_laps_{i}")
    tire = st.selectbox(f"Tire Type for Stint {i+1} (B)", list(TIRE_TYPES.keys()), key=f"b_tire_{i}")
    stints_b.append({"laps": laps, "tire": tire})

# Simulate both strategies
if st.button("Simulate & Compare"):
    time1, laps1, pits1 = simulate_strategy(stints_a)
    time2, laps2, pits2 = simulate_strategy(stints_b)

    st.success(f"Strategy A Time: {time1:.2f} seconds")
    st.success(f"Strategy B Time: {time2:.2f} seconds")

    # Plot
    fig, ax = plt.subplots()
    ax.plot(range(1, len(laps1) + 1), laps1, label="Strategy A", color='blue', marker='o')
    ax.plot(range(1, len(laps2) + 1), laps2, label="Strategy B", color='red', marker='x')
    for pit in pits1:
        ax.axvline(x=pit, color='blue', linestyle='--', alpha=0.5)
    for pit in pits2:
        ax.axvline(x=pit, color='red', linestyle='--', alpha=0.5)
    ax.set_title("Lap Time Evolution – Strategy A vs B")
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap Time (s)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # Generate and offer PDF download
    pdf = generate_comparison_pdf(time1, laps1, stints_a, pits1, time2, laps2, stints_b, pits2)
    st.download_button("📄 Download Comparison Report (PDF)", data=pdf, file_name="strategy_comparison.pdf", mime="application/pdf")
