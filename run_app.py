"""Entry point para rodar o dashboard Streamlit.

Uso:
    python run_app.py            # inicia app em http://localhost:8501
    python run_app.py --page 2   # inicia em página específica (1, 2 ou 3)
"""
import subprocess
import sys
from pathlib import Path


def main():
    app_dir = Path(__file__).parent / "src" / "app"
    page = sys.argv[1] if len(sys.argv) > 1 else "Home"

    if page.isdigit():
        page = f"{page}_Home" if page == "0" else {
            "1": "1_Gap_Salarial",
            "2": "2_Funil_Lideranca",
            "3": "3_Perfil_Mensal",
        }.get(page, "Home")

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_dir / f"{page}.py"),
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
    ]
    print(f"🚀 Iniciando dashboard: {page}")
    print(f"   Acesse: http://localhost:8501")
    subprocess.run(cmd)


if __name__ == "__main__":
    main()